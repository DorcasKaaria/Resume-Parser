-- ============================================================
-- RESUME PARSER DATABASE
-- SQLite Database Schema
-- ============================================================

-- ------------------------------------------------------------
-- 1. Enable foreign-key enforcement
-- ------------------------------------------------------------

PRAGMA foreign_keys = ON;


-- ============================================================
-- 2. LOCATION
-- Stores reusable geographic locations.
-- ============================================================

CREATE TABLE IF NOT EXISTS location (
    location_id   INTEGER PRIMARY KEY,
    location_name TEXT NOT NULL UNIQUE
);


-- ============================================================
-- 3. CANDIDATE
-- Main candidate/applicant table.
-- ============================================================

CREATE TABLE IF NOT EXISTS candidate (
    candidate_id        INTEGER PRIMARY KEY,
    candidate_name      TEXT NOT NULL,
	target_role         TEXT,
	phone_number        TEXT UNIQUE,
    email               TEXT UNIQUE,
    linkedin_url        TEXT UNIQUE,
    github              TEXT UNIQUE,
    years_of_experience TEXT,
    location_id         INTEGER,

    FOREIGN KEY (location_id)
        REFERENCES location(location_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


-- ============================================================
-- 4. COMPANY
-- Stores companies extracted from resumes.
-- ============================================================

CREATE TABLE IF NOT EXISTS company (
    company_id   INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL UNIQUE,
    location_id  INTEGER,

    FOREIGN KEY (location_id)
        REFERENCES location(location_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);


-- ============================================================
-- 5. SKILL
-- Master list of normalized skills.
-- ============================================================

CREATE TABLE IF NOT EXISTS skill (
    skill_id    INTEGER PRIMARY KEY,
    skill_title TEXT NOT NULL UNIQUE
);


-- ============================================================
-- 6. CANDIDATE_SKILL
-- Many-to-many relationship between candidates and skills.
-- ============================================================

CREATE TABLE IF NOT EXISTS candidate_skill (
    candidate_id INTEGER NOT NULL,
    skill_id     INTEGER NOT NULL,

    PRIMARY KEY (candidate_id, skill_id),

    FOREIGN KEY (candidate_id)
        REFERENCES candidate(candidate_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES skill(skill_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- 7. INSTITUTION
-- Schools, colleges, universities, training institutions, etc.
-- ============================================================

CREATE TABLE IF NOT EXISTS institution (
    institution_id   INTEGER PRIMARY KEY,
    institution_name TEXT NOT NULL UNIQUE
);


-- ============================================================
-- 8. DEGREE
-- Normalized list of degrees / qualifications.
-- ============================================================

CREATE TABLE IF NOT EXISTS degree (
    degree_id INTEGER PRIMARY KEY,
    title     TEXT NOT NULL UNIQUE
);


-- ============================================================
-- 9. EDUCATION
-- Associates a candidate with a degree and institution.
-- ============================================================

CREATE TABLE IF NOT EXISTS education (
    education_id   INTEGER PRIMARY KEY,
    candidate_id   INTEGER NOT NULL,
    degree_id      INTEGER,
    institution_id INTEGER,
    graduation_year INTEGER,

    FOREIGN KEY (candidate_id)
        REFERENCES candidate(candidate_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (degree_id)
        REFERENCES degree(degree_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    FOREIGN KEY (institution_id)
        REFERENCES institution(institution_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CHECK (
        graduation_year IS NULL
        OR graduation_year BETWEEN 1900 AND 2100
    )
);


-- ============================================================
-- 10. ROLE
-- Normalized list of job titles.
-- ============================================================

CREATE TABLE IF NOT EXISTS role (
    role_id INTEGER PRIMARY KEY,
    title   TEXT NOT NULL UNIQUE
);


-- ============================================================
-- 11. EMPLOYMENT
-- Connects candidate + company + role.
-- Represents employment history.
-- ============================================================

CREATE TABLE IF NOT EXISTS employment (
    employment_id INTEGER PRIMARY KEY,
    candidate_id  INTEGER NOT NULL,
    company_id    INTEGER,
    role_id       INTEGER,
	role_description TEXT,
    start_date    TEXT,
    end_date      TEXT,
    is_current    INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (candidate_id)
        REFERENCES candidate(candidate_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (company_id)
        REFERENCES company(company_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    FOREIGN KEY (role_id)
        REFERENCES role(role_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CHECK (is_current IN (0, 1)),

    CHECK (
        start_date IS NULL
        OR date(start_date) IS NOT NULL
    ),

    CHECK (
        end_date IS NULL
        OR date(end_date) IS NOT NULL
    ),

    CHECK (
        start_date IS NULL
        OR end_date IS NULL
        OR date(end_date) >= date(start_date)
    )
);


-- ============================================================
-- 12. INDEXES
-- Improve lookup and JOIN performance.
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_candidate_location
    ON candidate(location_id);

CREATE INDEX IF NOT EXISTS idx_company_location
    ON company(location_id);

CREATE INDEX IF NOT EXISTS idx_candidate_skill_skill
    ON candidate_skill(skill_id);

CREATE INDEX IF NOT EXISTS idx_candidate_skill_candidate
    ON candidate_skill(candidate_id);

CREATE INDEX IF NOT EXISTS idx_education_candidate
    ON education(candidate_id);

CREATE INDEX IF NOT EXISTS idx_education_degree
    ON education(degree_id);

CREATE INDEX IF NOT EXISTS idx_education_institution
    ON education(institution_id);

CREATE INDEX IF NOT EXISTS idx_employment_candidate
    ON employment(candidate_id);

CREATE INDEX IF NOT EXISTS idx_employment_company
    ON employment(company_id);

CREATE INDEX IF NOT EXISTS idx_employment_role
    ON employment(role_id);

CREATE INDEX IF NOT EXISTS idx_employment_current
    ON employment(candidate_id, is_current);