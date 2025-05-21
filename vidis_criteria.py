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

VIDIS_CRITERIA = {
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
        code="RDS-CUC-375",
        name="Informationen auf der Endeinrichtung des Endnutzers",
        description=rds_cuc_375_text,
    ),
    "RDS-CUC-376": VidisCriterion(
        code="RDS-CUC-376", name="Browserfingerprints", description=rds_cuc_376_text
    ),
    "RDS-CUC-377": VidisCriterion(
        code="RDS-CUC-377",
        name="Trackingmechanismen zu nicht pädagogischen Zwecken",
        description=rds_cuc_377_text,
    ),
    "RDS-CUC-453": VidisCriterion(
        code="RDS-CUC-453",
        name="Beschreibung aller Cookies",
        description=rds_cuc_453_text,
    ),
    "RDS-DEV-380": VidisCriterion(
        code="RDS-DEV-380",
        name="Datenerhebung und -verarbeitung",
        description=rds_dev_380_text,
    ),
    "RDS-DEV-381": VidisCriterion(
        code="RDS-DEV-381",
        name="Umgang mit Daten nach Beendigung der Zusammenarbeit",
        description=rds_dev_381_text,
    ),
    "RDS-DEV-466": VidisCriterion(
        code="RDS-DEV-466",
        name="Sichere Datenverarbeitung",
        description=rds_dev_466_text,
    ),
    "RDS-DSO-383": VidisCriterion(
        code="RDS-DSO-383",
        name="Benennung eines Datenschutzbeauftragten",
        description=rds_dso_383_text,
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
        name="Nutzungsbedingungen/AGB: Datenschutzkonform",
        description=rds_agb_368_text,
    ),
    "RDS-AGB-369": VidisCriterion(
        code="RDS-AGB-369",
        name="Nutzungsbedingungen/AGB: AVV-konform",
        description=rds_agb_369_text,
    ),
}
