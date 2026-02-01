-- name: CreateApplication :one
INSERT INTO applications (
    user_id, job_id, resume_id, resume_snapshot, cover_letter_id,
    cover_letter_snapshot, answers, status, submission_mode,
    submitted_at, submission_screenshot_url, error_message,
    retry_count, timeline
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14
) RETURNING *;

-- name: GetApplicationByID :one
SELECT * FROM applications WHERE id = $1;

-- name: ListApplicationsByUserID :many
SELECT * FROM applications WHERE user_id = $1 ORDER BY created_at DESC;

-- name: UpdateApplication :one
UPDATE applications SET
    resume_id = $2,
    resume_snapshot = $3,
    cover_letter_id = $4,
    cover_letter_snapshot = $5,
    answers = $6,
    status = $7,
    submission_mode = $8,
    submitted_at = $9,
    submission_screenshot_url = $10,
    error_message = $11,
    retry_count = $12,
    timeline = $13,
    updated_at = NOW()
WHERE id = $1 RETURNING *;

-- name: DeleteApplication :exec
DELETE FROM applications WHERE id = $1;
