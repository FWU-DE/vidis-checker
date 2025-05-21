from src.classification.storage import (
    get_local_storage_entries,
    get_session_storage_entries,
    check_local_storage_entries,
    check_session_storage_entries,
    SingleStorageEntryCheckResult,
)

from src.report.report import Report
import os
from datetime import datetime


if __name__ == "__main__":
    # Define the input file path
    input_file = "tmp/schooltogo.de_legal/browser_data_log.jsonl"

    # Create a report file with timestamp
    report_path = "storage_report.pdf"
    report = Report(report_path)

    # Add title and introduction
    report.add_title("Browser Storage Analysis Report")
    report.add_spacer()
    report.add_paragraph(
        f"Analysis of browser storage for data collected from: {input_file}"
    )
    report.add_paragraph(
        f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    report.add_separator()

    # Get and analyze local storage entries
    local_storage_entries = get_local_storage_entries(input_file)
    local_storage_results = check_local_storage_entries(input_file)

    # Add local storage section
    report.add_header("Local Storage Analysis")
    report.add_paragraph(
        f"Found {len(local_storage_entries)} unique local storage entries."
    )

    for result in local_storage_results:
        color = "#008000" if result.is_essential else "#FF0000"
        status = "✓ ESSENTIAL:" if result.is_essential else "✗ NON-ESSENTIAL:"

        report.add_result(status, f"Key: {result.key}", color)
        report.add_paragraph(f"Value: {result.value}")
        report.add_paragraph(f"URL: {result.url}")
        report.add_paragraph(f"Explanation: {result.explanation}")
        report.add_separator()

    report.add_page_break()

    # Get and analyze session storage entries
    session_storage_entries = get_session_storage_entries(input_file)
    session_storage_results = check_session_storage_entries(input_file)

    # Add session storage section
    report.add_header("Session Storage Analysis")
    report.add_paragraph(
        f"Found {len(session_storage_entries)} unique session storage entries."
    )

    for result in session_storage_results:
        color = "#008000" if result.is_essential else "#FF0000"
        status = "✓ ESSENTIAL:" if result.is_essential else "✗ NON-ESSENTIAL:"

        report.add_result(status, f"Key: {result.key}", color)
        report.add_paragraph(f"Value: {result.value}")
        report.add_paragraph(f"URL: {result.url}")
        report.add_paragraph(f"Explanation: {result.explanation}")
        report.add_separator()

    # Generate summary
    report.add_page_break()
    report.add_header("Summary")

    essential_local = sum(1 for r in local_storage_results if r.is_essential)
    essential_session = sum(1 for r in session_storage_results if r.is_essential)

    report.add_paragraph(
        f"Local Storage: {essential_local} essential entries out of {len(local_storage_results)}"
    )
    report.add_paragraph(
        f"Session Storage: {essential_session} essential entries out of {len(session_storage_results)}"
    )

    # Generate the PDF
    report.generate_pdf()
    print(f"Report generated successfully at {report_path}")
