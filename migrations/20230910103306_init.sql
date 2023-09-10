-- +goose Up
-- +goose StatementBegin
SELECT 'up SQL query';
CREATE EXTENSION vector;
CREATE TABLE vector_store (
    id bigserial primary key,
    content text,
    metadata JSONB,
    embedding vector(384) --Using MINI v12 embedding
);
CREATE INDEX metadata_gin ON vector_store USING gin (metadata jsonb_path_ops);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
SELECT 'down SQL query';
DROP INDEX metadata_gin;
DROP TABLE vector_store;
DROP EXTENSION vector;
-- +goose StatementEnd
