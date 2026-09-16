-- EDA

-- How many candidates are in the database
SELECT count(*) FROM candidate;

-- Which job roles are the most popular target_role
SELECT
    target_role,
    COUNT(*) AS popularity
FROM candidate
WHERE target_role IS NOT NULL
GROUP BY target_role
ORDER BY popularity DESC;

-- What are the most popular job titles among the candidates
SELECT
    r.title AS job_title,
    COUNT(DISTINCT e.candidate_id) AS candidate_count
FROM employment e
JOIN role r
    ON e.role_id = r.role_id
GROUP BY r.role_id, r.title
ORDER BY candidate_count DESC
LIMIT 10;

-- Which are the most common skills among the candidates
SELECT
    s.skill_title,
    COUNT(DISTINCT cs.candidate_id) AS candidate_count
FROM skill s
JOIN candidate_skill cs
    ON s.skill_id = cs.skill_id
GROUP BY s.skill_id, s.skill_title
ORDER BY candidate_count DESC;

-- Which degrees do most candidates hold
SELECT
    d.title AS degree,
    COUNT(DISTINCT e.candidate_id) AS candidate_count
FROM education e
JOIN degree d
    ON e.degree_id = d.degree_id
GROUP BY d.degree_id, d.title
ORDER BY candidate_count DESC;

-- Which location most candidates come from
SELECT
    l.location_name,
    COUNT(*) AS candidate_count
FROM candidate c
JOIN location l
    ON c.location_id = l.location_id
GROUP BY l.location_id, l.location_name
ORDER BY candidate_count DESC;

-- Degree types by popularity 
SELECT
    CASE
        WHEN LOWER(d.title) LIKE '%doctor%'
          OR LOWER(d.title) LIKE '%phd%'
          OR LOWER(d.title) LIKE '%doctoral%'
            THEN 'Doctorate'

        WHEN LOWER(d.title) LIKE '%master%'
          OR LOWER(d.title) LIKE '%mba%'
          OR LOWER(d.title) LIKE '%ms%'
          OR LOWER(d.title) LIKE '%m.s.%'
          OR LOWER(d.title) LIKE '%ma%'
          OR LOWER(d.title) LIKE '%m.a.%'
            THEN 'Master''s'

        WHEN LOWER(d.title) LIKE '%bachelor%'
          OR LOWER(d.title) LIKE '%b.s.%'
          OR LOWER(d.title) LIKE '%b.a.%'
          OR LOWER(d.title) LIKE '%bba%'
          OR LOWER(d.title) LIKE '%b.sc%'
            THEN 'Bachelor''s'

        WHEN LOWER(d.title) LIKE '%associate%'
          OR LOWER(d.title) LIKE '%a.a.%'
          OR LOWER(d.title) LIKE '%a.s.%'
            THEN 'Associate''s'

        WHEN LOWER(d.title) LIKE '%diploma%'
            THEN 'Diploma'

        WHEN LOWER(d.title) LIKE '%certificate%'
            THEN 'Certificate'

        ELSE 'Other'
    END AS degree_level,

    COUNT(DISTINCT e.candidate_id) AS candidate_count

FROM education e
JOIN degree d
    ON e.degree_id = d.degree_id

GROUP BY degree_level
ORDER BY candidate_count DESC;

-- Where most candidates come from
SELECT 
    l.location_name,
    COUNT(*) AS candidate_count
FROM candidate c
JOIN location l
    ON c.location_id = l.location_id
GROUP BY l.location_name
ORDER BY candidate_count DESC;

-- Which company appears more frequently in the database
SELECT
    c.company_name,
    COUNT(DISTINCT e.candidate_id) AS candidate_count
FROM company c
JOIN employment e
    ON c.company_id = e.company_id
GROUP BY c.company_id, c.company_name
ORDER BY candidate_count DESC;





