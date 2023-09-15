-- name: GetNearestNodes :many
SELECT content, embedding <-> $1 AS distance
FROM node
ORDER BY 2
LIMIT $2;

-- name: GetNearestNodesGivenCondition :many
SELECT content, embedding <-> $1 AS distance
FROM node
WHERE metadata @> $3::JSONB
ORDER BY 2
LIMIT $2;