import os
from typing import Dict, List

from .models import TypedArgs

login_task_prompt = """
1. Navigate to the login
2. Login with Vidis 
3. On the Vidis login page choose "Test Landesportal" as Landesportal/Schulportal
4. Login with the credentials: 
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
    Click on each (Datenschutz, Impressum, AGB) and save the entire content of each page as pdf in the current task folder (use the action 'save_page_as_pdf' with either 'privacy_policy', 'imprint' or 'tos').

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

    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.instructions = ""

    def __repr__(self):
        return f"TaskTemplate(name={self.name}, description={self.description})"


class LoginTask(TaskTemplate):
    """Template for tasks that require login functionality"""

    def __init__(self, name="login", description="Login to the website"):
        super().__init__(name, description)
        self.instructions = inject_username_password(login_task_prompt)


class LegalContentTask(LoginTask):
    """Task to find and save legal documents from a website"""

    def __init__(self):
        super().__init__(name="legal", description="Find and save legal documents")
        self.instructions = inject_username_password(legal_content_task_prompt)


class StudentTask(LoginTask):
    """Task to explore a website as a student"""

    def __init__(self):
        super().__init__(name="student", description="Explore the website as a student")
        self.instructions = inject_username_password(student_task_prompt)


class TeacherTask(LoginTask):
    """Task to explore a website as a teacher"""

    def __init__(self):
        super().__init__(name="teacher", description="Explore the website as a teacher")
        self.instructions = inject_username_password(teacher_task_prompt)


class RegisterTask(TaskTemplate):
    """Task to find the registration page"""

    def __init__(self):
        super().__init__(name="register", description="Find the registration page")
        self.instructions = inject_username_password(register_task_prompt)


class LogoutTask(LoginTask):
    """Task to find the logout functionality"""

    def __init__(self):
        super().__init__(name="logout", description="Find the logout page")
        self.instructions = inject_username_password(logout_task_prompt)


class Website:
    """Class representing a website that can be tested with different tasks"""

    def __init__(self, name, url):
        self.name = name
        self.url = url


def get_all_tasks(url: str, task_names: List[str]):
    """Return tasks for the specified website and task names"""
    known_tasks = {
        "login": LoginTask(),
        "legal": LegalContentTask(),
        "student": StudentTask(),
        "teacher": TeacherTask(),
        "register": RegisterTask(),
        "logout": LogoutTask(),
    }

    website_name = url.split("/")[-1]

    task_dicts = []
    for task_name in task_names:
        if task_name in known_tasks:
            task = known_tasks[task_name]
            task_dicts.append(
                {
                    "name": f"{website_name}_{task_name}",
                    "url": url,
                    "task": task.instructions,
                }
            )

    return task_dicts
