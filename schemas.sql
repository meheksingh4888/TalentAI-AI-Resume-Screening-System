
CREATE TABLE IF NOT EXISTS candidates (

    candidate_id SERIAL PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(150) UNIQUE NOT NULL,

    phone VARCHAR(20),

    location VARCHAR(100),

    experience_years NUMERIC(4,1),

    education VARCHAR(150),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


CREATE TABLE IF NOT EXISTS resumes (

    resume_id SERIAL PRIMARY KEY,

    candidate_id INTEGER NOT NULL,

    file_name VARCHAR(255) NOT NULL,

    file_path TEXT NOT NULL,

    file_type VARCHAR(20),

    extracted_text TEXT,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_candidate
        FOREIGN KEY (candidate_id)
        REFERENCES candidates(candidate_id)
        ON DELETE CASCADE

);


CREATE TABLE IF NOT EXISTS skills (

    skill_id SERIAL PRIMARY KEY,

    skill_name VARCHAR(100) UNIQUE NOT NULL,

    skill_category VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS candidate_skills (

    candidate_skill_id SERIAL PRIMARY KEY,

    candidate_id INTEGER NOT NULL,

    skill_id INTEGER NOT NULL,

    proficiency_level VARCHAR(50),

    CONSTRAINT fk_cs_candidate
        FOREIGN KEY (candidate_id)
        REFERENCES candidates(candidate_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cs_skill
        FOREIGN KEY (skill_id)
        REFERENCES skills(skill_id)
        ON DELETE CASCADE,

    CONSTRAINT unique_candidate_skill
        UNIQUE (candidate_id, skill_id)

);



-- ==========================================
-- MATCH RESULTS TABLE
-- ==========================================

CREATE TABLE IF NOT EXISTS match_results (
    match_id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(candidate_id),
    resume_id INTEGER REFERENCES resumes(resume_id),
    match_percentage NUMERIC(5,2),
    matched_skills TEXT[],
    missing_skills TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================
-- JOB DESCRIPTION MANAGEMENT
-- ==========================================

CREATE TABLE IF NOT EXISTS job_descriptions (

    job_id SERIAL PRIMARY KEY,

    job_title VARCHAR(200) NOT NULL,

    min_experience NUMERIC(4,1),

    max_experience NUMERIC(4,1),

    job_description TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- Link screening results to a selected job

ALTER TABLE match_results
ADD COLUMN IF NOT EXISTS job_id INTEGER
REFERENCES job_descriptions(job_id);
