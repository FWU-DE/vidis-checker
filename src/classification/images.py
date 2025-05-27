from typing import List
from pydantic import BaseModel

from .util import analyze_image


class ContentCheckResult(BaseModel):
    ads_explanation: str
    has_ads: bool
    youth_protection_explanation: str
    is_youth_secure: bool

prompt = """
Analysiere dieses Bild und führe zwei Prüfungen durch:

1. WERBEERKENNUNG:
Bestimme, ob es Werbung oder Werbeinhalte enthält.
Achte auf:
- Banner-Werbung
- Pop-up-Werbung
- Gesponserte Inhalte
- Produktwerbung
- Marketing-Nachrichten
- Kommerzielle Banner
- Werbe-Overlays

2. JUGENDMEDIENSCHUTZ:
Bestimme, ob der Inhalt für Jugendliche geeignet ist und nicht gegen demokratische Grundsätze verstößt.
Prüfe auf Inhalte, die folgendes enthalten oder fördern:
- Extremismus
- Rassismus
- Gewaltverherrlichung
- Pornografie
- Diskriminierung
- Verletzung von Persönlichkeitsrechten
- Fundamentalismus
- Inhalte, die demokratischen, verfassungsrechtlichen Grundsätzen widersprechen

Für jede Prüfung gib eine kurze Erklärung deiner Begründung und bestimme:
- has_ads: ob Werbung gefunden wurde
- is_youth_secure: ob der Inhalt für Jugendliche sicher ist (true wenn sicher, false wenn problematisch)
"""

def check_page_content(image_path: str) -> ContentCheckResult:
    """
    Analyze an image to detect advertisements and check youth protection compliance.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        ContentCheckResult: Result containing ad detection and youth protection analysis
    """    
    return analyze_image(image_path, ContentCheckResult, prompt)

if __name__ == "__main__":
    result = check_page_content("agent_results/run_https_schooltogo.de_20250527_121048_6a5f9e65-024b-499a-be91-660f983c7929/images/step_000.png")
    print(result.model_dump_json(indent=4))
