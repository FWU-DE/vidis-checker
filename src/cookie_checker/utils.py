from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    """
    Extract domain from a URL.
    If URL doesn't have a scheme (http:// or https://), https:// is added
    by default.

    Args:
        url (str): URL to parse

    Returns:
        str: Domain extracted from the URL
    """
    # Make sure URL has scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Parse domain from URL
    parsed_url = urlparse(url)
    return parsed_url.netloc
