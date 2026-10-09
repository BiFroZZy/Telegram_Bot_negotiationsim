CREATE TABLE IF NOT EXISTS attempts (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username TEXT,
    scenario_key TEXT NOT NULL,
    scenario_title TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    score SMALLINT,
    review TEXT,
    transcript JSONB
);
CREATE INDEX IF NOT EXISTS idx_attempts_user_id ON attempts(user_id);

CREATE TABLE IF NOT EXISTS user_streaks (
    user_id BIGINT PRIMARY KEY,
    current_streak INTEGER NOT NULL DEFAULT 0,
    longest_streak INTEGER NOT NULL DEFAULT 0,
    last_active_date DATE
);
