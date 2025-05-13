from .util import generate_text, read_text_from_pdf


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

Abschließend gib in einem letzten Satz an, ob die AGB insgesamt valide sind.
Schreibe nur 'True' wenn alle erforderlichen Punkte erfüllt sind, ansonsten 'False'.
Nach dieser Zeile DARF keine weitere Erklärung folgen, da wir diese Zeile automatisch auswerten werden.
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

Abschließend gib in einem letzten Satz an, ob die AGB gemäß Art. 28 DSGVO valide sind.
Schreibe nur 'True' wenn alle erforderlichen Punkte erfüllt sind, ansonsten 'False'.
Nach dieser Zeile DARF keine weitere Erklärung folgen, da wir diese Zeile automatisch auswerten werden.
"""

def get_terms_of_use_check_prompt(terms_of_use_text: str, processor_only: bool = False) -> str:
    if processor_only:
        return terms_of_use_processor_only_prompt.replace("$TERMS_OF_USE", terms_of_use_text)
    return terms_of_use_check_prompt.replace("$TERMS_OF_USE", terms_of_use_text)


def check_terms_of_use_from_text(terms_of_use_text: str, processor_only: bool = False) -> tuple[bool, str]:
    prompt = get_terms_of_use_check_prompt(terms_of_use_text, processor_only)
    response = generate_text(prompt)

    # Extract the last sentence to determine if the terms of use are complete
    lines = response.strip().split("\n")
    last_line = lines[-1].strip()

    is_complete = "True" in last_line

    return is_complete, response


def check_terms_of_use(file_path: str, processor_only: bool = False) -> tuple[bool, str]:
    terms_of_use_text = read_text_from_pdf(file_path)
    return check_terms_of_use_from_text(terms_of_use_text, processor_only)


if __name__ == "__main__":
    result, explanation = check_terms_of_use(
        "tmp/schooltogo.de_legal/terms_of_use.pdf",
        processor_only=False
    )
    print(f"Nutzungsbedingungen vollständig: {result}")
    print(explanation)