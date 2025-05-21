from src.classification.cookie import get_cookie_check_results
from src.report.report import Report
import datetime
from typing import Union
from src.classification.cookie import CookieDbCheckResult, CookieLLMCheckResult


if __name__ == "__main__":
    # print(COOKIE_DATABASE.get_cookie_info("_crazyegg"))
    # print(COOKIE_DATABASE.is_cookie_essential("XSRF-TOKEN"))
    # cookies = get_cookies("../tmp/schooltogo.de_legal/browser_data_log.jsonl")
    # print(cookies)
    # issues = get_cookie_issues("../tmp/schooltogo.de_legal/browser_data_log.jsonl")
    # print(issues)
    results = get_cookie_check_results("tmp/schooltogo.de_legal/browser_data_log.jsonl")

    # Generate cookie report
    report = Report("cookie_report.pdf")

    # Add title and date
    report.add_title("Cookie Analysis Report")
    report.add_text(
        f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    report.add_spacer()

    # Add summary
    report.add_header("Summary")
    essential_count = sum(
        1
        for r in results
        if isinstance(r, (CookieDbCheckResult, CookieLLMCheckResult)) and r.is_essential
    )
    non_essential_count = sum(
        1
        for r in results
        if isinstance(r, (CookieDbCheckResult, CookieLLMCheckResult))
        and r.is_essential is False
    )
    unknown_count = sum(
        1
        for r in results
        if isinstance(r, CookieDbCheckResult) and r.is_essential is None
    )

    report.add_paragraph(f"Total cookies analyzed: {len(results)}")
    report.add_paragraph(f"Essential cookies: {essential_count}")
    report.add_paragraph(f"Non-essential cookies: {non_essential_count}")
    report.add_paragraph(f"Unknown classification: {unknown_count}")
    report.add_spacer()

    # Add detailed results
    report.add_header("Detailed Cookie Analysis")

    for result in results:
        report.add_separator()

        if isinstance(result, CookieDbCheckResult):
            report.add_text(
                f"<b>Cookie Name:</b> {result.cookie_name}", report.body_style
            )
            report.add_text(
                f"<b>Domain:</b> {result.cookie.domain}", report.body_style
            )

            if result.is_essential:
                report.add_result("✓", "Essential Cookie", "#27AE60")
            elif result.is_essential is False:
                report.add_result("⚠", "Non-Essential Cookie", "#E74C3C")
            else:
                report.add_result("?", "Unknown Classification", "#F39C12")

            report.add_text(
                f"<b>Category:</b> {result.cookie_info.category}", report.body_style
            )
            report.add_text(
                f"<b>Description:</b> {result.cookie_info.description}",
                report.body_style,
            )
            report.add_text(
                f"<b>Retention Period:</b> {result.cookie_info.retention_period}",
                report.body_style,
            )

        elif isinstance(result, CookieLLMCheckResult):
            report.add_text(
                f"<b>Cookie Name:</b> {result.cookie_name}", report.body_style
            )
            report.add_text(
                f"<b>Domain:</b> {result.cookie_details.domain}", report.body_style
            )

            if result.is_essential:
                report.add_result(
                    "✓", "Essential Cookie (AI Classification)", "#27AE60"
                )
            else:
                report.add_result(
                    "⚠", "Non-Essential Cookie (AI Classification)", "#E74C3C"
                )

            report.add_text("<b>Explanation:</b>", report.body_style)
            report.add_paragraph(result.explanation)

    # Generate the PDF
    report.generate_pdf()
    print("Cookie report generated: cookie_report.pdf")
