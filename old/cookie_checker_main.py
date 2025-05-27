from typing import Dict, Optional, List, Set
import os
import zipfile
import shutil
import datetime
import json

from .classification.cookie import get_cookie_issues
from .classification.tracking import check_for_tracking_pixels, analyze_tracking
from .classification.storage import (
    check_local_storage_entries,
    check_session_storage_entries,
)

from .classification.encryption import check_encryption
from .classification.types_models import (
    CookieResult,
    FolderResult,
    StorageViolation,
    TrackingIssue,
    RequestIssue,
)


def extract_files_from_zip(zip_file_path: str, temp_dir: str) -> List[Dict[str, str]]:
    """
    Extract browser data log files and network request files from a ZIP file

    Args:
        zip_file_path: Path to the ZIP file
        temp_dir: Directory to extract files to

    Returns:
        List of dictionaries containing extracted file paths
    """
    extracted_files = []

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Find all browser_data_log.jsonl files in the zip
        log_files = [
            f for f in zip_ref.namelist() if f.endswith("browser_data_log.jsonl")
        ]

        if not log_files:
            print("No browser_data_log.jsonl files found in the zip.")
            return []

        print(f"Found {len(log_files)} browser data log files.")

        for log_file in log_files:
            folder_name = os.path.dirname(log_file)

            # Extract the browser data log file
            zip_ref.extract(log_file, temp_dir)
            extracted_log_path = os.path.join(temp_dir, log_file)

            # Check if there's a network_requests.json file in the same folder
            network_file = f"{folder_name}/network_requests.json"
            network_file_path = None

            if network_file in zip_ref.namelist():
                zip_ref.extract(network_file, temp_dir)
                network_file_path = os.path.join(temp_dir, network_file)

            extracted_files.append(
                {
                    "folder_name": folder_name,
                    "log_file": log_file,
                    "log_path": extracted_log_path,
                    "network_file_path": network_file_path,
                }
            )

    return extracted_files


def process_zip_file(zip_file_path: str) -> List[Dict[str, str]]:
    """
    Process a ZIP file and extract browser data log files and network request files

    Args:
        zip_file_path: Path to the ZIP file

    Returns:
        List of dictionaries containing extracted file paths
    """
    if not os.path.exists(zip_file_path):
        print(f"Error: File {zip_file_path} does not exist.")
        return []

    temp_dir = "temp_extract"
    os.makedirs(temp_dir, exist_ok=True)

    return extract_files_from_zip(zip_file_path, temp_dir)


def clean_up_temp_files(temp_dir: str = "temp_extract") -> None:
    """
    Clean up temporary files created during processing

    Args:
        temp_dir: Directory containing temporary files
    """
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def save_results_to_json(output_json: str, results_data: Dict) -> None:
    """
    Save results to a JSON file

    Args:
        output_json: Path to save the JSON output file
        results_data: Data to save
    """
    try:
        with open(output_json, "w") as f:
            json.dump(results_data, f, indent=2)
        print(f"\nTracking findings saved to: {output_json}")
    except Exception as e:
        print(f"Error saving JSON output: {e}")


def create_output_directory(directory: str = "results") -> None:
    """
    Create directory for output files if it doesn't exist

    Args:
        directory: Directory to create
    """
    os.makedirs(directory, exist_ok=True)


class CookieZipProcessor:
    """Processes ZIP files containing browser data log files"""

    def __init__(
        self,
        zip_file_path: str,
    ) -> None:
        """
        Initialize with the ZIP file to process

        Args:
            zip_file_path: Path to the ZIP file
        """
        super().__init__()
        self.zip_file_path = zip_file_path

        # Results storage
        self.local_storage_results: List[StorageViolation] = []
        self.session_storage_results: List[StorageViolation] = []
        self.tracking_results: List[FolderResult] = []
        self.cookie_results: List[CookieResult] = []
        self.cross_page_tracking_found = False
        self.encryption_results: Dict[str, bool] = {}

        # Sets to collect unique tracking issues
        self.unique_tracking_pixels: Set[str] = set()
        self.unique_suspicious_resources: Set[str] = set()
        self.unique_suspicious_requests: Set[str] = set()
        self.unique_cookie_issues: Set[str] = set()

    def process(self) -> None:
        """
        Process the ZIP file and run all checks

        Args:
            output_json: Path to save the JSON output file (default: None)

        Returns:
            Results of all checks
        """
        extracted_files = process_zip_file(self.zip_file_path)

        if not extracted_files:
            return

        create_output_directory("results")
        for file_info in extracted_files:
            self._run_checks(**file_info)
            folder_name = os.path.basename(file_info["folder_name"])
            # Create filename with timestamp and folder name
            output_json = f"results/result_{folder_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self._save_to_json(output_json)

        # Clean up temporary files
        clean_up_temp_files()

        return

    def _run_checks(
        self,
        folder_name: str,
        log_file: str,
        log_path: str,
        network_file_path: Optional[str],
    ) -> None:
        """Run all checks on the extracted log file"""

        # Run encryption check
        self.encryption_results = check_encryption(log_path)

        # Run tracking pixel check
        tracking_issues = check_for_tracking_pixels(log_path, network_file_path)

        # Run cookie check
        cookie_issues = get_cookie_issues(log_path)
        if cookie_issues:
            self.cookie_results.append(
                CookieResult(
                    folder=folder_name,
                    file=log_file,
                    issues=cookie_issues,
                )
            )
            # Add unique cookie issues
            for issue in cookie_issues:
                if issue.type == "unnecessary_cookie":
                    self.unique_cookie_issues.add(issue.name)
        if self.unique_cookie_issues:
            print("Cookie check failed")
        else:
            print("Cookie check passed")

        # Collect unique tracking URLs
        for tracking_issue in tracking_issues:
            if isinstance(tracking_issue, TrackingIssue):
                url = tracking_issue.resource.url
                if url:
                    self.unique_tracking_pixels.add(url)
            elif isinstance(tracking_issue, RequestIssue):
                url = tracking_issue.url
                if url:
                    self.unique_suspicious_requests.add(url)

        # Determine if tracking check passed (no issues found)
        tracking_passed = len(tracking_issues) == 0

        if self.unique_tracking_pixels:
            print("Tracking Pixel check failed")
        else:
            print("Tracking Pixel check passed")

        if self.unique_suspicious_resources:
            print("Suspicious Resource check failed")
        else:
            print("Suspicious Resource check passed")

        if self.unique_suspicious_requests:
            print("Suspicious Request check failed")
        else:
            print("Suspicious Request check passed")

        # Analyze tracking for cross-page tracking
        cross_tracking_analysis = analyze_tracking(tracking_issues)
        if cross_tracking_analysis.has_cross_page_tracking:
            self.cross_page_tracking_found = True
            tracking_passed = False

        # Check storage entries
        local_passed, local_unauthorized = check_local_storage_entries(log_path)
        if local_passed:
            print("Local storage check passed")
        else:
            print("Local storage check failed")

        session_passed, session_unauthorized = check_session_storage_entries(log_path)
        if session_passed:
            print("Session storage check passed")
        else:
            print("Session storage check failed")

        # Store tracking check results
        if not tracking_passed:
            has_cross_tracking = cross_tracking_analysis.has_cross_page_tracking
            self.tracking_results.append(
                FolderResult(
                    folder=folder_name,
                    file=log_file,
                    issues=tracking_issues,
                    cross_page_tracking=has_cross_tracking,
                    cross_page_analysis=cross_tracking_analysis,
                )
            )

        # Store storage check results if there are violations
        if not local_passed:
            self.local_storage_results.append(
                StorageViolation(
                    folder=folder_name,
                    file=log_file,
                    unauthorized=local_unauthorized,
                )
            )

        if not session_passed:
            self.session_storage_results.append(
                StorageViolation(
                    folder=folder_name,
                    file=log_file,
                    unauthorized=session_unauthorized,
                )
            )

    def _save_to_json(self, output_json: str) -> None:
        """Save the results to a JSON file"""
        # Convert Pydantic models to dictionaries
        unique_local_storage_issues = [
            [entry.model_dump() for entry in i.unauthorized]
            for i in self.local_storage_results
        ]
        unique_session_storage_issues = [
            [entry.model_dump() for entry in i.unauthorized]
            for i in self.session_storage_results
        ]

        tracking_output = {
            "unique_tracking_pixels": sorted(list(self.unique_tracking_pixels)),
            "unique_suspicious_resources": sorted(
                list(self.unique_suspicious_resources)
            ),
            "unique_suspicious_requests": sorted(list(self.unique_suspicious_requests)),
            "unique_unnecessary_cookies": sorted(list(self.unique_cookie_issues)),
            "cross_page_tracking_found": self.cross_page_tracking_found,
            "overall_passed": self._get_overall_passed(),
            "local_storage_issues": unique_local_storage_issues,
            "session_storage_issues": unique_session_storage_issues,
            "encryption_results": self.encryption_results,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        save_results_to_json(output_json, tracking_output)

    def _get_overall_passed(self) -> bool:
        """Determine if all checks passed"""
        return (
            len(self.tracking_results) == 0
            and len(self.local_storage_results) == 0
            and len(self.session_storage_results) == 0
            and len(self.cookie_results) == 0
        )


if __name__ == "__main__":
    processor = CookieZipProcessor("tmp/schooltogo.de_legal.zip")
    processor.process()

    print("\n=== Tracking Pixels ===")
    print(f"Found {len(processor.unique_tracking_pixels)} unique tracking pixels")

    print("\n=== Suspicious Resources ===")
    print(
        f"Found {len(processor.unique_suspicious_resources)} unique suspicious resources"
    )

    print("\n=== Suspicious Requests ===")
    print(
        f"Found {len(processor.unique_suspicious_requests)} unique suspicious requests"
    )

    print("\n=== Cookie Issues ===")
    print(f"Found {len(processor.unique_cookie_issues)} unique cookie issues")

    print("\n=== Cross-Page Tracking ===")
    print(f"Cross-page tracking found: {processor.cross_page_tracking_found}")

    print("\n=== Encryption Results ===")
    for check, result in processor.encryption_results.items():
        print(f"{check}: {'Passed' if result else 'Failed'}")

    print("\n=== Overall Result ===")
    print(f"All checks passed: {processor._get_overall_passed()}")
