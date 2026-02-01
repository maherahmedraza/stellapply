-- name: CreateResume :one
INSERT INTO resumes (
    user_id,
    name,
    template_id,
    content,
    is_primary
) VALUES (
    $1, $2, $3, $4, $5
) RETURNING *;

-- name: GetResumeByID :one
SELECT * FROM resumes
WHERE id = $1 LIMIT 1;

-- name: ListResumesByUserID :many
SELECT * FROM resumes
WHERE user_id = $1
ORDER BY created_at DESC;

-- name: UpdateResume :one
UPDATE resumes
SET
    name = COALESCE($2, name),
    template_id = COALESCE($3, template_id),
    content = COALESCE($4, content),
    is_primary = COALESCE($5, is_primary),
    ats_score = COALESCE($6, ats_score),
    analysis_results = COALESCE($7, analysis_results),
    analyzed_at = COALESCE($8, analyzed_at),
    updated_at = NOW(),
    version = version + 1
WHERE id = $1
RETURNING *;

-- name: DeleteResume :exec
DELETE FROM resumes
WHERE id = $1;
