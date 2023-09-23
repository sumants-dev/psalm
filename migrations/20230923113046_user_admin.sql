-- +goose Up
-- +goose StatementBegin
SELECT 'up SQL query';

CREATE TYPE roletype AS ENUM ('user', 'admin');
CREATE TABLE IF NOT EXISTS pontus_api_keys (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role roletype NOT NULL DEFAULT 'user',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
SELECT 'down SQL query';

DROP TABLE IF EXISTS api_keys;
DROP TYPE roletype;
-- +goose StatementEnd
