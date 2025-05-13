from .util import generate_text, read_text_from_pdf


imprint_check_prompt = """
Helfe dem Nutzer, die Richtigkeit des Impressums zu prüfen (bzw. helfe ihm bei der Bearbeitung des Impressums).

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

Hebe die einzelnen Punkte einzeln hervor (mit Hilfe der Textformatierung) und zeige dem Nutzer an, ob der Punkt erfüllt (✅), nicht erfüllt (❌) oder möglicherweise zu prüfen ist (⚠️).

Im nachfolgenden Text findest du das Impressum.

Text:
$IMPRINT

Abschließend gib in einem letzten Satz an, ob das Impressum insgesamt vollständig ist.
Schreibe nur 'True' wenn alle erforderlichen Angaben vorhanden sind, ansonsten 'False'.
Nach dieser Zeile DARF keine weitere Erklärung folgen, da wir diese Zeile automatisch auswerten werden.
"""


def get_imprint_check_prompt(imprint_text: str) -> str:
    return imprint_check_prompt.replace("$IMPRINT", imprint_text)


def check_imprint_from_text(imprint_text: str) -> tuple[bool, str]:
    prompt = get_imprint_check_prompt(imprint_text)
    response = generate_text(prompt)

    # Extract the last sentence to determine if the imprint is complete
    lines = response.strip().split("\n")
    last_line = lines[-1].strip()

    is_complete = "True" in last_line

    return is_complete, response


def check_imprint(file_path: str) -> tuple[bool, str]:
    imprint_text = read_text_from_pdf(file_path)
    return check_imprint_from_text(imprint_text)


if __name__ == "__main__":
    result, explanation = check_imprint("tmp/schooltogo.de_legal/impressum.pdf")
    print(f"Impressum vollständig: {result}")
    print(explanation)
