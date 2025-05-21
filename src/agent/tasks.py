import os
from typing import Optional

login_task_prompt = """
1. Navigate to the login button (usually called something like "Anmelden" or "Login")
2. Select "Login with Vidis" (which is a German SSO provider)
3. You will now be redirected to the Vidis Login page containing a text field where you need to enter the Landesportal/Schulportal.
Here you should enter the text "Test Landesportal".
4. A dropdown will appear containing "Test Landesportal".
Click the "Test Landesportal" entry.
5. Now click the blue button "Sichere Anmeldung über Test Landesportal"
You will now be redirected to the Vidis login page.
6. Login with the credentials: 
    * username: $USERNAME
    * password: $PASSWORD
"""


legal_content_task_prompt = (
    login_task_prompt
    + """
Afterwards:
Look for something like "Datenschutz" (Privacy Policy) or "Impressum" (Legal Notice) or 'AGB' (Nutzungsbedingungen/ Terms and Conditions/ Terms of Use) on the website:
Start by browsing the website.
Try to find links or sections labeled "Datenschutz" (Privacy Policy), "Impressum" (Legal Notice) and 'AGB'(Nutzungsbedingungen/ Terms and Conditions/ Terms of Use).
These are usually located at the top or bottom of the page, so you might need to scroll to the bottom of the page.

YOU HAVE 3 Options: 

1. If found:
    Click on each (Datenschutz, Impressum, AGB) and save the entire content of each page as pdf in the current task folder (use the action 'save_page_as_pdf' with either 'privacy_policy', 'imprint' or 'terms_of_use').

2. If not found:
    Navigate through the website by clicking through pages or menus or scrolling to locate them.

3. Cookie Banner:
    If a cookie banner appears asking you to determine cookies settings like accept (akzeptieren/alle akzeptieren etc.) or decline (ablehnen/ alle ablehnen) cookies, call the cookie_handler function and AFTERWARDS in the next step decline the cookies.
    
NEVER:
- use the action to google or search for something
"""
)

student_task_prompt = (
    login_task_prompt
    + """
Afterwards:
Act like a normal student that explores the website.
Navigate through the website by clicking through pages or menus that are relevant and interesting for a student. 

If a cookie banner appears asking you to determine cookies settings like accept (akzeptieren/alle akzeptieren etc.) or decline (ablehnen/ alle ablehnen) cookies, call the cookie_handler function and AFTERWARDS in the next step decline the cookies.
    
NEVER:
- use the action to google or search for something
"""
)

teacher_task_prompt = (
    login_task_prompt
    + """
Afterwards:
Act like a teacher that uses the website. Navigate through the website by clicking through pages or menus that are relevant and interesting for a teacher. 

If a cookie banner appears asking you to determine cookies settings like accept (akzeptieren/alle akzeptieren etc.) or decline (ablehnen/ alle ablehnen) cookies, call the cookie_handler function and AFTERWARDS in the next step decline the cookies.
    
NEVER:
- use the action to google or search for something
"""
)

register_task_prompt = """
Instructions:
You try to register on the website. The goal is to navigate to the registration page. If you found it save the page as pdf in the current task folder (use the action 'save_page_as_pdf' with 'register')

If a cookie banner appears asking you to determine cookies settings like accept (akzeptieren/alle akzeptieren etc.) or decline (ablehnen/ alle ablehnen) cookies, call the cookie_handler function and AFTERWARDS in the next step decline the cookies.
        
NEVER:
- use the action to google or search for something
"""

logout_task_prompt = (
    login_task_prompt
    + """
5. Logout from the website. The goal is to navigate to the logout page. If you found it save the page as pdf in the current task folder (use the action 'save_page_as_pdf' with 'logout')

NEVER:
- use the action to google or search for something
"""
)


def inject_username_password(
    instructions: str, username: str | None = None, password: str | None = None
):
    if username is None:
        username = os.getenv("VIDIS_USERNAME")
    if password is None:
        password = os.getenv("VIDIS_PASSWORD")
    return instructions.replace("$USERNAME", username).replace("$PASSWORD", password)


class TaskTemplate:
    """Base class for task templates that can be applied to different websites"""

    def __init__(
        self,
        name,
        description="",
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.instructions = ""
        self.username = username
        self.password = password

    def __repr__(self):
        return f"TaskTemplate(name={self.name}, description={self.description})"


class LoginTask(TaskTemplate):
    """Template for tasks that require login functionality"""

    def __init__(
        self,
        name="login",
        description="Login to the website",
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        super().__init__(name, description, username, password)
        self.instructions = inject_username_password(
            login_task_prompt, username, password
        )


class LegalContentTask(LoginTask):
    """Task to find and save legal documents from a website"""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        super().__init__(
            name="legal",
            description="Find and save legal documents",
            username=username,
            password=password,
        )
        self.instructions = inject_username_password(
            legal_content_task_prompt, username, password
        )


class StudentTask(LoginTask):
    """Task to explore a website as a student"""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        super().__init__(
            name="student",
            description="Explore the website as a student",
            username=username,
            password=password,
        )
        self.instructions = inject_username_password(
            student_task_prompt, username, password
        )


class TeacherTask(LoginTask):
    """Task to explore a website as a teacher"""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        super().__init__(
            name="teacher",
            description="Explore the website as a teacher",
            username=username,
            password=password,
        )
        self.instructions = inject_username_password(
            teacher_task_prompt, username, password
        )


class RegisterTask(TaskTemplate):
    """Task to find the registration page"""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        super().__init__(
            name="register",
            description="Find the registration page",
            username=username,
            password=password,
        )
        self.instructions = inject_username_password(
            register_task_prompt, username, password
        )


class LogoutTask(LoginTask):
    """Task to find the logout functionality"""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        super().__init__(
            name="logout",
            description="Find the logout page",
            username=username,
            password=password,
        )
        self.instructions = inject_username_password(
            logout_task_prompt, username, password
        )


class Website:
    """Class representing a website that can be tested with different tasks"""

    def __init__(self, name, url):
        self.name = name
        self.url = url


def get_task(
    url: str,
    task_name: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
):
    """Return a task for the specified website and task name"""
    known_tasks = {
        "login": LoginTask(username=username, password=password),
        "legal": LegalContentTask(username=username, password=password),
        "student": StudentTask(username=username, password=password),
        "teacher": TeacherTask(username=username, password=password),
        "register": RegisterTask(username=username, password=password),
        "logout": LogoutTask(username=username, password=password),
    }

    website_name = url.split("/")[-1]

    if task_name in known_tasks:
        task = known_tasks[task_name]
        return {
            "name": f"{website_name}_{task_name}",
            "url": url,
            "task": task.instructions,
        }
    
    return None
