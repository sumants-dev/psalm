-- name: CreateAPIKey :one
INSERT INTO pontus_api_keys (username, password)
VALUES ($1, $2)
RETURNING *;

-- name: CreateAPIKeyWithRole :one
INSERT INTO pontus_api_keys (username, password, role)
VALUES ($1, $2, $3)
RETURNING *;

-- name: DeleteAPIKeyByUsername :one
DELETE FROM pontus_api_keys WHERE username = $1 RETURNING *;

-- name: GetAPIKeyByUsername :one
SELECT * FROM pontus_api_keys WHERE username = $1;
