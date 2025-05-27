import argparse
import asyncio

from agent import VidisAgent
from src.agent.tasks import get_task_prompt
from src.classification.util import generate_dirname


async def main():
    parser = argparse.ArgumentParser(description="Crawl the web and save the data")
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="URL of the website to crawl. This will be the initial URL of the agent.",
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
        "--number-of-pages-to-visit",
        type=int,
        default=10,
        help="Number of pages the agent should browse.",
    )
    args = parser.parse_args()

    output_name = generate_dirname(args.url)
    vidis_agent = VidisAgent(
        task_prompt=get_task_prompt(args.number_of_pages_to_visit),
        initial_url=args.url,
        output_name=output_name,
    )
    await vidis_agent.run_task(max_steps=args.max_steps)


if __name__ == "__main__":
    asyncio.run(main())
