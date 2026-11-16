
import re
import os

from pypdf import PdfReader

from SRC.skill_extractor import extract_skills
from SRC.text_cleaner import clean_resume_text
from SRC.database import (
    save_candidate,
    save_resume,
    save_candidate_skills
)


# =====================================================
# STEP 1: EXTRACT TEXT FROM PDF
# =====================================================

def extract_resume_text(file_path):

    try:
        reader = PdfReader(file_path)

        resume_text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                resume_text += page_text + "\n"

        return resume_text

    except Exception as error:

        print("Resume parsing failed:", error)

        return ""


# =====================================================
# STEP 2: EXTRACT CANDIDATE DETAILS
# =====================================================

def extract_candidate_details(resume_text):

    details = {}

    if not resume_text:
        return details

    # Clean text
    text = clean_resume_text(resume_text)

    # Convert text into individual lines
    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    # -------------------------------------------------
    # 1. EXTRACT NAME
    # -------------------------------------------------

    name = re.search(
        r'Name\s*:\s*(.+)',
        text,
        re.IGNORECASE
    )

    if name:
        details["full_name"] = name.group(1).strip()

    else:
        # If Name label is missing, use the first line
        # containing a likely candidate name.

        for line in lines[:5]:

            if (
                "@" not in line
                and not re.search(r'\d{10}', line)
                and not re.search(
                    r'RESUME|CURRICULUM VITAE|PROFILE',
                    line,
                    re.IGNORECASE
                )
                and len(line.split()) <= 5
                and re.fullmatch(
                    r'[A-Za-z][A-Za-z .\'-]*',
                    line
                )
            ):

                details["full_name"] = line.title()
                break

    # -------------------------------------------------
    # 2. EXTRACT EMAIL
    # -------------------------------------------------

    email = re.search(
        r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
        text
    )

    if email:
        details["email"] = email.group(0).lower()

    # -------------------------------------------------
    # 3. EXTRACT PHONE
    # -------------------------------------------------

    phone = re.search(
        r'(?:Phone|Mobile|Contact|Phone Number)?\s*[:\-]?\s*(?:\+91[\s-]?)?(\d{10})',
        text,
        re.IGNORECASE
    )

    if phone:
        details["phone"] = phone.group(1)

    # -------------------------------------------------
    # 4. EXTRACT LOCATION
    # -------------------------------------------------

    location = re.search(
        r'Location\s*:\s*(.+)',
        text,
        re.IGNORECASE
    )

    if location:
        details["location"] = location.group(1).strip()

    else:
        # Look for location in the first few lines.
        # Example: Nashik, Maharashtra

        for line in lines[:8]:

            if (
                "," in line
                and "@" not in line
                and not re.search(r'\d{10}', line)
                and not re.search(
                    r'EMAIL|PHONE|SUMMARY|RESUME|CURRICULUM',
                    line,
                    re.IGNORECASE
                )
            ):

                details["location"] = line.strip()
                break

    # -------------------------------------------------
    # 5. EXTRACT EXPERIENCE
    # -------------------------------------------------

    experience = re.search(
        r'(\d+(?:\.\d+)?)\s*\+?\s*years?',
        text,
        re.IGNORECASE
    )

    if experience:
        details["experience_years"] = float(
            experience.group(1)
        )

    # -------------------------------------------------
    # 6. EXTRACT EDUCATION
    # -------------------------------------------------

    education_patterns = [
        r'Bachelor of [A-Za-z ]+',
        r'Master of [A-Za-z ]+',
        r'Bachelor\'s Degree in [A-Za-z ]+',
        r'Master\'s Degree in [A-Za-z ]+',
        r'B\.?Sc\.?(?:\s+[A-Za-z]+)?',
        r'M\.?Sc\.?(?:\s+[A-Za-z]+)?',
        r'B\.?Tech\.?(?:\s+[A-Za-z]+)?',
        r'M\.?Tech\.?(?:\s+[A-Za-z]+)?',
        r'BCA',
        r'MCA',
        r'BBA',
        r'MBA'
    ]

    for line in lines:

        for pattern in education_patterns:

            education = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if education:

                details["education"] = (
                    education.group(0).strip()
                )

                break

        if "education" in details:
            break

    return details


# =====================================================
# STEP 3: MAIN PROGRAM
# =====================================================

if __name__ == "__main__":

    file_path = "data/resumes/sample_resume2.pdf"

    # Extract PDF text
    extracted_text = extract_resume_text(file_path)

    if extracted_text:

        # Clean resume text
        cleaned_text = clean_resume_text(extracted_text)

        # Extract skills
        skills = extract_skills(cleaned_text)

        # Extract candidate details
        candidate_details = extract_candidate_details(
            extracted_text
        )

        print("\n========== EXTRACTED SKILLS ==========\n")
        print(skills)

        print("\n========== CANDIDATE DETAILS ==========\n")
        print(candidate_details)

        # Validate required fields
        required_fields = [
            "full_name",
            "email",
            "phone",
            "location",
            "experience_years",
            "education"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in candidate_details
        ]

        if not missing_fields:

            # Save candidate
            candidate_id = save_candidate(
                candidate_details["full_name"],
                candidate_details["email"],
                candidate_details["phone"],
                candidate_details["location"],
                candidate_details["experience_years"],
                candidate_details["education"]
            )

            print("\n========== DATABASE RESULT ==========\n")
            print("Candidate ID:", candidate_id)

            if candidate_id:

                file_name = os.path.basename(file_path)

                file_type = (
                    os.path.splitext(file_name)[1]
                    .replace(".", "")
                    .upper()
                )

                # Save resume
                resume_id = save_resume(
                    candidate_id,
                    file_name,
                    file_path,
                    file_type,
                    cleaned_text
                )

                print("Resume ID:", resume_id)

                # Save skills
                if resume_id:
                    save_candidate_skills(
                        candidate_id,
                        skills
                    )

        else:

            print(
                "\nMissing candidate details:",
                missing_fields
            )

            print(
                "\nDatabase insertion skipped."
            )

        print("\n========== CLEANED RESUME TEXT ==========\n")
        print(cleaned_text)

    else:

        print("No resume text found!")
