login_task_prompt = """
1. Navigate to the login button (usually called something like "Anmelden" or "Login")
2. Select "Login with Vidis" (which is a German SSO provider)
3. You will now be redirected to the Vidis Login page containing a text field where you 
   need to enter the Landesportal/Schulportal.
   Here you should enter the text "Test Landesportal".
4. A dropdown will appear containing "Test Landesportal".
   Click the "Test Landesportal" entry.
5. Now click the blue button "Sichere Anmeldung über Test Landesportal"
   You will now be redirected to the Vidis login page.
6. Login with the credentials: 
    * username: VIDIS_USERNAME
    * password: VIDIS_PASSWORD
    
"""


def get_task_prompt(pages_to_visit: int = 10) -> str:
    """
    Generate the legal content task prompt with the specified number of pages to visit.

    Args:
        pages_to_visit: Number of pages the agent should browse

    Returns:
        The complete task prompt with the configured number of pages
    """
    return (
        login_task_prompt
        + f"""

Afterwards:
Begin with searching for legal pages on the website, followed by a general browsing phase.

Step 1: Search for Legal Pages (Datenschutz, Impressum, AGB)
------------------------------------------------------------------
Look for something like "Datenschutz" (Privacy Policy), "Impressum" (Legal Notice), or "AGB" (Terms and Conditions).
These are often located in the header or footer of the page or in the settings menu.

You have 3 options:

1. If found:
    - Click on each (Datenschutz, Impressum, AGB) and save the entire content of each page as a PDF in the current task folder.
    - Use the action `save_page_as_pdf` with one of the following labels: `privacy_policy`, `imprint`, or `terms_of_use`.

2. If not found:
    - Navigate through the website using menus, links, or buttons to look for them.
    - Continue searching up to 3 levels deep into the website if necessary.

3. Cookie Banner:
    - If a cookie banner appears asking you to accept or decline cookies:
        a. Call the `cookie_handler` function.
        b. Afterwards, explicitly decline cookies (e.g., "Alle ablehnen", "Ablehnen").

Step 2: Browse the Website
------------------------------
Once legal pages have been handled or thoroughly searched for, continue browsing the website to get a general overview:

- Click on different visible menu items, homepage sections, or internal links.
- Visit key pages that are relevant. Interactions with footer elements are most likely not relevant.
- Explore at least a total of {pages_to_visit} unique internal pages, including legal pages.
- Avoid repeatedly visiting the same pages or looping.

Step 3: Completion Condition
-------------------------------
You are done with this task if both conditions are met:
- You have saved available legal pages (Datenschutz, Impressum, AGB)
AND ALSO:
- You have browsed at least {pages_to_visit} total unique pages.

"""
    )
