import argparse
import asyncio

from src.agent.agent import VidisAgent
from src.agent.tasks import get_task_prompt
from src.classification.util import generate_dirname


async def main():
    parser = argparse.ArgumentParser(
        description="Run the Vidis checker agent and save the results."
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the website to check. This will be the initial URL the agent navigates to.",
    )
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Username for the website login.",
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for the website login.",
    )
    parser.add_argument(
        "--task-type",
        type=str,
        default="legal",
        help="Type of task to run. Can be 'login', 'legal', 'student', or 'teacher'.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Name of the output directory and zip file (without extension). This will be placed in the ./agent_results directory.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=25,
        help="Maximum number of steps to run. The agent might decide to stop before this number.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the agent in headless mode.",
    )

    args = parser.parse_args()

    output_name = generate_dirname(args.url)
    vidis_agent = VidisAgent(
        task_prompt=get_task_prompt(args.task_type),
        initial_url=args.url,
        output_name=output_name,
        username=args.username,
        password=args.password,
        headless=args.headless,
    )
    await vidis_agent.run_task(max_steps=args.max_steps)


if __name__ == "__main__":
    asyncio.run(main())
