#!/usr/bin/env python3
"""
Import extracted resume JSON into the normalized SQLite resume database.

Usage:
    python import_data_to_database.py resumes.db parsed_resumes.json

The importer:
- Reuses existing location/company/skill/institution/degree/role rows.
- De-duplicates candidates using the strongest available identifier:
  email -> linkedin_url -> github -> phone_number.
- Creates candidate_skill rows through the many-to-many relationship.
- Creates normalized education and employment rows linked by foreign keys.
- Is idempotent: rerunning the same JSON does not create duplicate child rows.
- Converts extracted dates such as "May, 2028" and "2023" to SQLite ISO dates.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def clean(value: Any) -> Optional[str]:
    """Return stripped text, or None for missing/blank values."""
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def normalize_date(value: Any) -> Optional[str]:
    """
    Convert the JSON date formats to ISO YYYY-MM-DD, which satisfies
    the CHECK constraints in the supplied SQLite schema.

    Examples:
        "May, 2028"     -> "2028-05-01"
        "MAY, 2028"     -> "2028-05-01"
        "2023"          -> "2023-01-01"

    The database schema does not store date precision, so month-only values
    use day 01 and year-only values use January 01.
    """
    value = clean(value)
    if value is None:
        return None

    # Already ISO.
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            return None

    # "May, 2028", "May 2028", "MAY, 2028"
    match = re.fullmatch(
        r"([A-Za-z]+)\s*,?\s*(\d{4})",
        value,
        flags=re.IGNORECASE,
    )
    if match:
        month_name, year = match.groups()
        month = MONTHS.get(month_name.lower())
        if month:
            return f"{int(year):04d}-{month:02d}-01"

    # "2023"
    if re.fullmatch(r"\d{4}", value):
        return f"{int(value):04d}-01-01"

    raise ValueError(f"Unsupported date format: {value!r}")


def normalize_text(value: Any) -> Optional[str]:
    """Normalize simple master-data text while preserving meaningful wording."""
    value = clean(value)
    if value is None:
        return None
    return re.sub(r"\s+", " ", value)


def get_or_create_location(cur: sqlite3.Cursor, location_name: Any) -> Optional[int]:
    name = normalize_text(location_name)
    if not name:
        return None

    cur.execute(
        "INSERT OR IGNORE INTO location (location_name) VALUES (?)",
        (name,),
    )
    cur.execute(
        "SELECT location_id FROM location WHERE location_name = ?",
        (name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_company(
    cur: sqlite3.Cursor,
    company_name: Any,
    company_location: Any,
) -> Optional[int]:
    name = normalize_text(company_name)
    if not name:
        return None

    location_id = get_or_create_location(cur, company_location)

    cur.execute(
        "INSERT OR IGNORE INTO company (company_name, location_id) VALUES (?, ?)",
        (name, location_id),
    )

    # Do not overwrite an existing company location unless it is missing.
    if location_id is not None:
        cur.execute(
            """
            UPDATE company
               SET location_id = ?
             WHERE company_name = ?
               AND location_id IS NULL
            """,
            (location_id, name),
        )

    cur.execute(
        "SELECT company_id FROM company WHERE company_name = ?",
        (name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_skill(cur: sqlite3.Cursor, skill_title: Any) -> Optional[int]:
    title = normalize_text(skill_title)
    if not title:
        return None

    cur.execute(
        "INSERT OR IGNORE INTO skill (skill_title) VALUES (?)",
        (title,),
    )
    cur.execute(
        "SELECT skill_id FROM skill WHERE skill_title = ?",
        (title,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_institution(
    cur: sqlite3.Cursor,
    institution_name: Any,
) -> Optional[int]:
    name = normalize_text(institution_name)
    if not name:
        return None

    cur.execute(
        "INSERT OR IGNORE INTO institution (institution_name) VALUES (?)",
        (name,),
    )
    cur.execute(
        "SELECT institution_id FROM institution WHERE institution_name = ?",
        (name,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_degree(cur: sqlite3.Cursor, title: Any) -> Optional[int]:
    degree_title = normalize_text(title)
    if not degree_title:
        return None

    cur.execute(
        "INSERT OR IGNORE INTO degree (title) VALUES (?)",
        (degree_title,),
    )
    cur.execute(
        "SELECT degree_id FROM degree WHERE title = ?",
        (degree_title,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_role(cur: sqlite3.Cursor, title: Any) -> Optional[int]:
    role_title = normalize_text(title)
    if not role_title:
        return None

    cur.execute(
        "INSERT OR IGNORE INTO role (title) VALUES (?)",
        (role_title,),
    )
    cur.execute(
        "SELECT role_id FROM role WHERE title = ?",
        (role_title,),
    )
    row = cur.fetchone()
    return row[0] if row else None


def find_candidate(
    cur: sqlite3.Cursor,
    profile: dict[str, Any],
    location_id: Optional[int] = None,
) -> Optional[int]:
    """
    Find an existing candidate without relying on candidate_name because names
    are not guaranteed to be unique.
    """
    for field in ("email", "linkedin_url", "github", "phone_number"):
        value = normalize_text(profile.get(field))
        if not value:
            continue

        cur.execute(
            f"SELECT candidate_id FROM candidate WHERE {field} = ?",
            (value,),
        )
        row = cur.fetchone()
        if row:
            return row[0]

    # Some extracted profiles have no contact identifiers. Use the combination
    # below as a fallback so rerunning the same JSON remains idempotent.
    # This is deliberately weaker than email/LinkedIn/GitHub/phone matching.
    name = normalize_text(profile.get("candidate_name"))
    target_role = normalize_text(profile.get("target_role"))
    if name:
        cur.execute(
            """
            SELECT candidate_id
              FROM candidate
             WHERE candidate_name = ?
               AND target_role IS ?
               AND location_id IS ?
             LIMIT 1
            """,
            (name, target_role, location_id),
        )
        row = cur.fetchone()
        if row:
            return row[0]

    return None


def insert_or_update_candidate(
    cur: sqlite3.Cursor,
    profile: dict[str, Any],
) -> int:
    location_id = get_or_create_location(cur, profile.get("location"))
    candidate_id = find_candidate(cur, profile, location_id)

    fields = {
        "candidate_name": normalize_text(profile.get("candidate_name")),
        "target_role": normalize_text(profile.get("target_role")),
        "phone_number": normalize_text(profile.get("phone_number")),
        "email": normalize_text(profile.get("email")),
        "linkedin_url": normalize_text(profile.get("linkedin_url")),
        "github": normalize_text(profile.get("github")),
        "years_of_experience": (
            str(profile["years_of_experience"]).strip()
            if profile.get("years_of_experience") is not None
            else None
        ),
        "location_id": location_id,
    }

    if candidate_id is None:
        cur.execute(
            """
            INSERT INTO candidate (
                candidate_name,
                target_role,
                phone_number,
                email,
                linkedin_url,
                github,
                years_of_experience,
                location_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(fields.values()),
        )
        return cur.lastrowid

    # Fill missing scalar fields but do not overwrite existing values with null.
    # Non-null values from a later resume version are allowed to refresh the
    # candidate's current profile fields.
    cur.execute(
        """
        UPDATE candidate
           SET candidate_name = COALESCE(?, candidate_name),
               target_role = COALESCE(?, target_role),
               phone_number = COALESCE(?, phone_number),
               email = COALESCE(?, email),
               linkedin_url = COALESCE(?, linkedin_url),
               github = COALESCE(?, github),
               years_of_experience = COALESCE(?, years_of_experience),
               location_id = COALESCE(?, location_id)
         WHERE candidate_id = ?
        """,
        (
            fields["candidate_name"],
            fields["target_role"],
            fields["phone_number"],
            fields["email"],
            fields["linkedin_url"],
            fields["github"],
            fields["years_of_experience"],
            fields["location_id"],
            candidate_id,
        ),
    )
    return candidate_id


def import_skills(
    cur: sqlite3.Cursor,
    candidate_id: int,
    skills: Any,
) -> int:
    count = 0
    for skill in skills or []:
        skill_id = get_or_create_skill(cur, skill)
        if skill_id is None:
            continue

        cur.execute(
            """
            INSERT OR IGNORE INTO candidate_skill (candidate_id, skill_id)
            VALUES (?, ?)
            """,
            (candidate_id, skill_id),
        )
        count += cur.rowcount
    return count


def import_education(
    cur: sqlite3.Cursor,
    candidate_id: int,
    education: Any,
) -> int:
    count = 0

    for item in education or []:
        institution_id = get_or_create_institution(
            cur,
            item.get("insitution_name") or item.get("institution_name"),
        )
        degree_id = get_or_create_degree(
            cur,
            item.get("education_level"),
        )

        graduation_year_raw = clean(item.get("graduation_year"))
        graduation_year = None
        if graduation_year_raw and re.fullmatch(r"\d{4}", graduation_year_raw):
            graduation_year = int(graduation_year_raw)

        # Education has no supplied natural key, so use candidate + institution
        # + degree + graduation year as a practical deduplication key.
        cur.execute(
            """
            SELECT education_id
              FROM education
             WHERE candidate_id = ?
               AND institution_id IS ?
               AND degree_id IS ?
               AND graduation_year IS ?
            LIMIT 1
            """,
            (
                candidate_id,
                institution_id,
                degree_id,
                graduation_year,
            ),
        )
        row = cur.fetchone()

        if row:
            continue

        cur.execute(
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
                graduation_year,
            ),
        )
        count += 1

    return count


def import_employment(
    cur: sqlite3.Cursor,
    candidate_id: int,
    experience: Any,
) -> int:
    count = 0

    for item in experience or []:
        company_id = get_or_create_company(
            cur,
            item.get("company_name"),
            item.get("company_location"),
        )
        role_id = get_or_create_role(cur, item.get("role_title"))

        start_date = normalize_date(item.get("start_date"))
        end_date = normalize_date(item.get("end_date"))

        if start_date and end_date and end_date < start_date:
            raise ValueError(
                f"Employment end date precedes start date: "
                f"{item.get('start_date')!r} -> {item.get('end_date')!r}"
            )

        is_current = 1 if item.get("is_current") is True else 0
        description = clean(item.get("role_description"))

        # Practical natural key for one candidate's employment record.
        # Description is intentionally excluded so a later resume version can
        # refresh the same job rather than creating a duplicate employment row.
        cur.execute(
            """
            SELECT employment_id
              FROM employment
             WHERE candidate_id = ?
               AND company_id IS ?
               AND role_id IS ?
               AND start_date IS ?
             LIMIT 1
            """,
            (
                candidate_id,
                company_id,
                role_id,
                start_date,
            ),
        )
        row = cur.fetchone()

        if row:
            employment_id = row[0]
            cur.execute(
                """
                UPDATE employment
                   SET role_description = COALESCE(?, role_description),
                       end_date = COALESCE(?, end_date),
                       is_current = ?
                 WHERE employment_id = ?
                """,
                (description, end_date, is_current, employment_id),
            )
            continue

        cur.execute(
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
                description,
                start_date,
                end_date,
                is_current,
            ),
        )
        count += 1

    return count


def import_profiles(db_path: str, json_path: str) -> None:
    json_file = Path(json_path)
    if not json_file.exists():
        raise FileNotFoundError(f"JSON file not found: {json_file}")

    with json_file.open("r", encoding="utf-8") as fh:
        profiles = json.load(fh)

    if not isinstance(profiles, list):
        raise ValueError("Expected the JSON root to be an array of candidate profiles.")

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")

    totals = {
        "profiles": 0,
        "skills_linked": 0,
        "education_inserted": 0,
        "employment_inserted": 0,
    }

    try:
        with con:
            cur = con.cursor()

            for profile in profiles:
                if not isinstance(profile, dict):
                    continue

                candidate_id = insert_or_update_candidate(cur, profile)

                totals["skills_linked"] += import_skills(
                    cur,
                    candidate_id,
                    profile.get("skills"),
                )
                totals["education_inserted"] += import_education(
                    cur,
                    candidate_id,
                    profile.get("education"),
                )
                totals["employment_inserted"] += import_employment(
                    cur,
                    candidate_id,
                    profile.get("experience"),
                )

                totals["profiles"] += 1

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

    print("Import complete.")
    print(f"Profiles processed:       {totals['profiles']}")
    print(f"New skill links:          {totals['skills_linked']}")
    print(f"New education rows:       {totals['education_inserted']}")
    print(f"New employment rows:      {totals['employment_inserted']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import parsed resumes JSON into the SQLite database."
    )
    parser.add_argument(
        "database",
        help="Path to the SQLite database file.",
    )
    parser.add_argument(
        "json_file",
        help="Path to parsed_resumes.json.",
    )
    args = parser.parse_args()

    import_profiles(args.database, args.json_file)


if __name__ == "__main__":
    main()
