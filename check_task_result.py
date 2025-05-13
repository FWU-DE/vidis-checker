import argparse
import datetime
from src.cookie_checker_main import CookieZipProcessor
from src.imprint import check_imprint
from src.privacy_policy import check_privacy_policy
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from src.terms_of_use import check_terms_of_use


class VidisCriterion:
    def __init__(self, code: str, name: str, description: str):
        self.code = code
        self.name = name
        self.description = description

rds_cdn_379_text = """
Es wird kein CDN genutzt, das nicht ausschließlich der reinen Bereitstellung von Inhalten dient.
Darüber hinaus erfüllt das CDN die Voraussetzungen des Prüfunterbereichs Dienstleister.
"""

rds_cuc_371_text = """
Es werden keine Cookies gesetzt, die für den Betrieb der Webseite nicht erforderlich sind, sofern sich diese an die Nutzergruppe der Schülerinnen und Schüler richten.
Richtet sich das Angebot an Lehrkräfte, wird dafür eine entsprechende Einwilligung eingeholt.
"""

rds_cuc_372_text = """
Es werden keine Cookies gesetzt, für die eine Einwilligung erforderlich ist, sofern sich das Angebot an die Nutzergruppe der Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, kann die Einwilligung eingeholt werden.
"""

rds_cuc_373_text = """
Es werden keine Trackingpixel verwendet, wenn sich ein Angebot an Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, wird dafür eine entsprechende Einwilligung eingeholt.
"""

rds_cuc_374_text = """
Es werden keine Daten im Local Browser Storage oder Session Storage abgelegt, sofern dafür eine Einwilligung erforderlich ist und sich das Angebot an die Nutzergruppe der Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, darf die Einwilligung eingeholt werden.
Dies schützt die Privatsphäre der Schülerinnen und Schüler und gewährleistet die Einhaltung datenschutzrechtlicher Anforderungen.
"""

rds_cuc_375_text = """
Es werden keine sonstigen Informationen auf der Endeinrichtung des Endnutzers gespeichert und es erfolgt kein Zugriff auf Informationen, die bereits in der Endeinrichtung gespeichert sind, sofern dafür eine Einwilligung erforderlich ist und sich das Angebot an die Nutzergruppe der Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, darf die Einwilligung eingeholt werden.
"""

rds_cuc_376_text = """
Es werden keine Browserfingerprints gebildet, wenn sich ein Angebot an Schülerinnen und Schüler richtet.
Richtet sich das Angebot an Lehrkräfte, wird dafür eine entsprechende Einwilligung eingeholt
"""

rds_cuc_377_text = """
Es werden keine Trackingmechanismen eingesetzt, wenn sich ein Angebot an Schülerinnen und Schüler richtet, es sei denn, das Nutzerverhalten wird aus pädagogischen Gründen getrackt, wie z. B. bei adaptiven Lernsystemen notwendig.
Richtet sich das Angebot an Lehrkräfte, wird dafür eine entsprechende Einwilligung eingeholt.
"""

rds_cuc_453_text = """
Bei der Nutzung von Web-Browsern, als auch bei der Nutzung von Mobile Apps (Webansichten, integrierte Browserumgebungen) können sog. "Cookies" genutzt werden.
Der Anbieter beschreibt alle "Cookies" seines Angebots und deren Zwecke in der Datenschutzerklärung
"""

rds_dev_380_text = """
Daten werden ausschließlich für die Nutzung des Angebots verarbeitet.
Insbesondere eine Nutzung zu Werbezwecken ist ausgeschlossen.
"""

rds_dev_381_text = """
Nach Beendigung der Zusammenarbeit mit dem Auftraggeber werden die Daten des Auftraggebers (also beispielsweise die Daten sämtlicher Schülerinnen und Schüler sowie Lehrkräfte einer Schule, mit der ein Vertrag zur Auftragsverarbeitung geschlossen wurde) nach Wahl des Auftraggebers gelöscht und, wenn gewünscht, an diesen herausgegeben.
"""

rds_dev_466_text = """
Es werden keine Server in unsicheren Drittländern eingesetzt und/oder Datenverarbeitungen in unsicheren Drittländern durchgeführt.
Dies gilt auch für Sub- oder Mutterunternehmen.
"""

rds_dso_383_text = """
Der Anbieter stellt die Kontaktdaten des Datenschutzbeauftragten bereit.
Falls noch kein Datenschutzbeauftragter existiert, benennt der Anbieter den DSB.
"""

rds_ipf_364_text = """
Ein stets verfügbares und leicht erkennbares Impressum ist von allen Seiten erreichbar.
Dies gilt insbesondere bei Angeboten mit responsiven Designs
"""

rds_ipf_365_text = """
Eine stets verfügbare und leicht erkennbare Datenschutzerklärung ist von allen Seiten erreichbar.
Dies gilt insbesondere bei Angeboten mit responsiven Designs.
"""

rds_ipf_366_text = """
Das Impressum enthält alle nach § § 5 und 6 DDG vorgeschriebenen Informationen.
"""

rds_ipf_367_text = """
Die Datenschutzerklärung enthält alle Informationen, die nach Art. 13 und 14 DSGVO vorgeschrieben sind.
"""

its_enc_359_text = """
Seiten des Angebots sind ausschließlich über https abrufbar.
"""

its_enc_360_text = """
Es sind Umleitungen von http auf https konfiguriert.
"""

its_enc_361_text = """
Veraltete TLS/SSL-Protokolle werden abgelehnt.
"""

rds_agb_368_text = """
Die Nutzungsbedingungen oder AGB des Angebots enthalten keine Klauseln, die gegen die Grundsätze des Datenschutzes verstoßen.
"""

rds_agb_369_text = """
Die Nutzungsbedingungen oder AGB des Angebots enthalten keine Klauseln, die gegen die Vorschriften zur Auftragsverarbeitung verstoßen.
"""

criteria = {
    "RDS-CDN-379": VidisCriterion(
        code="RDS-CDN-379",
        name="CDN nur zur Bereitstellung von Inhalten",
        description=rds_cdn_379_text,
    ),
    "RDS-CUC-371": VidisCriterion(
        code="RDS-CUC-371",
        name="Nicht essenzielle Cookies",
        description=rds_cuc_371_text,
    ),
    "RDS-CUC-372": VidisCriterion(
        code="RDS-CUC-372", name="Cookies allgemein", description=rds_cuc_372_text
    ),
    "RDS-CUC-373": VidisCriterion(
        code="RDS-CUC-373", name="Trackingpixel", description=rds_cuc_373_text
    ),
    "RDS-CUC-374": VidisCriterion(
        code="RDS-CUC-374", name="Local Browser Storage", description=rds_cuc_374_text
    ),
    "RDS-CUC-375": VidisCriterion(
        code="RDS-CUC-375", name="Informationen auf der Endeinrichtung des Endnutzers", description=rds_cuc_375_text
    ),
    "RDS-CUC-376": VidisCriterion(
        code="RDS-CUC-376", name="Browserfingerprints", description=rds_cuc_376_text
    ),
    "RDS-CUC-377": VidisCriterion(
        code="RDS-CUC-377", name="Trackingmechanismen zu nicht pädagogischen Zwecken", description=rds_cuc_377_text
    ),
    "RDS-CUC-453": VidisCriterion(
        code="RDS-CUC-453", name="Beschreibung aller Cookies", description=rds_cuc_453_text
    ),
    "RDS-DEV-380": VidisCriterion(
        code="RDS-DEV-380", name="Datenerhebung und -verarbeitung", description=rds_dev_380_text
    ),
    "RDS-DEV-381": VidisCriterion(
        code="RDS-DEV-381", name="Umgang mit Daten nach Beendigung der Zusammenarbeit", description=rds_dev_381_text
    ),
    "RDS-DEV-466": VidisCriterion(
        code="RDS-DEV-466", name="Sichere Datenverarbeitung", description=rds_dev_466_text
    ),
    "RDS-DSO-383": VidisCriterion(
        code="RDS-DSO-383", name="Benennung eines Datenschutzbeauftragten", description=rds_dso_383_text
    ),
    "RDS-IPF-364": VidisCriterion(
        code="RDS-IPF-364",
        name="Leicht auffindbares Impressum",
        description=rds_ipf_364_text,
    ),
    "RDS-IPF-365": VidisCriterion(
        code="RDS-IPF-365",
        name="Leicht auffindbare Datenschutzerklärung",
        description=rds_ipf_365_text,
    ),
    "RDS-IPF-366": VidisCriterion(
        code="RDS-IPF-366", name="Vollständiges Impressum", description=rds_ipf_366_text
    ),
    "RDS-IPF-367": VidisCriterion(
        code="RDS-IPF-367",
        name="Vollständige Datenschutzerklärung",
        description=rds_ipf_367_text,
    ),
    "ITS-ENC-359": VidisCriterion(
        code="ITS-ENC-359",
        name="Website nur über https:// aufrufbar",
        description=its_enc_359_text,
    ),
    "ITS-ENC-360": VidisCriterion(
        code="ITS-ENC-360",
        name="Es sind Umleitungen von http auf https konfiguriert.",
        description=its_enc_360_text,
    ),
    "ITS-ENC-361": VidisCriterion(
        code="ITS-ENC-361",
        name="Ablehnen veralteter TLS/SSL-Protokolle",
        description=its_enc_361_text,
    ),
    "RDS-AGB-368": VidisCriterion(
        code="RDS-AGB-368",
        name="utzungsbedingungen/AGB: Datenschutzkonform",
        description=rds_agb_368_text,
    ),
    "RDS-AGB-369": VidisCriterion(
        code="RDS-AGB-369",
        name="Nutzungsbedingungen/AGB: AVV-konform",
        description=rds_agb_369_text,
    ),
}


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
        return self.check_criterion_rds_cuc_371()

    def check_criterion_rds_cuc_373(self) -> VidisCriterionResult:
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
        dpo_check_result, dpo_check_explanation = check_privacy_policy(
            self.privacy_policy_path,
            dpo_only=True
        )
        return VidisCriterionResult(
            criterion_code="RDS-DSO-383",
            result=dpo_check_result,
            explanation=dpo_check_explanation,
        )

    def check_criterion_rds_ipf_364(self) -> VidisCriterionResult:
        return VidisCriterionResult(
            criterion_code="RDS-IPF-364",
            result=True,
            explanation="Das Impressum ist von allen Seiten erreichbar.",
        )

    def check_criterion_rds_ipf_365(self) -> VidisCriterionResult:
        return VidisCriterionResult(
            criterion_code="RDS-IPF-365",
            result=True,
            explanation="Die Datenschutzerklärung ist von allen Seiten erreichbar.",
        )

    def check_criterion_rds_ipf_366(self) -> VidisCriterionResult:
        imprint_check_result, imprint_check_explanation = check_imprint(
            self.imprint_path
        )
        return VidisCriterionResult(
            criterion_code="RDS-IPF-366",
            result=imprint_check_result,
            explanation=imprint_check_explanation,
        )

    def check_criterion_rds_ipf_367(self) -> VidisCriterionResult:
        privacy_policy_check_result, privacy_policy_check_explanation = (
            check_privacy_policy(self.privacy_policy_path)
        )
        return VidisCriterionResult(
            criterion_code="RDS-IPF-367",
            result=privacy_policy_check_result,
            explanation=privacy_policy_check_explanation,
        )

    def check_criterion_its_enc_359(self) -> VidisCriterionResult:
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
        check_result, check_explanation = check_terms_of_use(
            self.terms_of_use_path,
            processor_only=False
        )
        return VidisCriterionResult(
            criterion_code="RDS-AGB-368",
            result=check_result,
            explanation=check_explanation,
        )
    
    def check_criterion_rds_agb_369(self) -> VidisCriterionResult:
        check_result, check_explanation = check_terms_of_use(
            self.terms_of_use_path,
            processor_only=True
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
    # --- 1. Document setup ---
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Heading2"],
        alignment=TA_LEFT,
        spaceAfter=4,
        textColor=colors.HexColor("#2E4053"),
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        alignment=TA_LEFT,
        firstLineIndent=12,
        spaceAfter=8,
    )
    result_style = ParagraphStyle(
        "ResultStyle",
        parent=styles["BodyText"],
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    # --- 2. Build the flowable story ---
    story = []

    # Title page
    story.append(Spacer(1, 50 * mm))
    story.append(Paragraph("Vidis Checker Bericht", title_style))
    story.append(Spacer(1, 10 * mm))
    story.append(
        Paragraph(
            "Automatisch erstellt am "
            + datetime.datetime.now().strftime("%d.%m.%Y")
            + " um "
            + datetime.datetime.now().strftime("%H:%M:%S"),
            styles["Italic"],
        )
    )
    story.append(Spacer(1, 10 * mm))
    story.append(
        Paragraph(
            "Der vorliegende Bericht wurde automatisch erstellt und ersetzt keine offizielle Prüfung durch Vidis.",
            body_style,
        )
    )
    story.append(PageBreak())

    # --- 3. One section per criterion ---
    for code in sorted(criteria.keys()):
        crit = criteria[code]
        res = results.get(code)

        # Header: code + name
        story.append(Paragraph(f"{crit.code} — {crit.name}", header_style))

        # Description
        story.append(
            Paragraph(f"Kriteriumsbeschreibung: {crit.description}", body_style)
        )

        # Explanation (if available)
        if res and res.explanation:
            story.append(Paragraph(f"Prüfungsergebnis: {res.explanation}", body_style))

        # Pass / Fail icon + label
        if res is None:
            icon, label, col = "⚠", "Nicht geprüft", "#ffc107"
        elif res.result is None:
            icon, label, col = "⚠", "Nicht geprüft", "#ffc107"
        elif res.result:
            icon, label, col = "✓", "Bestanden", "#28a745"
        else:
            icon, label, col = "✗", "Nicht bestanden", "#dc3545"

        story.append(
            Paragraph(f'<font color="{col}">{icon} {label}</font>', result_style)
        )

        # Separator
        story.append(Spacer(1, 2 * mm))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        story.append(Spacer(1, 4 * mm))

    # --- 4. Build the PDF ---
    doc.build(story)
    print(f"Report written to {output_path}")


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
