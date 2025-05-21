from typing import List, Union

from pydantic import BaseModel

from ..models.models import Cookie

from .util import generate_structured_completion

from .cookie_db import COOKIE_DATABASE, CookieInfo


class CookieDbCheckResult(BaseModel):
    cookie_name: str
    cookie: Cookie
    cookie_info: CookieInfo
    is_essential: bool | None


class CookieLLMResult(BaseModel):
    explanation: str
    is_essential: bool


class CookieLLMCheckResult(BaseModel):
    cookie_name: str
    cookie_details: Cookie
    is_essential: bool
    explanation: str


SingleCookieCheckResult = Union[CookieDbCheckResult, CookieLLMCheckResult]

cookie_prompt = """
We need to determine if this cookie is essential or non-essential for website functionality:

Cookie Name: $NAME
Cookie Domain: $DOMAIN
Website Purpose: $WEBSITE_PURPOSE

Essential cookies are strictly necessary for basic website functionality (like keeping users logged in or remembering items in a shopping cart).

Non-essential cookies are used for analytics, marketing, or enhanced functionality that isn't required for the basic operation of the website.

Based on this information, is this cookie essential or non-essential? Provide your classification and reasoning.
"""


class CookieCheckResult(BaseModel):
    results: List[SingleCookieCheckResult]


def get_cookie_check_results(cookies: List[Cookie]) -> CookieCheckResult:
    results: List[SingleCookieCheckResult] = []

    for cookie in cookies:
        check_result = COOKIE_DATABASE.is_cookie_essential(cookie.name)
        if check_result is None:
            prompt = (
                cookie_prompt.replace("$NAME", cookie.name)
                .replace("$DOMAIN", cookie.domain)
                .replace("$WEBSITE_PURPOSE", "TODO")
            )
            check_result = generate_structured_completion(prompt, CookieLLMResult)

            cookie_llm_check_result = CookieLLMCheckResult(
                cookie_name=cookie.name,
                cookie_details=cookie,
                is_essential=check_result.is_essential,
                explanation=check_result.explanation,
            )
            results.append(cookie_llm_check_result)
        else:
            is_essential, cookie_info = check_result

            cookie_db_check_result = CookieDbCheckResult(
                cookie_name=cookie.name,
                cookie=cookie,
                cookie_info=cookie_info,
                is_essential=is_essential,
            )
            results.append(cookie_db_check_result)

    return CookieCheckResult(results=results)
