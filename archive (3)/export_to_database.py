import sqlite3
import json
from pathlib import Path


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

JSON_FILE = Path(
    r"C:\Users\25471\Desktop\Resume Parser Project\parsed_resumes\parsed_resumes.json"
)

DATABASE_FILE = Path(
    r"C:\Users\25471\Desktop\Resume Parser Project\resume_parser.db"
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

conn = sqlite3.connect(DATABASE_FILE)

# Enable foreign key constraints
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()


# --------------------------------------------------
# LOAD EXTRACTED JSON
# --------------------------------------------------

with open(JSON_FILE, "r", encoding="utf-8") as file:
    resumes = json.load(file)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_or_create_location(location_name):
    """Return location_id. Create location if it does not exist."""

    if not location_name:
        return None

    location_name = location_name.strip()

    cursor.execute(
        """
        SELECT location_id
        FROM location
        WHERE location_name = ?
        """,
        (location_name,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO location (location_name)
        VALUES (?)
        """,
        (location_name,)
    )

    return cursor.lastrowid


def get_or_create_skill(skill_title):
    """Return skill_id. Create skill if it does not exist."""

    if not skill_title:
        return None

    skill_title = skill_title.strip()

    cursor.execute(
        """
        SELECT skill_id
        FROM skill
        WHERE LOWER(skill_title) = LOWER(?)
        """,
        (skill_title,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO skill (skill_title)
        VALUES (?)
        """,
        (skill_title,)
    )

    return cursor.lastrowid


def get_or_create_company(company_name, location_id):
    """Return company_id. Create company if it does not exist."""

    if not company_name:
        return None

    company_name = company_name.strip()

    cursor.execute(
        """
        SELECT company_id
        FROM company
        WHERE LOWER(company_name) = LOWER(?)
        """,
        (company_name,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO company (company_name, location_id)
        VALUES (?, ?)
        """,
        (company_name, location_id)
    )

    return cursor.lastrowid


def get_or_create_role(role_title):
    """Return role_id. Create role if it does not exist."""

    if not role_title:
        return None

    role_title = role_title.strip()

    cursor.execute(
        """
        SELECT role_id
        FROM role
        WHERE LOWER(title) = LOWER(?)
        """,
        (role_title,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO role (title)
        VALUES (?)
        """,
        (role_title,)
    )

    return cursor.lastrowid


def get_or_create_institution(institution_name):
    """Return institution_id. Create institution if it does not exist."""

    if not institution_name:
        return None

    institution_name = institution_name.strip()

    cursor.execute(
        """
        SELECT institution_id
        FROM institution
        WHERE LOWER(institution_name) = LOWER(?)
        """,
        (institution_name,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO institution (institution_name)
        VALUES (?)
        """,
        (institution_name,)
    )

    return cursor.lastrowid


def get_or_create_degree(degree_title):
    """Return degree_id. Create degree if it does not exist."""

    if not degree_title:
        return None

    degree_title = degree_title.strip()

    cursor.execute(
        """
        SELECT degree_id
        FROM degree
        WHERE LOWER(title) = LOWER(?)
        """,
        (degree_title,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        """
        INSERT INTO degree (title)
        VALUES (?)
        """,
        (degree_title,)
    )

    return cursor.lastrowid


# --------------------------------------------------
# PROCESS EACH RESUME
# --------------------------------------------------

for resume in resumes:

    # Skip failed extraction records
    if "error" in resume:
        print(
            f"Skipping {resume.get('source_file', 'unknown file')}: "
            f"{resume['error']}"
        )
        continue

    try:

        # --------------------------------------------------
        # CANDIDATE LOCATION
        # --------------------------------------------------

        location_id = get_or_create_location(
            resume.get("location")
        )


        # --------------------------------------------------
        # CANDIDATE
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO candidate (
                target_role,
                candidate_name,
                phone_number,
                email,
                linkedin_url,
                github,
                years_of_experience,
                location_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resume.get("target_role"),
                resume.get("candidate_name"),
                resume.get("phone_number"),
                resume.get("email"),
                resume.get("linkedin_url"),
                resume.get("github"),
                resume.get("years_of_experience"),
                location_id
            )
        )

        candidate_id = cursor.lastrowid


        # --------------------------------------------------
        # SKILLS
        # --------------------------------------------------

        skills = resume.get("skills") or []

        for skill_name in skills:

            skill_id = get_or_create_skill(skill_name)

            if skill_id:

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO candidate_skill (
                        candidate_id,
                        skill_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        candidate_id,
                        skill_id
                    )
                )


        # --------------------------------------------------
        # EXPERIENCE / EMPLOYMENT
        # --------------------------------------------------

        experiences = resume.get("experience") or []

        for experience in experiences:

            company_location_id = get_or_create_location(
                experience.get("company_location")
            )

            company_id = get_or_create_company(
                experience.get("company_name"),
                company_location_id
            )

            role_id = get_or_create_role(
                experience.get("role_title")
            )

            cursor.execute(
                """
                INSERT INTO employment (
                    candidate_id,
                    company_id,
                    role_id,
                    role_description,
                    start_date,
                    end_date,
                    is_current
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate_id,
                    company_id,
                    role_id,
                    experience.get("role_description"),
                    experience.get("start_date"),
                    experience.get("end_date"),
                    experience.get("is_current", False)
                )
            )


        # --------------------------------------------------
        # EDUCATION
        # --------------------------------------------------

        education_records = resume.get("education") or []

        for education in education_records:

            institution_id = get_or_create_institution(
                education.get("institution_name")
            )

            degree_id = get_or_create_degree(
                education.get("education_level")
            )

            graduation_year = education.get("graduation_year")

            # Convert graduation year to integer
            if graduation_year:
                try:
                    graduation_year = int(graduation_year)
                except (ValueError, TypeError):
                    graduation_year = None

            cursor.execute(
                """
                INSERT INTO education (
                    candidate_id,
                    degree_id,
                    institution_id,
                    graduation_year
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    candidate_id,
                    degree_id,
                    institution_id,
                    graduation_year
                )
            )


        print(
            f"Successfully inserted: "
            f"{resume.get('candidate_name', 'Unknown')}"
        )


    except Exception as e:

        print(
            f"Error processing "
            f"{resume.get('source_file', 'unknown file')}: {e}"
        )


# --------------------------------------------------
# SAVE CHANGES
# --------------------------------------------------

conn.commit()

conn.close()

print("\nDatabase import completed successfully.")
print(f"Database: {DATABASE_FILE}")