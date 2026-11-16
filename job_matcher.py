
# STEP 1: Calculate skill matching percentage

def calculate_skill_match(candidate_skills, required_skills):

    matched_skills = []
    missing_skills = []

    candidate_skill_names = [
        skill.lower() for skill in candidate_skills
    ]

    for skill in required_skills:

        if skill.lower() in candidate_skill_names:
            matched_skills.append(skill)

        else:
            missing_skills.append(skill)

    if len(required_skills) == 0:
        return 0, matched_skills, missing_skills

    match_percentage = (
        len(matched_skills) / len(required_skills)
    ) * 100

    return round(match_percentage, 2), matched_skills, missing_skills


# STEP 2: Test the function

if __name__ == "__main__":

    candidate_skills = [
        "Python",
        "SQL",
        "PostgreSQL",
        "PL/SQL",
        "Power BI",
        "Excel"
    ]

    required_skills = [
        "Python",
        "SQL",
        "PostgreSQL",
        "AWS"
    ]

    percentage, matched, missing = calculate_skill_match(
        candidate_skills,
        required_skills
    )

    print("\n========== JOB MATCHING RESULT ==========")

    print("Matched Skills:", matched)

    print("Missing Skills:", missing)

    print("Match Percentage:", percentage, "%")
