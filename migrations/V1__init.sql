CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE shows (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_date DATE NOT NULL
);

CREATE TABLE seasons (
    id SERIAL PRIMARY KEY,
    number INTEGER NOT NULL,
    show_id INTEGER NOT NULL REFERENCES shows(id) ON DELETE CASCADE,
    release_date DATE NOT NULL,
    CONSTRAINT uq_season_show_number UNIQUE (show_id, number)
);

CREATE TABLE episodes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    number INTEGER NOT NULL,
    season_id INTEGER NOT NULL REFERENCES seasons(id) ON DELETE CASCADE,
    release_date DATE NOT NULL,
    CONSTRAINT uq_episode_season_number UNIQUE (season_id, number)
);

CREATE TABLE views (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    episode_id INTEGER NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
    viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_view_user_episode UNIQUE (user_id, episode_id)
);

