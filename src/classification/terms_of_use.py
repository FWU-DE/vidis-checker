import os
from .util import (
    read_text_from_pdf,
    generate_structured_completion,
)
from pydantic import BaseModel


class TermsOfUseCheckResult(BaseModel):
    explanation_transparency_and_lawfulness: str
    transparency_and_lawfulness: bool
    explanation_purpose_limitation: str
    purpose_limitation: bool
    explanation_data_minimization: str
    data_minimization: bool
    explanation_consent_clauses: str
    consent_clauses: bool
    explanation_cookie_tracking_consent: str
    cookie_tracking_consent: bool
    explanation_data_subject_rights: str
    data_subject_rights: bool
    explanation_objection_and_opt_out: str
    objection_and_opt_out: bool
    explanation_third_country_transfers: str
    third_country_transfers: bool
    explanation_processors: str
    processors: bool
    explanation_profiling: str
    profiling: bool
    explanation_amendment_clauses: str
    amendment_clauses: bool
    explanation_liability_clauses: str
    liability_clauses: bool
    is_valid: bool


class TermsOfUseProcessorOnlyCheckResult(BaseModel):
    explanation_written_agreement: str
    written_agreement: bool
    explanation_processing_instructions: str
    processing_instructions: bool
    explanation_confidentiality: str
    confidentiality: bool
    explanation_security_measures: str
    security_measures: bool
    explanation_subprocessors: str
    subprocessors: bool
    explanation_data_subject_rights_support: str
    data_subject_rights_support: bool
    explanation_security_support: str
    security_support: bool
    explanation_deletion_return: str
    deletion_return: bool
    explanation_audit_rights: str
    audit_rights: bool
    explanation_liability_limitations: str
    liability_limitations: bool
    is_valid: bool


terms_of_use_check_prompt = """
Analysiere die vorliegenden Nutzungs­bedingungen / AGB. Gehe die folgenden Prüfpunkte nacheinander durch und gib zu jedem Punkt an, ob die Klauseln konform sind oder datenschutz­rechtliche Probleme enthalten:

1. Transparenz & Rechtmäßigkeit (Art. 5 Abs. 1 lit. a DSGVO)
2. Zweckbindung (Art. 5 Abs. 1 lit. b DSGVO)
3. Daten­minimierung & Speicher­begrenzung (Art. 5 Abs. 1 lit. c + e DSGVO)
4. Einwilligungs­klauseln (Art. 7 DSGVO)
5. Cookie/Tracking-Einwilligung (§ 25 TDDDG / TTDSG)
6. Betroffenenrechte (Art. 12–23 DSGVO)
7. Widerspruchs- & Opt-out-Regelungen (Art. 21 DSGVO)
8. Drittland­übermittlungen (Art. 44 ff. DSGVO)
9. Auftrags­verarbeiter / Sub-Processors (Art. 28 DSGVO)
10. Profiling / automatisierte Entscheidungen (Art. 22 DSGVO)
11. Änderungs­klauseln
12. Haftungs- & Freistellungs­klauseln

Im nachfolgenden Text findest du die Nutzungsbedingungen / AGB.

Text:
$TERMS_OF_USE
"""

terms_of_use_processor_only_prompt = """
Analysiere die vorliegenden Nutzungs­bedingungen / AGB und prüfe ausschließlich deren Regelungen zur Auftrags­verarbeitung gemäß Art. 28 DSGVO. Gehe die folgenden Prüfpunkte nacheinander durch und gib zu jedem Punkt kurz an, ob er erfüllt ist oder ob ein datenschutz­rechtliches Problem vorliegt:

1. Besteht eine ausdrückliche (schriftliche oder elektronische) Vereinbarung zur Auftrags­verarbeitung?
2. Verarbeitung nur auf dokumentierte Weisung des Verantwortlichen (Art. 28 Abs. 3 lit. a).
3. Vertraulichkeits­pflicht des mit der Verarbeitung befassten Personals (lit. b).
4. Zusicherung geeigneter technischer und organisatorischer Sicherheits­maßnahmen nach Art. 32 (lit. c).
5. Bedingungen für Unter­auftrags­verarbeiter: vorherige Genehmigung / Option zum Widerspruch + Weitergabe gleicher Schutzpflichten (lit. d + Abs. 4).
6. Unterstützung des Verantwortlichen bei Betroffenen­rechten (lit. e).
7. Unterstützung bei Sicherheit / Meldung von Datenschutz­verletzungen sowie bei Datenschutz-Folgenabschätzungen (lit. f).
8. Verpflichtung zur Löschung oder Rückgabe sämtlicher personenbezogener Daten nach Ende der Verarbeitung (lit. g).
9. Pflicht zur Bereitstellung aller nötigen Informationen und Ermöglichung von Audits / Inspektionen (lit. h).
10. Keine Klauseln, die gesetzliche Haftungspflichten oder Aufsichts­rechte unzulässig einschränken bzw. auf den Verantwortlichen abwälzen.

Text:
$TERMS_OF_USE
"""


def get_terms_of_use_check_prompt(
    terms_of_use_text: str, processor_only: bool = False
) -> str:
    if processor_only:
        return terms_of_use_processor_only_prompt.replace(
            "$TERMS_OF_USE", terms_of_use_text
        )
    return terms_of_use_check_prompt.replace("$TERMS_OF_USE", terms_of_use_text)


def check_terms_of_use_from_text(terms_of_use_text: str, processor_only: bool = False):
    prompt = get_terms_of_use_check_prompt(terms_of_use_text, processor_only)

    if processor_only:
        return generate_structured_completion(
            prompt, TermsOfUseProcessorOnlyCheckResult
        )
    else:
        return generate_structured_completion(prompt, TermsOfUseCheckResult)


def check_terms_of_use(file_path: str, processor_only: bool = False):
    if not os.path.exists(file_path):
        if processor_only:
            # Return a result with all bools set to False and explanations indicating the file was not found
            return TermsOfUseProcessorOnlyCheckResult(
                explanation_written_agreement="Die AGBs konnten nicht gefunden werden",
                written_agreement=False,
                explanation_processing_instructions="Die AGBs konnten nicht gefunden werden",
                processing_instructions=False,
                explanation_confidentiality="Die AGBs konnten nicht gefunden werden",
                confidentiality=False,
                explanation_security_measures="Die AGBs konnten nicht gefunden werden",
                security_measures=False,
                explanation_subprocessors="Die AGBs konnten nicht gefunden werden",
                subprocessors=False,
                explanation_data_subject_rights_support="Die AGBs konnten nicht gefunden werden",
                data_subject_rights_support=False,
                explanation_security_support="Die AGBs konnten nicht gefunden werden",
                security_support=False,
                explanation_deletion_return="Die AGBs konnten nicht gefunden werden",
                deletion_return=False,
                explanation_audit_rights="Die AGBs konnten nicht gefunden werden",
                audit_rights=False,
                explanation_liability_limitations="Die AGBs konnten nicht gefunden werden",
                liability_limitations=False,
                is_valid=False,
            )
        else:
            # Return a result with all bools set to False and explanations indicating the file was not found
            return TermsOfUseCheckResult(
                explanation_transparency_and_lawfulness="Die AGBs konnten nicht gefunden werden",
                transparency_and_lawfulness=False,
                explanation_purpose_limitation="Die AGBs konnten nicht gefunden werden",
                purpose_limitation=False,
                explanation_data_minimization="Die AGBs konnten nicht gefunden werden",
                data_minimization=False,
                explanation_consent_clauses="Die AGBs konnten nicht gefunden werden",
                consent_clauses=False,
                explanation_cookie_tracking_consent="Die AGBs konnten nicht gefunden werden",
                cookie_tracking_consent=False,
                explanation_data_subject_rights="Die AGBs konnten nicht gefunden werden",
                data_subject_rights=False,
                explanation_objection_and_opt_out="Die AGBs konnten nicht gefunden werden",
                objection_and_opt_out=False,
                explanation_third_country_transfers="Die AGBs konnten nicht gefunden werden",
                third_country_transfers=False,
                explanation_processors="Die AGBs konnten nicht gefunden werden",
                processors=False,
                explanation_profiling="Die AGBs konnten nicht gefunden werden",
                profiling=False,
                explanation_amendment_clauses="Die AGBs konnten nicht gefunden werden",
                amendment_clauses=False,
                explanation_liability_clauses="Die AGBs konnten nicht gefunden werden",
                liability_clauses=False,
                is_valid=False,
            )

    terms_of_use_text = read_text_from_pdf(file_path)
    return check_terms_of_use_from_text(terms_of_use_text, processor_only)


if __name__ == "__main__":
    result = check_terms_of_use(
        "tmp/schooltogo.de_legal/terms_of_use.pdf", processor_only=False
    )
    print(f"Nutzungsbedingungen vollständig: {result.is_valid}")
    print(result)
