-- name: CreateUser :one
INSERT INTO users (
    email_encrypted,
    email_hash,
    password_hash,
    status,
    governance_metadata
) VALUES (
    $1, $2, $3, $4, $5
) RETURNING *;

-- name: GetUserByEmailHash :one
SELECT * FROM users
WHERE email_hash = $1 LIMIT 1;

-- name: GetUserByID :one
SELECT * FROM users
WHERE id = $1 LIMIT 1;

-- name: UpdateUser :exec
UPDATE users
SET 
    email_hash = $2,
    email_encrypted = $3,
    status = $4,
    governance_metadata = $5,
    updated_at = NOW()
WHERE id = $1;

-- name: UpdateUserStatus :exec
UPDATE users
SET status = $2, updated_at = NOW()
WHERE id = $1;

-- name: DeleteUser :exec
DELETE FROM users
WHERE id = $1;

-- name: CountUsers :one
SELECT count(*) FROM users;
