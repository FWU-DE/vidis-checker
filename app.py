from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import json
from typing import Dict, Any

from src.classification.util import generate_dirname
from src.agent.tasks import get_task_prompt
from agent import VidisAgent, AGENT_OUTPUT_DIR
from run_classification import run_classification
from generate_report import generate_report

app = FastAPI()

JOBS_FILE = "jobs.json"


class JobPayload(BaseModel):
    url: str
    max_steps: int = 25
    number_of_pages_to_visit: int = 10


def load_jobs() -> Dict[str, Any]:
    """Load jobs from JSON file"""
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_jobs(jobs: Dict[str, Any]) -> None:
    """Save jobs to JSON file"""
    try:
        with open(JOBS_FILE, "w") as f:
            json.dump(jobs, f, indent=2)
    except IOError:
        pass  # Handle error silently for now


def update_job_status(job_id: str, updates: Dict[str, Any]) -> None:
    """Update job status in persistent storage"""
    jobs = load_jobs()
    if job_id in jobs:
        jobs[job_id].update(updates)
        save_jobs(jobs)


async def run_automation_job(job_id: str, payload: JobPayload):
    update_job_status(job_id, {"status": "running"})
    try:
        output_name = job_id  # job_id is already the output_name

        # Step 1: Run the agent
        vidis_agent = VidisAgent(
            task_prompt=get_task_prompt(payload.number_of_pages_to_visit),
            initial_url=payload.url,
            output_name=output_name,
            headless=True,
        )
        await vidis_agent.run_task(max_steps=payload.max_steps)

        # Step 2: Run classification
        run_classification(output_name, output_name)

        # Step 3: Generate report
        generate_report(output_name, output_name)

        # Get the zip file path and report path
        zip_path = os.path.join(AGENT_OUTPUT_DIR, f"{output_name}.zip")
        report_path = f"reports/{output_name}/report.pdf"

        update_job_status(
            job_id,
            {
                "status": "finished",
                "result": {
                    "message": "Automation completed successfully",
                    "zip_file": zip_path,
                    "report_file": report_path,
                    "output_name": output_name,
                },
            },
        )
    except Exception as e:
        update_job_status(job_id, {"status": "error", "error": str(e)})


@app.post("/jobs/", status_code=202)
def start_job(payload: JobPayload, bg: BackgroundTasks):
    job_id = generate_dirname(payload.url)
    jobs = load_jobs()
    jobs[job_id] = {"status": "pending", "result": None}
    save_jobs(jobs)
    bg.add_task(run_automation_job, job_id, payload)
    return {"job_id": job_id, "status_url": f"/jobs/{job_id}"}


@app.get("/jobs/")
def get_all_jobs():
    """Get all jobs"""
    jobs = load_jobs()
    return {"jobs": jobs}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    jobs = load_jobs()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@app.get("/jobs/{job_id}/report")
def download_report(job_id: str):
    jobs = load_jobs()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    if job["status"] != "finished":
        raise HTTPException(400, "Job not finished yet")

    output_name = job_id  # job_id is the output_name
    report_path = f"reports/{output_name}/report.pdf"

    if not os.path.exists(report_path):
        raise HTTPException(404, "Report file not found")

    return FileResponse(
        path=report_path,
        filename=f"{output_name}_report.pdf",
        media_type="application/pdf",
    )


@app.get("/jobs/{job_id}/zip")
def download_zip(job_id: str):
    jobs = load_jobs()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    if job["status"] != "finished":
        raise HTTPException(400, "Job not finished yet")

    output_name = job_id  # job_id is the output_name
    zip_path = os.path.join(AGENT_OUTPUT_DIR, f"{output_name}.zip")

    if not os.path.exists(zip_path):
        raise HTTPException(404, "Zip file not found")

    return FileResponse(
        path=zip_path,
        filename=f"{output_name}_results.zip",
        media_type="application/zip",
    )


@app.get("/")
def root():
    return {
        "message": "Web Automation API",
        "endpoints": {
            "/jobs/": "POST - Start automation job, GET - Get all jobs",
            "/jobs/{job_id}": "GET - Get job status",
            "/jobs/{job_id}/report": "GET - Download PDF report",
            "/jobs/{job_id}/zip": "GET - Download classification results zip",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
