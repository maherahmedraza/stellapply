-- name: CreatePersona :one
INSERT INTO personas (
    user_id,
    full_name_encrypted,
    preferred_name,
    pronouns,
    location,
    work_authorization,
    experience,
    education,
    skills,
    certifications,
    preferences,
    personality,
    behavioral_stories,
    completeness_score,
    completeness_breakdown
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
) RETURNING id, user_id, full_name_encrypted, preferred_name, pronouns, location, work_authorization, experience, education, skills, certifications, preferences, personality, behavioral_stories, completeness_score, completeness_breakdown, version, created_at, updated_at;

-- name: UpdatePersona :one
UPDATE personas
SET
    full_name_encrypted = COALESCE($2, full_name_encrypted),
    preferred_name = COALESCE($3, preferred_name),
    pronouns = COALESCE($4, pronouns),
    location = COALESCE($5, location),
    work_authorization = COALESCE($6, work_authorization),
    experience = COALESCE($7, experience),
    education = COALESCE($8, education),
    skills = COALESCE($9, skills),
    certifications = COALESCE($10, certifications),
    preferences = COALESCE($11, preferences),
    personality = COALESCE($12, personality),
    behavioral_stories = COALESCE($13, behavioral_stories),
    completeness_score = COALESCE($14, completeness_score),
    completeness_breakdown = COALESCE($15, completeness_breakdown),
    updated_at = NOW(),
    version = version + 1
WHERE user_id = $1
RETURNING id, user_id, full_name_encrypted, preferred_name, pronouns, location, work_authorization, experience, education, skills, certifications, preferences, personality, behavioral_stories, completeness_score, completeness_breakdown, version, created_at, updated_at;

-- name: GetPersonaByUserID :one
SELECT id, user_id, full_name_encrypted, preferred_name, pronouns, location, work_authorization, experience, education, skills, certifications, preferences, personality, behavioral_stories, completeness_score, completeness_breakdown, version, created_at, updated_at FROM personas
WHERE user_id = $1 LIMIT 1;
