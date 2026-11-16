
import os
import pg8000
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ==========================================
# STEP 1: DATABASE CONNECTION
# ==========================================

def get_connection():
    """
    Establish a connection with PostgreSQL
    using the pg8000 Python driver.
    """

    connection = pg8000.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    return connection


# ==========================================
# STEP 2: EXECUTE DATABASE SCHEMA
# ==========================================

def execute_schema():

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        with open("database/schemas.sql", "r", encoding="utf-8") as file:
            sql_script = file.read()

        # Execute individual SQL statements.
        # This avoids multi-command prepared statement errors.
        statements = [
            statement.strip()
            for statement in sql_script.split(";")
            if statement.strip()
        ]

        for statement in statements:
            cursor.execute(statement)

        connection.commit()

        print("Database tables created successfully!")

    except Exception as error:
        connection.rollback()
        print("Error creating tables:", error)
        raise

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# STEP 3: SAVE CANDIDATE
# ==========================================

def save_candidate(
    full_name,
    email,
    phone,
    location,
    experience_years,
    education
):

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        check_query = """
            SELECT candidate_id
            FROM candidates
            WHERE email = %s;
        """

        cursor.execute(check_query, (email,))
        existing_candidate = cursor.fetchone()

        if existing_candidate:
            candidate_id = existing_candidate[0]

            print("Candidate already exists!")
            print("Using Existing Candidate ID:", candidate_id)

            return candidate_id

        insert_query = """
            INSERT INTO candidates
            (
                full_name,
                email,
                phone,
                location,
                experience_years,
                education
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING candidate_id;
        """

        cursor.execute(
            insert_query,
            (
                full_name,
                email,
                phone,
                location,
                experience_years,
                education
            )
        )

        candidate_id = cursor.fetchone()[0]
        connection.commit()

        print("Candidate saved successfully!")

        return candidate_id

    except Exception as error:
        connection.rollback()
        print("Error saving candidate:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# STEP 4: SAVE RESUME
# ==========================================

def save_resume(
    candidate_id,
    file_name,
    file_path,
    file_type,
    extracted_text
):

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO resumes
            (
                candidate_id,
                file_name,
                file_path,
                file_type,
                extracted_text
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING resume_id;
        """

        cursor.execute(
            query,
            (
                candidate_id,
                file_name,
                file_path,
                file_type,
                extracted_text
            )
        )

        resume_id = cursor.fetchone()[0]
        connection.commit()

        print("Resume saved successfully!")

        return resume_id

    except Exception as error:
        connection.rollback()
        print("Error saving resume:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# STEP 5: SAVE CANDIDATE SKILLS
# ==========================================

def save_candidate_skills(candidate_id, skills):

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        for skill in skills:

            insert_skill_query = """
                INSERT INTO skills (skill_name)
                VALUES (%s)
                ON CONFLICT (skill_name) DO NOTHING;
            """

            cursor.execute(insert_skill_query, (skill,))

            select_skill_query = """
                SELECT skill_id
                FROM skills
                WHERE skill_name = %s;
            """

            cursor.execute(select_skill_query, (skill,))
            skill_result = cursor.fetchone()

            if not skill_result:
                continue

            skill_id = skill_result[0]

            insert_candidate_skill_query = """
                INSERT INTO candidate_skills
                (candidate_id, skill_id)
                VALUES (%s, %s)
                ON CONFLICT (candidate_id, skill_id) DO NOTHING;
            """

            cursor.execute(
                insert_candidate_skill_query,
                (candidate_id, skill_id)
            )

        connection.commit()

        print("Candidate skills saved successfully!")

    except Exception as error:
        connection.rollback()
        print("Error saving candidate skills:", error)

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# STEP 6: GET DASHBOARD METRICS
# ==========================================

def get_dashboard_metrics():

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        # Count total candidates
        cursor.execute("""
            SELECT COUNT(*)
            FROM candidates;
        """)

        total_candidates = cursor.fetchone()[0]

        # Count total resumes
        cursor.execute("""
            SELECT COUNT(*)
            FROM resumes;
        """)

        total_resumes = cursor.fetchone()[0]

        # Calculate average match score
        cursor.execute("""
            SELECT COALESCE(AVG(match_percentage), 0)
            FROM match_results;
        """)

        average_match_score = cursor.fetchone()[0]

        return (
            total_candidates,
            total_resumes,
            average_match_score
        )

    except Exception as error:
        print("Error fetching dashboard metrics:", error)
        return 0, 0, 0

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# STEP 7: SAVE MATCH RESULT
# ==========================================

def save_match_result(
    candidate_id,
    resume_id,
    match_percentage,
    matched_skills,
    missing_skills,
    job_id=None
):

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO match_results
            (
                candidate_id,
                resume_id,
                match_percentage,
                matched_skills,
                missing_skills,
                job_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING match_id;
        """

        cursor.execute(
            query,
            (
                candidate_id,
                resume_id,
                match_percentage,
                matched_skills,
                missing_skills,
                job_id
            )
        )

        match_id = cursor.fetchone()[0]

        connection.commit()

        print("Match result saved successfully!")

        return match_id

    except Exception as error:
        connection.rollback()
        print("Error saving match result:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# STEP 8: GET RECENT SCREENING HISTORY
# ==========================================

def get_recent_screenings(limit=10):

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                mr.match_id,
                c.full_name,
                r.file_name,
                mr.match_percentage,
                mr.matched_skills,
                mr.missing_skills,
                mr.created_at

            FROM match_results mr

            JOIN candidates c
                ON mr.candidate_id = c.candidate_id

            JOIN resumes r
                ON mr.resume_id = r.resume_id

            ORDER BY mr.created_at DESC

            LIMIT %s;
        """

        cursor.execute(query, (limit,))

        screenings = cursor.fetchall()

        return screenings

    except Exception as error:
        print("Error fetching screening history:", error)
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# JOB DESCRIPTION MANAGEMENT
# ==========================================

def save_job_description(
    job_title,
    min_experience,
    max_experience,
    job_description
):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO job_descriptions
            (
                job_title,
                min_experience,
                max_experience,
                job_description
            )
            VALUES (%s, %s, %s, %s)
            RETURNING job_id;
            """,
            (
                job_title,
                min_experience,
                max_experience,
                job_description
            )
        )

        job_id = cursor.fetchone()[0]

        connection.commit()

        print("Job description saved successfully!")

        return job_id

    except Exception as error:

        if connection:
            connection.rollback()

        print("Job description save failed:", error)

        return None

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# GET ALL JOB DESCRIPTIONS
# ==========================================

def get_job_descriptions():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                job_id,
                job_title,
                min_experience,
                max_experience,
                created_at,
                job_description

            FROM job_descriptions

            ORDER BY created_at DESC;
            """
        )

        jobs = cursor.fetchall()

        return jobs

    except Exception as error:
        print("Fetching jobs failed:", error)
        return []

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ==========================================
# GET CANDIDATES BY JOB
# ==========================================

def get_candidates_by_job(job_id):

    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT DISTINCT ON (c.candidate_id)

                mr.match_id,
                c.candidate_id,
                c.full_name,
                c.email,
                c.experience_years,
                c.education,
                mr.match_percentage,
                mr.matched_skills,
                mr.missing_skills,
                mr.created_at

            FROM match_results mr

            INNER JOIN candidates c
                ON mr.candidate_id = c.candidate_id

            WHERE mr.job_id = %s

            ORDER BY
                c.candidate_id,
                mr.created_at DESC,
                mr.match_id DESC;
        """

        cursor.execute(query, (job_id,))

        results = cursor.fetchall()

        # Rank candidates by their latest match score
        results.sort(
            key=lambda candidate: float(candidate[6] or 0),
            reverse=True
        )

        return results

    except Exception as error:
        print("Error fetching candidates:", error)
        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# STEP 9: TEST DATABASE AND JOB MANAGEMENT
# ==========================================

if __name__ == "__main__":

    try:

        # 1. Create/update database tables
        execute_schema()

        # 2. Test database connection
        connection = get_connection()

        print("\nDatabase connected successfully!")

        cursor = connection.cursor()

        cursor.execute("SELECT current_database();")

        result = cursor.fetchone()

        print("Connected Database:", result[0])

        cursor.close()
        connection.close()

        # 3. Fetch saved jobs
        jobs = get_job_descriptions()

        print("\n========== SAVED JOBS ==========\n")

        for job in jobs:
            print(job)

        print("\nDatabase testing completed!")

    except Exception as error:

        print("Database operation failed!")
        print("Error:", error)
