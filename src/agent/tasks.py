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

legal_task_prompt = """
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
- Explore unique internal pages throughout the website.
- Avoid repeatedly visiting the same pages or looping.

Step 3: Completion Condition
-------------------------------
You are done with this task when:
- You have saved available legal pages (Datenschutz, Impressum, AGB)
AND ALSO:
- You have thoroughly browsed the website.
"""


def get_legal_task_prompt() -> str:
    """
    Generate the legal content task prompt.

    Returns:
        The complete task prompt
    """
    return login_task_prompt + legal_task_prompt


student_task_prompt = """
Afterwards:
You are a student who wants to learn and explore educational content on this website. Your goal is to understand what this website offers and navigate through it like a real student would.

Step 1: Understand the Website's Purpose
------------------------------------------
- Explore the main navigation menu and homepage to understand what's available
- Understand the website's purpose and what educational content it provides
- Check out "About" sections to understand the institution or platform

Step 2: Explore Educational Content
------------------------------------
- Look for sections like "Courses", "Lessons", "Tutorials", "Learning Materials", "Subjects", etc.
- Click on course listings, subject categories, or educational content that interests you
- Navigate to course descriptions, syllabi, or learning module overviews
- Explore different educational pathways or learning tracks
- Look for student resources, help sections, or getting started guides

Step 3: Browse the Website
---------------------------
Continue browsing the website to explore educational opportunities:

- Click on different visible menu items, homepage sections, or internal links.
- Visit key pages that would help you learn something new.
- Explore unique internal pages throughout the website.
- Avoid repeatedly visiting the same pages or looping.

Important restrictions:
- DO NOT play videos, audio, or interactive media - focus on navigating to new pages instead
- DO NOT fill out forms or try to register/login unless necessary for navigation
- DO NOT download files - focus on web page content
- Prioritize clicking links that take you to NEW pages rather than interactive elements on the same page

Step 4: Completion Condition
------------------------------
You are done with this task when:
- You have thoroughly browsed the website.

Your browsing should feel natural and purposeful, as if you're genuinely interested in learning from this website and exploring what educational opportunities it offers.
"""


def get_student_task_prompt() -> str:
    return login_task_prompt + student_task_prompt


teacher_task_prompt = """
Afterwards:
You are a teacher who wants to explore educational resources and tools on this website. Your goal is to understand what this platform offers for educators and how it could support your teaching activities.

Step 1: Understand the Website's Purpose
------------------------------------------
- Explore the main navigation menu and homepage to understand what's available for educators
- Understand the website's purpose and what educational resources it provides for teachers
- Check out "About" sections to understand the institution or platform's educational philosophy

Step 2: Explore Educational Resources
--------------------------------------
- Look for sections like "For Teachers", "Educator Resources", "Teaching Materials", "Instructor Tools", "Curriculum", etc.
- Click on teacher guides, lesson plans, or educational resources that could be useful in your classroom
- Navigate to instructor dashboards, teaching methodologies, or educational frameworks
- Explore different teaching tools, assessment resources, or classroom management features
- Look for teacher support, professional development, or training resources

Step 3: Browse the Website
---------------------------
Continue browsing the website to explore educational tools and resources:

- Click on different visible menu items, homepage sections, or internal links.
- Visit key pages that would help you in your teaching role.
- Explore unique internal pages throughout the website.
- Avoid repeatedly visiting the same pages or looping.

Important restrictions:
- DO NOT play videos, audio, or interactive media - focus on navigating to new pages instead
- DO NOT fill out forms or try to register/login unless necessary for navigation
- DO NOT download files - focus on web page content
- Prioritize clicking links that take you to NEW pages rather than interactive elements on the same page

Step 4: Completion Condition
------------------------------
You are done with this task when:
- You have thoroughly browsed the website.

Your browsing should feel natural and purposeful, as if you're genuinely interested in finding resources that could enhance your teaching and exploring what educational tools this website offers for educators.
"""


def get_teacher_task_prompt() -> str:
    return login_task_prompt + teacher_task_prompt


def get_all_tasks_prompt() -> str:
    """
    Generate a combined prompt that executes all tasks in sequence.

    Returns:
        The complete task prompt combining all tasks
    """
    combined_prompt = login_task_prompt + "\n\n"
    combined_prompt += "=== TASK 1: LEGAL CONTENT EXPLORATION ===\n"
    combined_prompt += legal_task_prompt + "\n\n"
    combined_prompt += "=== TASK 2: STUDENT EXPLORATION ===\n"
    combined_prompt += student_task_prompt + "\n\n"
    combined_prompt += "=== TASK 3: TEACHER EXPLORATION ===\n"
    combined_prompt += teacher_task_prompt + "\n\n"
    combined_prompt += """
=== OVERALL COMPLETION CONDITION ===
You are done with ALL tasks when you have completed:
1. Legal content exploration (saved legal pages and thoroughly browsed the website)
2. Student exploration (thoroughly browsed the website as a student)
3. Teacher exploration (thoroughly browsed the website as a teacher)

Execute all tasks in the order listed above.
"""

    return combined_prompt


def get_task_prompt(task_type: str) -> str:
    if task_type == "login":
        return login_task_prompt
    elif task_type == "legal":
        return get_legal_task_prompt()
    elif task_type == "student":
        return get_student_task_prompt()
    elif task_type == "teacher":
        return get_teacher_task_prompt()
    elif task_type == "all":
        return get_all_tasks_prompt()
    else:
        raise ValueError(f"Invalid task type: {task_type}")
