from .util import (
    generate_structured_completion,
    read_text_from_pdf,
)
from pydantic import BaseModel


class PrivacyPolicyCheckResult(BaseModel):
    explanation_responsible_entity_present: str
    responsible_entity_present: bool
    explanation_dpo_present: str
    dpo_present: bool
    explanation_processing_purposes_present: str
    processing_purposes_present: bool
    explanation_legal_basis_present: str
    legal_basis_present: bool
    explanation_recipients_present: str
    recipients_present: bool
    explanation_storage_duration_present: str
    storage_duration_present: bool
    explanation_data_subject_rights_present: str
    data_subject_rights_present: bool
    explanation_data_provision_requirements_present: str
    data_provision_requirements_present: bool
    explanation_automated_decision_making_info_present: str
    automated_decision_making_info_present: bool


privacy_policy_check_prompt = """
Prüfe die Richtigkeit der Datenschutzerklärung.

Es müssen insbesondere folgende Punkte geprüft werden:

1. Der Name und die Kontaktdaten des Verantwortlichen sowie gegebenenfalls seines Vertreters sind enthalten. (Art. 13 Abs. 1 lit. a)

2. Die Kontaktdaten des Datenschutzbeauftragten sind enthalten, falls ein Datenschutzbeauftragter bestellt wurde. (Art. 13 Abs. 1 lit. b)

3. Die Zwecke, für die die personenbezogenen Daten verarbeitet werden sollen, sind genannt. (Art. 13 Abs. 1 lit. c)

4. Die Rechtsgrundlage für die Verarbeitung der personenbezogenen Daten ist genannt. (Art. 13 Abs. 1 lit. c)

5. Die Empfänger oder Kategorien von Empfängern der personenbezogenen Daten sind genannt. (Art. 13 Abs. 1 lit. e)

6. Die Dauer, für die die personenbezogenen Daten gespeichert werden oder, falls dies nicht möglich ist, die Kriterien für die Festlegung dieser Dauer sind genannt (Art. 13 Abs. 2 lit. a).

7. Die Betroffenenrechte sind genannt (Art. 13 Abs. 2 lit. b-d):

7. 1. Das Bestehen eines Rechts auf Auskunft seitens des Verantwortlichen über die betreffenden personenbezogenen Daten

7. 2. Das Bestehen eines Rechts auf Berichtigung

7. 3. Das Bestehen eines Rechts auf Löschung

7. 4. Das Bestehen eines Rechts auf Einschränkung der Verarbeitung

7. 5. Das Bestehen eines Widerspruchsrechts gegen die Verarbeitung

7. 6. Das Bestehen eines Rechts auf Datenübertragbarkeit

7. 7. Wenn die Verarbeitung auf Art. 6 Abs. 1 lit. a beruht, das Bestehen eines Rechts, die Einwilligung jederzeit zu widerrufen, ohne dass die Rechtmäßigkeit der aufgrund der Einwilligung bis zum Widerruf erfolgten Verarbeitung berührt wird

7. 8. Das Bestehen eines Beschwerderechts bei einer Aufsichtsbehörde

8. Ob die Bereitstellung der personenbezogenen Daten gesetzlich oder vertraglich vorgeschrieben oder für einen Vertragsabschluss erforderlich ist, ob die betroffene Person verpflichtet ist, die personenbezogenen Daten bereitzustellen, und welche mögliche Folgen die Nichtbereitstellung hätte (Art. 13 Abs. 2 lit. e)

9. Das Bestehen einer automatisierten Entscheidungsfindung einschließlich Profiling gemäß Artikel 22 Absätze 1 und 4 und – zumindest in diesen Fällen – aussagekräftige Informationen über die involvierte Logik sowie die Tragweite und die angestrebten Auswirkungen einer derartigen Verarbeitung für die betroffene Person. (Art. 13 Abs. 2 lit. f)

Analysiere die Datenschutzerklärung und gib für jeden Punkt an, ob er erfüllt ist oder nicht.
Im nachfolgenden Text findest du die Datenschutzerklärung.

Text:
$PRIVACY_POLICY
"""


def get_privacy_policy_check_prompt(privacy_policy_text: str) -> str:
    return privacy_policy_check_prompt.replace("$PRIVACY_POLICY", privacy_policy_text)


def check_privacy_policy_from_text(
    privacy_policy_text: str,
) -> PrivacyPolicyCheckResult:
    prompt = get_privacy_policy_check_prompt(privacy_policy_text)

    return generate_structured_completion(prompt, PrivacyPolicyCheckResult)


def check_privacy_policy(file_path: str) -> PrivacyPolicyCheckResult:
    privacy_policy_text = read_text_from_pdf(file_path)
    return check_privacy_policy_from_text(privacy_policy_text)


if __name__ == "__main__":
    result = check_privacy_policy("tmp/schooltogo.de_legal/privacy_policy.pdf")
    print(result)
