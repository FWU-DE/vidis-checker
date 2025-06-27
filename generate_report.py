import argparse
from datetime import datetime
import os
from src.classification.images import ContentCheckResult
from src.classification.encryption import EncryptionCheckResult
from src.classification.imprint import ImprintCheckResult
from src.classification.privacy_policy import PrivacyPolicyCheckResult
from src.classification.storage import StorageCheckResult
from src.classification.tracking import TrackingPixelIssues
from src.report.report import Report
from src.classification.cookie import (
    CookieCheckResult,
    CookieLLMCheckResult,
)
from src.classification.terms_of_use import (
    TermsOfUseCheckResult,
    TermsOfUseProcessorOnlyCheckResult,
)
from src.models.vidis_criteria import VIDIS_CRITERIA, VidisCriterion


def add_vidis_criterion_to_report(report: Report, criterion: VidisCriterion):
    report.add_header(f"{criterion.code}: {criterion.name}")
    report.add_paragraph(f"<b>Erklärung:</b> {criterion.description}")


# RDS-CUC-371
def add_rds_cuc_371_to_report(report: Report, cookie_results: CookieCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-CUC-371"])

    for cookie_result in cookie_results.results:
        report.add_separator()
        if cookie_result.is_essential:
            report.add_success(f"Essentieller Cookie: {cookie_result.cookie_name}")
        else:
            report.add_failure(
                f"Nicht essentieller Cookie: {cookie_result.cookie_name}"
            )

        if isinstance(cookie_result, CookieLLMCheckResult):
            report.add_paragraph("Cookie wurde von KI überprüft:")
            report.add_paragraph(f"<i>{cookie_result.explanation}</i>")
        else:  # CookieDbCheckResult
            report.add_paragraph("Cookie wurde in der Cookie-Datenbank gefunden:")
            report.add_paragraph(
                f"<i>Kategorie: {cookie_result.cookie_info.category}</i>"
            )
            report.add_paragraph(
                f"<i>Beschreibung: {cookie_result.cookie_info.description}</i>"
            )

    # Check if there are any non-essential cookies
    has_non_essential_cookies = any(
        not result.is_essential for result in cookie_results.results
    )

    # Add overall assessment for this criterion
    report.add_separator()
    if has_non_essential_cookies:
        report.add_failure(
            "Kriterium nicht erfüllt: Es wurden nicht-essentielle Cookies gefunden."
        )
        report.add_paragraph(
            "Die Webseite verwendet Cookies, die nicht für die grundlegende Funktionalität erforderlich sind."
        )
    else:
        report.add_success(
            "Kriterium erfüllt: Es wurden nur essentielle Cookies gefunden."
        )
        report.add_paragraph(
            "Die Webseite verwendet ausschließlich Cookies, die für die grundlegende Funktionalität erforderlich sind."
        )


def add_rds_cuc_372_to_report(report: Report, cookie_results: CookieCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-CUC-372"])

    report.add_separator()
    report.add_paragraph("Siehe Auswertung von RDS-CUC-371")


def add_rds_cuc_373_to_report(report: Report, tracking_issues: TrackingPixelIssues):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-CUC-373"])

    for issue in tracking_issues.issues:
        report.add_separator()
        report.add_failure(f"Tracking Pixel gefunden: {issue.url}")
        report.add_paragraph(f"<i>{issue.explanation}</i>")

    report.add_separator()

    if len(tracking_issues.issues) > 0:
        report.add_failure(
            "Kriterium nicht erfüllt: Es wurden Tracking Pixel gefunden."
        )
    else:
        report.add_success(
            "Kriterium erfüllt: Es wurden keine Tracking Pixel gefunden."
        )


def add_rds_cuc_374_to_report(
    report: Report,
    local_storage_results: StorageCheckResult,
    session_storage_results: StorageCheckResult,
):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-CUC-374"])

    for result in local_storage_results.results:
        report.add_separator()
        if result.is_essential:
            report.add_success(
                f"Essentielles Local Storage Key-Value-Paar: {result.key}"
            )
            report.add_paragraph(f"<i>{result.explanation}</i>")
        else:
            report.add_failure(
                f"Nicht essentielles Local Storage Key-Value-Paar: {result.key}"
            )
            report.add_paragraph(f"<i>{result.explanation}</i>")

    for result in session_storage_results.results:
        report.add_separator()
        if result.is_essential:
            report.add_success(
                f"Essentielles Session Storage Key-Value-Paar: {result.key}"
            )
            report.add_paragraph(f"<i>{result.explanation}</i>")
        else:
            report.add_failure(
                f"Nicht essentielles Session Storage Key-Value-Paar: {result.key}"
            )
            report.add_paragraph(f"<i>{result.explanation}</i>")

    report.add_separator()

    if (
        len(local_storage_results.results) > 0
        or len(session_storage_results.results) > 0
    ):
        report.add_failure(
            "Kriterium nicht erfüllt: Es wurden nicht-essentielle Storage Key-Value-Paare gefunden."
        )
    else:
        report.add_success(
            "Kriterium erfüllt: Es wurden nur essentielle Storage Key-Value-Paare gefunden."
        )


def add_rds_dso_383_to_report(
    report: Report, privacy_policy_result: PrivacyPolicyCheckResult
):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-DSO-383"])

    report.add_separator()

    if privacy_policy_result.dpo_present:
        report.add_success(
            "Kriterium erfüllt: Es wurde der Datenschutzbeauftragte angegeben."
        )
    else:
        report.add_failure(
            "Kriterium nicht erfüllt: Es wurde kein Datenschutzbeauftragter angegeben."
        )

    report.add_paragraph(
        f"<b>Erklärung:</b> {privacy_policy_result.explanation_dpo_present}"
    )


def add_rds_ipf_364_to_report(report: Report):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-IPF-364"])

    report.add_separator()
    report.add_success("Kriterium erfüllt: Das Impressum wurde erfolgreich gefunden.")


def add_rds_ipf_365_to_report(report: Report):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-IPF-365"])

    report.add_separator()
    report.add_success(
        "Kriterium erfüllt: Die Datenschutzerklärung wurde erfolgreich gefunden."
    )


def add_rds_ipf_366_to_report(report: Report, imprint_result: ImprintCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-IPF-366"])

    report.add_separator()

    # Check each criterion and add to report
    if imprint_result.name_and_address_present:
        report.add_success("Name und Anschrift angegeben")
    else:
        report.add_failure("Name und Anschrift nicht angegeben")
    report.add_paragraph(
        f"<i>{imprint_result.explanation_name_and_address_present}</i>"
    )

    report.add_separator()

    if imprint_result.legal_form_present:
        report.add_success("Rechtsform angegeben")
    else:
        report.add_failure("Rechtsform nicht angegeben")
    report.add_paragraph(f"<i>{imprint_result.explanation_legal_form_present}</i>")

    report.add_separator()

    if imprint_result.contact_info_present:
        report.add_success("Kontaktinformationen angegeben")
    else:
        report.add_failure("Kontaktinformationen nicht angegeben")
    report.add_paragraph(f"<i>{imprint_result.explanation_contact_info_present}</i>")

    report.add_separator()

    if imprint_result.register_info_present:
        report.add_success("Registerinformationen angegeben")
    else:
        report.add_failure("Registerinformationen nicht angegeben")
    report.add_paragraph(f"<i>{imprint_result.explanation_register_info_present}</i>")

    report.add_separator()

    if imprint_result.legal_reference_current:
        report.add_success("Aktuelle Rechtsgrundlage referenziert")
    else:
        report.add_failure("Veraltete Rechtsgrundlage referenziert")
    report.add_paragraph(f"<i>{imprint_result.explanation_legal_reference_current}</i>")

    # Overall result
    report.add_separator()
    all_criteria_met = (
        imprint_result.name_and_address_present
        and imprint_result.legal_form_present
        and imprint_result.contact_info_present
        and imprint_result.register_info_present
        and imprint_result.legal_reference_current
        and imprint_result.tax_id_present
        and imprint_result.audiovisual_media_info_present
        and imprint_result.supervisory_authority_present
    )

    if all_criteria_met:
        report.add_success(
            "Kriterium erfüllt: Das Impressum enthält alle erforderlichen Informationen."
        )
    else:
        report.add_failure(
            "Kriterium nicht erfüllt: Das Impressum enthält nicht alle erforderlichen Informationen."
        )


def add_rds_ipf_367_to_report(
    report: Report, privacy_policy_result: PrivacyPolicyCheckResult
):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-IPF-367"])

    report.add_separator()

    # Check each criterion and add to report
    if privacy_policy_result.dpo_present:
        report.add_success("Datenschutzbeauftragter angegeben")
    else:
        report.add_failure("Datenschutzbeauftragter nicht angegeben")
    report.add_paragraph(f"<i>{privacy_policy_result.explanation_dpo_present}</i>")

    report.add_separator()

    if privacy_policy_result.processing_purposes_present:
        report.add_success("Verarbeitungszwecke angegeben")
    else:
        report.add_failure("Verarbeitungszwecke nicht angegeben")
    report.add_paragraph(
        f"<i>{privacy_policy_result.explanation_processing_purposes_present}</i>"
    )

    report.add_separator()

    if privacy_policy_result.legal_basis_present:
        report.add_success("Rechtsgrundlagen angegeben")
    else:
        report.add_failure("Rechtsgrundlagen nicht angegeben")
    report.add_paragraph(
        f"<i>{privacy_policy_result.explanation_legal_basis_present}</i>"
    )

    report.add_separator()

    if privacy_policy_result.recipients_present:
        report.add_success("Empfänger angegeben")
    else:
        report.add_failure("Empfänger nicht angegeben")
    report.add_paragraph(
        f"<i>{privacy_policy_result.explanation_recipients_present}</i>"
    )

    report.add_separator()

    if privacy_policy_result.storage_duration_present:
        report.add_success("Speicherdauer angegeben")
    else:
        report.add_failure("Speicherdauer nicht angegeben")
    report.add_paragraph(
        f"<i>{privacy_policy_result.explanation_storage_duration_present}</i>"
    )

    report.add_separator()

    if privacy_policy_result.data_subject_rights_present:
        report.add_success("Betroffenenrechte angegeben")
    else:
        report.add_failure("Betroffenenrechte nicht angegeben")
    report.add_paragraph(
        f"<i>{privacy_policy_result.explanation_data_subject_rights_present}</i>"
    )

    report.add_separator()

    if privacy_policy_result.data_provision_requirements_present:
        report.add_success("Anforderungen zur Datenbereitstellung angegeben")
    else:
        report.add_failure("Anforderungen zur Datenbereitstellung nicht angegeben")
    report.add_paragraph(
        f"<i>{privacy_policy_result.explanation_data_provision_requirements_present}</i>"
    )

    report.add_separator()

    if privacy_policy_result.automated_decision_making_info_present:
        report.add_success(
            "Informationen zur automatisierten Entscheidungsfindung angegeben"
        )
    else:
        report.add_failure(
            "Informationen zur automatisierten Entscheidungsfindung nicht angegeben"
        )
    report.add_paragraph(
        f"<i>{privacy_policy_result.explanation_automated_decision_making_info_present}</i>"
    )

    # Overall result
    report.add_separator()
    all_criteria_met = (
        privacy_policy_result.dpo_present
        and privacy_policy_result.processing_purposes_present
        and privacy_policy_result.legal_basis_present
        and privacy_policy_result.recipients_present
        and privacy_policy_result.storage_duration_present
        and privacy_policy_result.data_subject_rights_present
        and privacy_policy_result.data_provision_requirements_present
        and privacy_policy_result.automated_decision_making_info_present
    )

    if all_criteria_met:
        report.add_success(
            "Kriterium erfüllt: Die Datenschutzerklärung enthält alle erforderlichen Informationen."
        )
    else:
        report.add_failure(
            "Kriterium nicht erfüllt: Die Datenschutzerklärung enthält nicht alle erforderlichen Informationen."
        )


def add_rds_agb_368_to_report(
    report: Report, terms_of_use_result: TermsOfUseCheckResult
):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-AGB-368"])

    # Check transparency and lawfulness
    report.add_separator()
    if terms_of_use_result.transparency_and_lawfulness:
        report.add_success("Transparenz & Rechtmäßigkeit (Art. 5 Abs. 1 lit. a DSGVO)")
    else:
        report.add_failure("Transparenz & Rechtmäßigkeit (Art. 5 Abs. 1 lit. a DSGVO)")
    report.add_paragraph(
        f"<i>{terms_of_use_result.explanation_transparency_and_lawfulness}</i>"
    )

    # Check purpose limitation
    report.add_separator()
    if terms_of_use_result.purpose_limitation:
        report.add_success("Zweckbindung (Art. 5 Abs. 1 lit. b DSGVO)")
    else:
        report.add_failure("Zweckbindung (Art. 5 Abs. 1 lit. b DSGVO)")
    report.add_paragraph(f"<i>{terms_of_use_result.explanation_purpose_limitation}</i>")

    # Check data minimization
    report.add_separator()
    if terms_of_use_result.data_minimization:
        report.add_success(
            "Datenminimierung & Speicherbegrenzung (Art. 5 Abs. 1 lit. c + e DSGVO)"
        )
    else:
        report.add_failure(
            "Datenminimierung & Speicherbegrenzung (Art. 5 Abs. 1 lit. c + e DSGVO)"
        )
    report.add_paragraph(f"<i>{terms_of_use_result.explanation_data_minimization}</i>")

    # Check consent clauses
    report.add_separator()
    if terms_of_use_result.consent_clauses:
        report.add_success("Einwilligungsklauseln (Art. 7 DSGVO)")
    else:
        report.add_failure("Einwilligungsklauseln (Art. 7 DSGVO)")
    report.add_paragraph(f"<i>{terms_of_use_result.explanation_consent_clauses}</i>")

    # Check cookie/tracking consent
    report.add_separator()
    if terms_of_use_result.cookie_tracking_consent:
        report.add_success("Cookie/Tracking-Einwilligung (§ 25 TDDDG / TTDSG)")
    else:
        report.add_failure("Cookie/Tracking-Einwilligung (§ 25 TDDDG / TTDSG)")
    report.add_paragraph(
        f"<i>{terms_of_use_result.explanation_cookie_tracking_consent}</i>"
    )

    # Check data subject rights
    report.add_separator()
    if terms_of_use_result.data_subject_rights:
        report.add_success("Betroffenenrechte (Art. 12-22 DSGVO)")
    else:
        report.add_failure("Betroffenenrechte (Art. 12-22 DSGVO)")
    report.add_paragraph(
        f"<i>{terms_of_use_result.explanation_data_subject_rights}</i>"
    )

    # Check objection and opt-out
    report.add_separator()
    if terms_of_use_result.objection_and_opt_out:
        report.add_success("Widerspruchs- und Opt-out-Möglichkeiten")
    else:
        report.add_failure("Widerspruchs- und Opt-out-Möglichkeiten")
    report.add_paragraph(
        f"<i>{terms_of_use_result.explanation_objection_and_opt_out}</i>"
    )

    # Check third country transfers
    report.add_separator()
    if terms_of_use_result.third_country_transfers:
        report.add_success("Drittlandübermittlungen (Art. 44-49 DSGVO)")
    else:
        report.add_failure("Drittlandübermittlungen (Art. 44-49 DSGVO)")
    report.add_paragraph(
        f"<i>{terms_of_use_result.explanation_third_country_transfers}</i>"
    )

    # Check processors
    report.add_separator()
    if terms_of_use_result.processors:
        report.add_success("Auftragsverarbeiter (Art. 28 DSGVO)")
    else:
        report.add_failure("Auftragsverarbeiter (Art. 28 DSGVO)")
    report.add_paragraph(f"<i>{terms_of_use_result.explanation_processors}</i>")

    # Check profiling
    report.add_separator()
    if terms_of_use_result.profiling:
        report.add_success("Profiling / automatisierte Entscheidungen (Art. 22 DSGVO)")
    else:
        report.add_failure("Profiling / automatisierte Entscheidungen (Art. 22 DSGVO)")
    report.add_paragraph(f"<i>{terms_of_use_result.explanation_profiling}</i>")

    # Check amendment clauses
    report.add_separator()
    if terms_of_use_result.amendment_clauses:
        report.add_success("Änderungsklauseln")
    else:
        report.add_failure("Änderungsklauseln")
    report.add_paragraph(f"<i>{terms_of_use_result.explanation_amendment_clauses}</i>")

    # Check liability clauses
    report.add_separator()
    if terms_of_use_result.liability_clauses:
        report.add_success("Haftungsklauseln")
    else:
        report.add_failure("Haftungsklauseln")
    report.add_paragraph(f"<i>{terms_of_use_result.explanation_liability_clauses}</i>")

    # Overall result
    report.add_separator()
    if terms_of_use_result.is_valid:
        report.add_success(
            "Kriterium erfüllt: Die Nutzungsbedingungen enthalten alle erforderlichen Informationen."
        )
    else:
        report.add_failure(
            "Kriterium nicht erfüllt: Die Nutzungsbedingungen enthalten nicht alle erforderlichen Informationen."
        )


def add_rds_agb_369_to_report(
    report: Report,
    terms_of_use_result_processor_only: TermsOfUseProcessorOnlyCheckResult,
):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-AGB-369"])

    # Check written agreement
    report.add_separator()
    if terms_of_use_result_processor_only.written_agreement:
        report.add_success("Ausdrückliche Vereinbarung zur Auftragsverarbeitung")
    else:
        report.add_failure("Ausdrückliche Vereinbarung zur Auftragsverarbeitung")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_written_agreement}</i>"
    )

    # Check processing instructions
    report.add_separator()
    if terms_of_use_result_processor_only.processing_instructions:
        report.add_success("Verarbeitung nur auf dokumentierte Weisung")
    else:
        report.add_failure("Verarbeitung nur auf dokumentierte Weisung")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_processing_instructions}</i>"
    )

    # Check confidentiality
    report.add_separator()
    if terms_of_use_result_processor_only.confidentiality:
        report.add_success("Vertraulichkeitspflicht des Personals")
    else:
        report.add_failure("Vertraulichkeitspflicht des Personals")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_confidentiality}</i>"
    )

    # Check security measures
    report.add_separator()
    if terms_of_use_result_processor_only.security_measures:
        report.add_success("Technische und organisatorische Maßnahmen")
    else:
        report.add_failure("Technische und organisatorische Maßnahmen")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_security_measures}</i>"
    )

    # Check subprocessors
    report.add_separator()
    if terms_of_use_result_processor_only.subprocessors:
        report.add_success("Regelungen zu Unterauftragsverarbeitern")
    else:
        report.add_failure("Regelungen zu Unterauftragsverarbeitern")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_subprocessors}</i>"
    )

    # Check data subject rights support
    report.add_separator()
    if terms_of_use_result_processor_only.data_subject_rights_support:
        report.add_success("Unterstützung bei Betroffenenrechten")
    else:
        report.add_failure("Unterstützung bei Betroffenenrechten")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_data_subject_rights_support}</i>"
    )

    # Check security support
    report.add_separator()
    if terms_of_use_result_processor_only.security_support:
        report.add_success("Unterstützung bei Sicherheitsmaßnahmen")
    else:
        report.add_failure("Unterstützung bei Sicherheitsmaßnahmen")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_security_support}</i>"
    )

    # Check deletion/return
    report.add_separator()
    if terms_of_use_result_processor_only.deletion_return:
        report.add_success("Löschung oder Rückgabe der Daten")
    else:
        report.add_failure("Löschung oder Rückgabe der Daten")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_deletion_return}</i>"
    )

    # Check audit rights
    report.add_separator()
    if terms_of_use_result_processor_only.audit_rights:
        report.add_success("Nachweis- und Kontrollrechte")
    else:
        report.add_failure("Nachweis- und Kontrollrechte")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_audit_rights}</i>"
    )

    # Check liability limitations
    report.add_separator()
    if terms_of_use_result_processor_only.liability_limitations:
        report.add_success("Angemessene Haftungsregelungen")
    else:
        report.add_failure("Angemessene Haftungsregelungen")
    report.add_paragraph(
        f"<i>{terms_of_use_result_processor_only.explanation_liability_limitations}</i>"
    )

    # Overall result
    report.add_separator()
    if terms_of_use_result_processor_only.is_valid:
        report.add_success(
            "Kriterium erfüllt: Die Auftragsverarbeitungsvereinbarung enthält alle erforderlichen Informationen."
        )
    else:
        report.add_failure(
            "Kriterium nicht erfüllt: Die Auftragsverarbeitungsvereinbarung enthält nicht alle erforderlichen Informationen."
        )


def add_rds_vin_354_to_report(report: Report, image_content_result: ContentCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-VIN-354"])

    report.add_separator()
    if image_content_result.is_youth_secure:
        report.add_success("Das Angebot ist jugendmedienschutzrechtlich unbedenklich.")
    else:
        report.add_failure("Das Angebot ist jugendmedienschutzrechtlich bedenklich.")

    report.add_paragraph(f"<i>{image_content_result.youth_protection_explanation}</i>")


def add_rds_wer_384_to_report(report: Report, image_content_result: ContentCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-WER-384"])

    report.add_separator()
    if not image_content_result.has_ads:
        report.add_success("Das digitale Bildungsangebot ist werbefrei.")
    else:
        report.add_failure("Das digitale Bildungsangebot enthält Werbung.")

    report.add_paragraph(f"<i>{image_content_result.ads_explanation}</i>")


def add_rds_wer_385_to_report(report: Report, image_content_result: ContentCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["RDS-WER-385"])

    report.add_separator()
    if not image_content_result.has_ads:
        report.add_success(
            "Aus dem Angebot wird nicht auf Zielseiten mit Werbung verlinkt."
        )
    else:
        report.add_failure("Aus dem Angebot wird auf Zielseiten mit Werbung verlinkt.")

    report.add_paragraph(f"<i>{image_content_result.ads_explanation}</i>")


def add_its_enc_359_to_report(report: Report, encryption_result: EncryptionCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["ITS-ENC-359"])

    report.add_separator()
    if encryption_result.https_available and not encryption_result.http_disabled:
        report.add_success("HTTPS ist verfügbar und HTTP ist deaktiviert")
        report.add_paragraph(
            "<i>Die Website ist ausschließlich über https:// aufrufbar.</i>"
        )
    else:
        report.add_failure("HTTPS ist nicht ausschließlich konfiguriert")
        if not encryption_result.https_available:
            report.add_paragraph("<i>Die Website ist nicht über HTTPS verfügbar.</i>")
        if encryption_result.http_disabled:
            report.add_paragraph(
                "<i>Die Website ist noch über unverschlüsseltes HTTP erreichbar.</i>"
            )
        report.add_paragraph(
            "<i>Die Website ist nicht ausschließlich über https:// aufrufbar.</i>"
        )


def add_its_enc_360_to_report(report: Report, encryption_result: EncryptionCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["ITS-ENC-360"])

    report.add_separator()
    if encryption_result.http_to_https_redirect:
        report.add_success("HTTP zu HTTPS Umleitung ist konfiguriert")
        report.add_paragraph(
            "<i>Es sind Umleitungen von http auf https konfiguriert.</i>"
        )
    else:
        report.add_failure("Keine HTTP zu HTTPS Umleitung konfiguriert")
        report.add_paragraph(
            "<i>Es sind keine Umleitungen von http auf https konfiguriert.</i>"
        )


def add_its_enc_361_to_report(report: Report, encryption_result: EncryptionCheckResult):
    add_vidis_criterion_to_report(report, VIDIS_CRITERIA["ITS-ENC-361"])

    report.add_separator()
    if encryption_result.tls_ssl_secure:
        report.add_success("Veraltete TLS/SSL-Protokolle werden abgelehnt")
        report.add_paragraph("<i>Veraltete TLS/SSL-Protokolle werden abgelehnt.</i>")
    else:
        report.add_failure("Veraltete TLS/SSL-Protokolle werden nicht abgelehnt")
        report.add_paragraph(
            "<i>Veraltete TLS/SSL-Protokolle werden nicht abgelehnt.</i>"
        )
        report.add_paragraph(
            "<i>Dies stellt ein Sicherheitsrisiko dar, da ältere Protokolle bekannte Schwachstellen aufweisen.</i>"
        )


def generate_report(url: str, input_name: str, output_name: str):
    """Generate a VIDIS report from classification results."""
    input_dir = f"classification_results/{input_name}"

    report_dir = f"reports/{output_name}"
    report_path = f"{report_dir}/report.pdf"

    if not os.path.exists(report_dir):
        os.makedirs(report_dir, exist_ok=True)

    cookie_results = CookieCheckResult.model_validate_json(
        open(f"{input_dir}/cookie_results.json").read()
    )
    tracking_issues = TrackingPixelIssues.model_validate_json(
        open(f"{input_dir}/tracking_issues.json").read()
    )
    local_storage_results = StorageCheckResult.model_validate_json(
        open(f"{input_dir}/local_storage_results.json").read()
    )
    session_storage_results = StorageCheckResult.model_validate_json(
        open(f"{input_dir}/session_storage_results.json").read()
    )
    privacy_policy_result = PrivacyPolicyCheckResult.model_validate_json(
        open(f"{input_dir}/privacy_policy_result.json").read()
    )
    imprint_result = ImprintCheckResult.model_validate_json(
        open(f"{input_dir}/imprint_result.json").read()
    )
    terms_of_use_result = TermsOfUseCheckResult.model_validate_json(
        open(f"{input_dir}/terms_of_use_result.json").read()
    )
    terms_of_use_result_processor_only = (
        TermsOfUseProcessorOnlyCheckResult.model_validate_json(
            open(f"{input_dir}/terms_of_use_result_processor_only.json").read()
        )
    )
    encryption_result = EncryptionCheckResult.model_validate_json(
        open(f"{input_dir}/encryption_result.json").read()
    )
    image_content_result = ContentCheckResult.model_validate_json(
        open(f"{input_dir}/image_content_result.json").read()
    )

    report = Report(report_path)

    report.add_title("Vidis Report")
    report.add_paragraph(f"Report generiert für {url}")
    report.add_paragraph(f"Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.add_paragraph(
        "Dieser Report wurde automatisch generiert und ersetzt keine Rechtsberatung oder offizielle Prüfung durch VIDIS."
    )
    report.add_page_break()

    add_rds_cuc_371_to_report(report, cookie_results)
    add_rds_cuc_372_to_report(report, cookie_results)
    add_rds_cuc_373_to_report(report, tracking_issues)
    add_rds_cuc_374_to_report(report, local_storage_results, session_storage_results)
    add_rds_dso_383_to_report(report, privacy_policy_result)
    add_rds_ipf_364_to_report(report)
    add_rds_ipf_365_to_report(report)
    add_rds_ipf_366_to_report(report, imprint_result)
    add_rds_ipf_367_to_report(report, privacy_policy_result)
    add_rds_agb_368_to_report(report, terms_of_use_result)
    add_rds_agb_369_to_report(report, terms_of_use_result_processor_only)
    add_rds_vin_354_to_report(report, image_content_result)
    add_rds_wer_384_to_report(report, image_content_result)
    add_rds_wer_385_to_report(report, image_content_result)
    add_its_enc_359_to_report(report, encryption_result)
    add_its_enc_360_to_report(report, encryption_result)
    add_its_enc_361_to_report(report, encryption_result)

    report.generate_pdf()


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "--input_name",
        help="Name of the input directory in the ./classification_results directory.",
        type=str,
        required=True,
    )
    args.add_argument(
        "--output_name",
        help="Name of the output directory in the ./reports directory. The report will be saved as report.pdf in this directory.",
        type=str,
        required=True,
    )
    args = args.parse_args()

    generate_report(args.input_name, args.output_name)
