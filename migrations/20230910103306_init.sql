-- +goose Up
-- +goose StatementBegin
SELECT 'up SQL query';
CREATE EXTENSION vector;
CREATE TABLE node (
    id bigserial primary key,
    content text not null,
    metadata JSONB not null,
    embedding vector(384) not null --Using MINI v12 embedding
);
CREATE INDEX metadata_gin ON node USING gin (metadata jsonb_path_ops);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
SELECT 'down SQL query';
DROP INDEX metadata_gin;
DROP TABLE node;
DROP EXTENSION vector;
-- +goose StatementEnd
