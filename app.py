from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
import requests

from src.classification.util import generate_dirname
from src.agent.tasks import get_task_prompt
from src.agent.agent import VidisAgent, AGENT_OUTPUT_DIR
from run_classification import run_classification
from generate_report import generate_report


load_dotenv()

app = FastAPI()
security = HTTPBearer()

JOBS_FILE = "jobs.json"
API_KEY = os.getenv("API_KEY")


class JobPayload(BaseModel):
    url: str
    username: str
    password: str
    task_type: str = "legal"
    max_steps: int = 25


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Authorization header"""
    if not API_KEY:
        raise HTTPException(500, "API key not configured")

    if credentials.credentials != API_KEY:
        raise HTTPException(401, "Invalid API key")

    return credentials.credentials


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
            task_prompt=get_task_prompt(payload.task_type),
            initial_url=payload.url,
            output_name=output_name,
            username=payload.username,
            password=payload.password,
            headless=True,
        )
        await vidis_agent.run_task(max_steps=payload.max_steps)

        # Step 2: Run classification
        run_classification(output_name, output_name)

        # Step 3: Generate report
        generate_report(payload.url, output_name, output_name)

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


@app.post("/test")
def test_endpoint():
    """Test endpoint that makes a request to Azure OpenAI"""
    try:
        url = "https://fwubmi.openai.azure.com/openai/deployments/fwuBMI_gpt-4.1/chat/completions"
        params = {"api-version": "2025-01-01-preview"}

        headers = {
            "Content-Type": "application/json",
            "api-key": os.getenv("OPENAI_API_KEY"),
        }

        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me a joke about computers."},
            ]
        }

        response = requests.post(url, params=params, headers=headers, json=data)
        return response.json()
    except Exception as e:
        raise HTTPException(500, f"Test endpoint failed: {str(e)}")


@app.post("/jobs/", status_code=202)
def start_job(
    payload: JobPayload, bg: BackgroundTasks, api_key: str = Depends(verify_api_key)
):
    job_id = generate_dirname(payload.url)
    jobs = load_jobs()
    jobs[job_id] = {"status": "pending", "result": None}
    save_jobs(jobs)
    bg.add_task(run_automation_job, job_id, payload)
    return {"job_id": job_id, "status_url": f"/jobs/{job_id}"}


@app.get("/jobs/")
def get_all_jobs(api_key: str = Depends(verify_api_key)):
    """Get all jobs"""
    jobs = load_jobs()
    return {"jobs": jobs}


@app.get("/jobs/{job_id}")
def get_job(job_id: str, api_key: str = Depends(verify_api_key)):
    jobs = load_jobs()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@app.get("/jobs/{job_id}/report")
def download_report(job_id: str, api_key: str = Depends(verify_api_key)):
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
def download_zip(job_id: str, api_key: str = Depends(verify_api_key)):
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
        "authentication": "Bearer token required in Authorization header",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
