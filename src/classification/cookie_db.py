import os
import json
from dataclasses import dataclass
from typing import Dict, Literal, Tuple


@dataclass
class CookieInfo:
    """Data class to store cookie information from the database"""

    id: str
    category: Literal["Analytics", "Functional", "Marketing", "Security"]
    cookie: str
    domain: str
    description: str
    retention_period: str
    data_controller: str
    privacy_link: str
    wildcard_match: str
    platform: str


class CookieDatabase:
    def __init__(self, db_path: str = None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = (
            db_path if db_path else os.path.join(current_dir, "cookie_db.json")
        )
        self.cookie_db = self.load_cookie_database()

    def load_cookie_database(self) -> Dict[str, CookieInfo]:
        """
        Load cookie information from the database file

        Args:
            db_path: Path to the cookie database JSON file

        Returns:
            Dictionary mapping cookie names to CookieInfo objects
        """
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            cookie_db: Dict[str, CookieInfo] = {}

            for service, cookies in data.items():
                for cookie_data in cookies:
                    cookie_name = cookie_data.get("cookie", "")
                    if cookie_name:
                        cookie_info = CookieInfo(
                            id=cookie_data.get("id", ""),
                            category=cookie_data.get("category", ""),
                            cookie=cookie_name,
                            domain=cookie_data.get("domain", ""),
                            description=cookie_data.get("description", ""),
                            retention_period=cookie_data.get("retentionPeriod", ""),
                            data_controller=cookie_data.get("dataController", ""),
                            privacy_link=cookie_data.get("privacyLink", ""),
                            wildcard_match=cookie_data.get("wildcardMatch", ""),
                            platform=service,
                        )
                        cookie_db[cookie_name] = cookie_info

            return cookie_db

        except Exception as e:
            print(f"Error loading cookie database: {e}")
            return {}

    def get_cookie_info(self, cookie_name: str) -> CookieInfo:
        return self.cookie_db.get(cookie_name, None)

    def is_cookie_essential(self, cookie_name: str) -> Tuple[bool, CookieInfo] | None:
        cookie_info = self.get_cookie_info(cookie_name)

        if cookie_info is None:
            return None

        category = cookie_info.category

        if category in ["Functional", "Security"]:
            return True, cookie_info
        elif category in ["Analytics", "Marketing"]:
            return False, cookie_info
        else:
            return None


COOKIE_DATABASE = CookieDatabase()
