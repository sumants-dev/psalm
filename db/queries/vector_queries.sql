-- name: GetNearestVectors :many
SELECT content, embedding <-> $1 AS distance
FROM vector_store
ORDER BY 2
LIMIT $2;

-- name: GetNearestVectorsGivenCondition :many
SELECT content, embedding <-> $1 AS distance
FROM vector_store
WHERE metadata @> $3::JSONB
ORDER BY 2
LIMIT $2;

-- name: CreateVector :one
INSERT INTO vector_store (
  content, metadata, embedding
) VALUES (
  $1, $2, $3
)
RETURNING id;

-- name: DeleteVector :exec
DELETE FROM vector_store
WHERE id = $1;