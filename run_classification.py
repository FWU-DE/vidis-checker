import os
import argparse
import random
from src.classification.images import check_page_content
from src.classification.util import read_step_result_file
from src.classification.encryption import check_encryption
from src.classification.imprint import check_imprint
from src.classification.privacy_policy import check_privacy_policy
from src.classification.storage import (
    check_local_storage_entries,
    check_session_storage_entries,
)
from src.classification.cookie import get_cookie_check_results
from src.classification.tracking import check_for_tracking_pixels
from src.classification.terms_of_use import check_terms_of_use


def run_classification(input_name: str, output_name: str):
    """Run classification on agent results."""
    input_dir = f"agent_results/{input_name}"
    output_dir = f"classification_results/{output_name}"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    step_results = read_step_result_file(f"{input_dir}/step_result.jsonl")
    terms_of_use_path = f"{input_dir}/terms_of_use.pdf"
    imprint_path = f"{input_dir}/imprint.pdf"
    privacy_policy_path = f"{input_dir}/privacy_policy.pdf"
    image_directory_path = f"{input_dir}/images"

    # TODO: We currently only use the last step result, but we should use all step results
    last_step_result = step_results[-1]

    def process_cookies():
        results = get_cookie_check_results(last_step_result.cookies)

        # Save base model to json file
        with open(f"{output_dir}/cookie_results.json", "w") as f:
            f.write(results.model_dump_json(indent=4))

    def process_tracking_pixels():
        issues = check_for_tracking_pixels(last_step_result)

        # Save base model to json file
        with open(f"{output_dir}/tracking_issues.json", "w") as f:
            f.write(issues.model_dump_json(indent=4))

    def process_storage():
        local_storage_results = check_local_storage_entries(last_step_result)
        session_storage_results = check_session_storage_entries(last_step_result)

        # Save base model to json file
        with open(f"{output_dir}/local_storage_results.json", "w") as f:
            f.write(local_storage_results.model_dump_json(indent=4))

        with open(f"{output_dir}/session_storage_results.json", "w") as f:
            f.write(session_storage_results.model_dump_json(indent=4))

    def process_privacy_policy():
        result = check_privacy_policy(privacy_policy_path)

        # Save base model to json file
        with open(f"{output_dir}/privacy_policy_result.json", "w") as f:
            f.write(result.model_dump_json(indent=4))

    def process_imprint():
        result = check_imprint(imprint_path)

        # Save base model to json file
        with open(f"{output_dir}/imprint_result.json", "w") as f:
            f.write(result.model_dump_json(indent=4))

    def process_terms_of_use():
        result = check_terms_of_use(terms_of_use_path, processor_only=False)

        with open(f"{output_dir}/terms_of_use_result.json", "w") as f:
            f.write(result.model_dump_json(indent=4))

        result_processor_only = check_terms_of_use(
            terms_of_use_path, processor_only=True
        )

        # Save base model to json file
        with open(f"{output_dir}/terms_of_use_result_processor_only.json", "w") as f:
            f.write(result_processor_only.model_dump_json(indent=4))

    def process_encryption():
        result = check_encryption(last_step_result)

        # Save base model to json file
        with open(f"{output_dir}/encryption_result.json", "w") as f:
            f.write(result.model_dump_json(indent=4))

    def process_content():
        image_files = []
        if os.path.exists(image_directory_path):
            for file in os.listdir(image_directory_path):
                image_files.append(os.path.join(image_directory_path, file))
        
        # TODO: We should check all images in the directory (but what about time?)
        random_image = random.choice(image_files)
        result = check_page_content(random_image)

        # Save base model to json file
        with open(f"{output_dir}/image_content_result.json", "w") as f:
            f.write(result.model_dump_json(indent=4))

    print("Processing cookies")
    process_cookies()
    print("Processing tracking pixels")
    process_tracking_pixels()
    print("Processing storage")
    process_storage()
    print("Processing privacy policy")
    process_privacy_policy()
    print("Processing imprint")
    process_imprint()
    print("Processing terms of use")
    process_terms_of_use()
    print("Processing encryption")
    process_encryption()
    print("Processing content")
    process_content()


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run classification on agent results")
    parser.add_argument(
        "--input_name",
        type=str,
        required=True,
        help="Name of the input directory in the ./agent_results directory.",
    )
    parser.add_argument(
        "--output_name",
        type=str,
        required=True,
        help="Name of the output directory in the ./classification_results directory.",
    )
    args = parser.parse_args()

    run_classification(args.input_name, args.output_name)
