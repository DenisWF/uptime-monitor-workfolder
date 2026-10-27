CREATE TABLE IF NOT EXISTS targets (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    url  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS checks (
    id          BIGSERIAL PRIMARY KEY,
    target_id   INT NOT NULL REFERENCES targets(id) ON DELETE CASCADE,
    checked_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    status_code INT,
    response_ms INT,
    is_up       BOOLEAN NOT NULL,
    error       TEXT
);

CREATE INDEX IF NOT EXISTS idx_checks_target_time
    ON checks (target_id, checked_at DESC);