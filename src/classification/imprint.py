from .util import (
    generate_completion,
    read_text_from_pdf,
    generate_structured_completion,
)
from typing import Type, TypeVar, List
from pydantic import BaseModel


class ImprintCheckResult(BaseModel):
    explanation_name_and_address_present: str
    name_and_address_present: bool
    explanation_legal_form_present: str
    legal_form_present: bool
    explanation_contact_info_present: str
    contact_info_present: bool
    explanation_supervisory_authority_present: str
    supervisory_authority_present: bool
    explanation_register_info_present: str
    register_info_present: bool
    explanation_tax_id_present: str
    tax_id_present: bool
    explanation_audiovisual_media_info_present: str
    audiovisual_media_info_present: bool
    explanation_legal_reference_current: str
    legal_reference_current: bool


imprint_check_prompt = """
Prüfe die Richtigkeit des Impressums.

Es müssen insbesondere folgende Punkte geprüft werden:

1. Den Namen und die Anschrift, unter welcher der Dienstanbieter niedergelassen ist (§ 5 Abs. 1 S. 1 DDG)

2. Bei juristischen Personen zusätzlich die Rechtsform, den Vertretungsberechtigten und, sofern Angaben über das Kapital der Gesellschaft gemacht werden, das Stamm- oder Grundkapital sowie, wenn nicht alle in Geld zu leistenden Einlagen eingezahlt sind, der Gesamtbetrag der ausstehenden Einlagen (§ 5 Abs. 1 S. 1 DDG)

3. Angaben, die eine schnelle elektronische Kontaktaufnahme und eine unmittelbare Kommunikation mit ihnen ermöglichen, einschließlich der Adresse für die elektronische Post (§ 5 Abs. 1 S. 2 DDG)

4. Soweit der Dienst im Rahmen einer Tätigkeit angeboten oder erbracht wird, die der behördlichen Zulassung bedarf, Angaben zur zuständigen Aufsichtsbehörde (§ 5 Abs. 1 S. 3 DDG)

5. Die Angabe des Handelsregisters oder ähnlicher Register, in das sie eingetragen sind, und die entsprechende Registernummer (§ 5 Abs. 1 S. 4 DDG)

6. In Fällen, in denen sie eine Umsatzsteueridentifikationsnummer oder eine Wirtschafts-Identifikationsnummer besitzen, die Angabe dieser Nummer (§ 5 Abs. 1 S. 6 DDG)

7. Bei Anbietern von audiovisuellen Mediendiensten die Angabe
a) des Mitgliedstaats, der für sie Sitzland ist oder als Sitzland gilt sowie
b) der zuständigen Regulierungs- und Aufsichtsbehörden. (§ 5 Abs. 1 S. 8 DDG)

8. Falls das Impressum sich noch auf das TMG bezieht, weise den Nutzer darauf hin, dass das TMG am 14. Mai 2024 außer Kraft getreten ist und durch das Digitale-Dienste-Gesetz (DDG) ersetzt wurde.

Analysiere das Impressum und gib für jeden Punkt an, ob er erfüllt ist oder nicht.
Im nachfolgenden Text findest du das Impressum.

Text:
$IMPRINT
"""


def get_imprint_check_prompt(imprint_text: str) -> str:
    return imprint_check_prompt.replace("$IMPRINT", imprint_text)


def check_imprint_from_text(imprint_text: str) -> ImprintCheckResult:
    prompt = get_imprint_check_prompt(imprint_text)

    return generate_structured_completion(prompt, ImprintCheckResult)


def check_imprint(file_path: str) -> ImprintCheckResult:
    imprint_text = read_text_from_pdf(file_path)
    return check_imprint_from_text(imprint_text)


if __name__ == "__main__":
    result = check_imprint("tmp/schooltogo.de_legal/impressum.pdf")
    print(result)
