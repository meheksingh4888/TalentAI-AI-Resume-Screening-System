
import re

# =====================================================
# SKILL MASTER LIST
# All skills are stored in canonical format.
# =====================================================

SKILLS = [
    # Programming Languages
    "Python",
    "Java",
    "C++",
    "JavaScript",

    # Database Skills
    "SQL",
    "PostgreSQL",
    "PL/SQL",
    "Oracle",
    "MySQL",
    "Database Connectivity",
    "Database Testing",
    "SQL Testing",
    "Data Validation",
    "Data Integrity",
    "Data Modeling",
    "ETL",

    # Python Development
    "OOP",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Flask",
    "Django",
    "REST API",
    "Data Structures",
    "Algorithms",
    "Git",
    "GitHub",

    # Data Analytics
    "Power BI",
    "Excel",
    "Tableau",
    "Data Analysis",
    "DAX",
    "Machine Learning",
    "AWS",
    "Azure",

    # Software Testing / Manual QA
    "Manual Testing",
    "Software Testing",
    "SDLC",
    "STLC",
    "Test Case Preparation",
    "Test Scenario Design",
    "Functional Testing",
    "Regression Testing",
    "Smoke Testing",
    "Sanity Testing",
    "Integration Testing",
    "System Testing",
    "UAT Testing",
    "Defect Reporting",
    "Bug Reporting",
    "Defect Investigation",
    "Jira",

    # General Skills
    "Problem Solving",
    "Communication"
]


# =====================================================
# SKILL ALIASES
# Different words can represent the same skill.
# =====================================================

SKILL_ALIASES = {
    "Python": [
        "Python programming",
        "Python development"
    ],

    "OOP": [
        "Object Oriented Programming",
        "Object-Oriented Programming",
        "OOP concepts"
    ],

    "REST API": [
        "REST APIs",
        "RESTful API",
        "RESTful APIs",
        "API development"
    ],

    "Data Structures": [
        "Data structure"
    ],

    "Algorithms": [
        "Algorithm",
        "DSA"
    ],

    "Database Connectivity": [
        "Database connection",
        "DB connectivity"
    ],

    "SQL Testing": [
        "SQL database testing",
        "Database SQL testing"
    ],

    "UAT Testing": [
        "UAT",
        "User Acceptance Testing"
    ],

    "Test Case Preparation": [
        "Test case design",
        "Test cases"
    ],

    "Test Scenario Design": [
        "Test scenario preparation",
        "Test scenarios"
    ],

    "Defect Reporting": [
        "Defect logging",
        "Bug reporting"
    ],

    "Manual Testing": [
        "Manual software testing"
    ],

    "GitHub": [
        "Git hub"
    ]
}


# =====================================================
# SKILL EXTRACTION FUNCTION
# =====================================================

def extract_skills(resume_text):

    if not resume_text:
        return []

    extracted_skills = []

    text = resume_text.lower()

    # Check canonical skill names
    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text):

            extracted_skills.append(skill)

    # Check alternative skill names
    for canonical_skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            pattern = r"(?<!\w)" + re.escape(alias.lower()) + r"(?!\w)"

            if re.search(pattern, text):

                extracted_skills.append(canonical_skill)
                break

    # Remove duplicate skills while preserving order
    extracted_skills = list(dict.fromkeys(extracted_skills))

    return extracted_skills
