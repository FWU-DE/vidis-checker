import argparse
import datetime
from report.report import Report
from src.cookie_checker_main import CookieZipProcessor
from src.imprint import check_imprint
from src.privacy_policy import check_privacy_policy
from reportlab.lib.units import mm

from src.terms_of_use import check_terms_of_use


class VidisCriterionResult:
    def __init__(self, criterion_code: str, result: bool | None, explanation: str):
        self.criterion_code = criterion_code
        self.result = result
        self.explanation = explanation


class TaskResult:
    def __init__(self, name: str):
        zip_path = f"tmp/{name}.zip"
        privacy_policy_path = f"tmp/{name}/privacy_policy.pdf"
        imprint_path = f"tmp/{name}/imprint.pdf"
        terms_of_use_path = f"tmp/{name}/terms_of_use.pdf"

        self.cookie_zip_processor = CookieZipProcessor(zip_path)
        self.privacy_policy_path = privacy_policy_path
        self.imprint_path = imprint_path
        self.terms_of_use_path = terms_of_use_path

    def check_result(self) -> str:
        # privacy_policy_check_result = check_privacy_policy(self.privacy_policy_path)
        # imprint_check_result = check_imprint(self.imprint_path)
        self.cookie_zip_processor.process()

        return {
            "RDS-CDN-379": VidisCriterionResult(
                criterion_code="RDS-CDN-379",
                result=None,
                explanation="Dieses Kriterium wird nicht geprüft.",
            ),
            "RDS-CUC-371": self.check_criterion_rds_cuc_371(),
            "RDS-CUC-372": self.check_criterion_rds_cuc_372(),
            "RDS-CUC-373": self.check_criterion_rds_cuc_373(),
            "RDS-CUC-374": self.check_criterion_rds_cuc_374(),
            "RDS-CUC-375": VidisCriterionResult(
                criterion_code="RDS-CUC-375",
                result=None,
                explanation="Dieses Kriterium wird nicht geprüft.",
            ),
            "RDS-CUC-376": VidisCriterionResult(
                criterion_code="RDS-CUC-376",
                result=None,
                explanation="Dieses Kriterium wird nicht geprüft.",
            ),
            "RDS-CUC-377": VidisCriterionResult(
                criterion_code="RDS-CUC-377",
                result=None,
                explanation="Dieses Kriterium wird nicht geprüft.",
            ),
            "RDS-CUC-453": VidisCriterionResult(
                criterion_code="RDS-CUC-453",
                result=None,
                explanation="TODO",
            ),
            "RDS-DEV-380": VidisCriterionResult(
                criterion_code="RDS-DEV-380",
                result=None,
                explanation="Dieses Kriterium wird nicht geprüft.",
            ),
            "RDS-DEV-381": VidisCriterionResult(
                criterion_code="RDS-DEV-381",
                result=None,
                explanation="Dieses Kriterium wird nicht geprüft.",
            ),
            "RDS-DEV-466": VidisCriterionResult(
                criterion_code="RDS-DEV-466",
                result=None,
                explanation="Dieses Kriterium wird nicht geprüft.",
            ),
            "RDS-DSO-383": self.check_criterion_rds_dso_383(),
            "RDS-IPF-364": self.check_criterion_rds_ipf_364(),
            "RDS-IPF-365": self.check_criterion_rds_ipf_365(),
            "RDS-IPF-366": self.check_criterion_rds_ipf_366(),
            "RDS-IPF-367": self.check_criterion_rds_ipf_367(),
            "ITS-ENC-359": self.check_criterion_its_enc_359(),
            "ITS-ENC-360": self.check_criterion_its_enc_360(),
            "ITS-ENC-361": self.check_criterion_its_enc_361(),
            "RDS-AGB-368": self.check_criterion_rds_agb_368(),
            "RDS-AGB-369": self.check_criterion_rds_agb_369(),
        }

    def check_criterion_rds_cuc_371(self) -> VidisCriterionResult:
        print("Checking RDS-CUC-371")
        cookie_issues = self.cookie_zip_processor.unique_cookie_issues
        if cookie_issues:
            return VidisCriterionResult(
                criterion_code="RDS-CUC-371",
                result=False,
                explanation="Folgende Cookies werden gesetzt, die für den Betrieb der Webseite nicht erforderlich sind: "
                + ", ".join(cookie_issues),
            )
        else:
            return VidisCriterionResult(
                criterion_code="RDS-CUC-371",
                result=True,
                explanation="Es werden keine nicht essenzielle Cookies gesetzt.",
            )

    def check_criterion_rds_cuc_372(self) -> VidisCriterionResult:
        print("Checking RDS-CUC-372")
        return self.check_criterion_rds_cuc_371()

    def check_criterion_rds_cuc_373(self) -> VidisCriterionResult:
        print("Checking RDS-CUC-373")
        tracking_pixels = self.cookie_zip_processor.unique_tracking_pixels
        if tracking_pixels:
            return VidisCriterionResult(
                criterion_code="RDS-CUC-373",
                result=False,
                explanation="Folgende Trackingpixel werden verwendet: "
                + ", ".join(tracking_pixels),
            )
        else:
            return VidisCriterionResult(
                criterion_code="RDS-CUC-373",
                result=True,
                explanation="Es werden keine Trackingpixel verwendet.",
            )

    def check_criterion_rds_cuc_374(self) -> VidisCriterionResult:
        print("Checking RDS-CUC-374")
        local_storage_results = []
        for violation in self.cookie_zip_processor.local_storage_results:
            for entry in violation.unauthorized:
                local_storage_results.append(f"{entry.url}: {entry.key}")

        session_storage_results = []
        for violation in self.cookie_zip_processor.session_storage_results:
            for entry in violation.unauthorized:
                session_storage_results.append(f"{entry.url}: {entry.key}")

        if local_storage_results or session_storage_results:
            return VidisCriterionResult(
                criterion_code="RDS-CUC-374",
                result=False,
                explanation="Folgende Daten werden im Local Browser Storage oder Session Storage abgelegt: "
                + ", ".join(local_storage_results)
                + ", ".join(session_storage_results),
            )
        else:
            return VidisCriterionResult(
                criterion_code="RDS-CUC-374",
                result=True,
                explanation="Es werden keine Daten im Local Browser Storage oder Session Storage abgelegt.",
            )

    def check_criterion_rds_dso_383(self) -> VidisCriterionResult:
        print("Checking RDS-DSO-383")
        dpo_check_result, dpo_check_explanation = check_privacy_policy(
            self.privacy_policy_path, dpo_only=True
        )
        return VidisCriterionResult(
            criterion_code="RDS-DSO-383",
            result=dpo_check_result,
            explanation=dpo_check_explanation,
        )

    def check_criterion_rds_ipf_364(self) -> VidisCriterionResult:
        print("Checking RDS-IPF-364")
        return VidisCriterionResult(
            criterion_code="RDS-IPF-364",
            result=True,
            explanation="Das Impressum ist von allen Seiten erreichbar.",
        )

    def check_criterion_rds_ipf_365(self) -> VidisCriterionResult:
        print("Checking RDS-IPF-365")
        return VidisCriterionResult(
            criterion_code="RDS-IPF-365",
            result=True,
            explanation="Die Datenschutzerklärung ist von allen Seiten erreichbar.",
        )

    def check_criterion_rds_ipf_366(self) -> VidisCriterionResult:
        print("Checking RDS-IPF-366")
        imprint_check_result, imprint_check_explanation = check_imprint(
            self.imprint_path
        )
        return VidisCriterionResult(
            criterion_code="RDS-IPF-366",
            result=imprint_check_result,
            explanation=imprint_check_explanation,
        )

    def check_criterion_rds_ipf_367(self) -> VidisCriterionResult:
        print("Checking RDS-IPF-367")
        privacy_policy_check_result, privacy_policy_check_explanation = (
            check_privacy_policy(self.privacy_policy_path)
        )
        return VidisCriterionResult(
            criterion_code="RDS-IPF-367",
            result=privacy_policy_check_result,
            explanation=privacy_policy_check_explanation,
        )

    def check_criterion_its_enc_359(self) -> VidisCriterionResult:
        print("Checking ITS-ENC-359")
        https_available = self.cookie_zip_processor.encryption_results[
            "https_available"
        ]
        http_disabled = self.cookie_zip_processor.encryption_results["http_disabled"]
        if https_available and not http_disabled:
            return VidisCriterionResult(
                criterion_code="ITS-ENC-359",
                result=True,
                explanation="Die Website ist ausschließlich über https:// aufrufbar.",
            )
        else:
            return VidisCriterionResult(
                criterion_code="ITS-ENC-359",
                result=False,
                explanation="Die Website ist nicht ausschließlich über https:// aufrufbar.",
            )

    def check_criterion_its_enc_360(self) -> VidisCriterionResult:
        print("Checking ITS-ENC-360")
        http_to_https_redirect = self.cookie_zip_processor.encryption_results[
            "http_to_https_redirect"
        ]
        if http_to_https_redirect:
            return VidisCriterionResult(
                criterion_code="ITS-ENC-360",
                result=True,
                explanation="Es sind Umleitungen von http auf https konfiguriert.",
            )
        else:
            return VidisCriterionResult(
                criterion_code="ITS-ENC-360",
                result=False,
                explanation="Es sind keine Umleitungen von http auf https konfiguriert.",
            )

    def check_criterion_its_enc_361(self) -> VidisCriterionResult:
        print("Checking ITS-ENC-361")
        tls_ssl_secure = self.cookie_zip_processor.encryption_results["tls_ssl_secure"]
        if tls_ssl_secure:
            return VidisCriterionResult(
                criterion_code="ITS-ENC-361",
                result=True,
                explanation="Veraltete TLS/SSL-Protokolle werden abgelehnt.",
            )
        else:
            return VidisCriterionResult(
                criterion_code="ITS-ENC-361",
                result=False,
                explanation="Veraltete TLS/SSL-Protokolle werden nicht abgelehnt.",
            )

    def check_criterion_rds_agb_368(self) -> VidisCriterionResult:
        print("Checking RDS-AGB-368")
        check_result, check_explanation = check_terms_of_use(
            self.terms_of_use_path, processor_only=False
        )
        return VidisCriterionResult(
            criterion_code="RDS-AGB-368",
            result=check_result,
            explanation=check_explanation,
        )

    def check_criterion_rds_agb_369(self) -> VidisCriterionResult:
        print("Checking RDS-AGB-369")
        check_result, check_explanation = check_terms_of_use(
            self.terms_of_use_path, processor_only=True
        )
        return VidisCriterionResult(
            criterion_code="RDS-AGB-369",
            result=check_result,
            explanation=check_explanation,
        )


def create_pdf_report(
    results: dict[str, VidisCriterionResult],
    criteria: dict[str, VidisCriterion],
    output_path: str,
):
    """
    Generate a PDF report summarizing each VidisCriterion and its check result.

    :param results: mapping criterion code -> VidisCriterionResult
    :param criteria: mapping criterion code -> VidisCriterion
    :param output_path: target file path, e.g. 'report.pdf'
    """
    # Create a new report
    report = Report(output_path)

    # Title page
    report.add_spacer(50 * mm)
    report.add_title("Vidis Checker Bericht")
    report.add_spacer(10 * mm)
    report.add_text(
        "Automatisch erstellt am "
        + datetime.datetime.now().strftime("%d.%m.%Y")
        + " um "
        + datetime.datetime.now().strftime("%H:%M:%S"),
        report.styles["Italic"],
    )
    report.add_spacer(10 * mm)
    report.add_paragraph(
        "Der vorliegende Bericht wurde automatisch erstellt und ersetzt keine offizielle Prüfung durch Vidis."
    )
    report.add_page_break()

    # One section per criterion
    for code in sorted(criteria.keys()):
        crit = criteria[code]
        res = results.get(code)

        # Header: code + name
        report.add_header(f"{crit.code} — {crit.name}")

        # Description
        report.add_paragraph(f"Kriteriumsbeschreibung: {crit.description}")

        # Explanation (if available)
        if res and res.explanation:
            report.add_paragraph(f"Prüfungsergebnis: {res.explanation}")

        # Pass / Fail icon + label
        if res is None:
            icon, label, col = "⚠", "Nicht geprüft", "#ffc107"
        elif res.result is None:
            icon, label, col = "⚠", "Nicht geprüft", "#ffc107"
        elif res.result:
            icon, label, col = "✓", "Bestanden", "#28a745"
        else:
            icon, label, col = "✗", "Nicht bestanden", "#dc3545"

        report.add_result(icon, label, col)

        # Separator
        report.add_separator()

    # Generate the PDF
    report.generate_pdf()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate PDF report from task results"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Input name for ClickPathResult (e.g. 'schooltogo_legal')",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="report.pdf",
        help="Output path for the PDF report",
    )

    args = parser.parse_args()

    task_result = TaskResult(args.input)
    check_result = task_result.check_result()
    create_pdf_report(check_result, criteria, args.output)
