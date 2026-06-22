CREATE TABLE show_watches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    show_id INTEGER NOT NULL REFERENCES shows(id) ON DELETE CASCADE,
    watching BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_show_watch_user_show UNIQUE (user_id, show_id)
);

INSERT INTO shows (id, title, release_date) VALUES
(120001, 'Cape Fear', '2026-06-05');

INSERT INTO seasons (id, number, show_id, release_date) VALUES
(120101, 1, 120001, '2026-06-05');

INSERT INTO episodes (id, title, number, season_id, release_date) VALUES
(120201, 'Fingers & Toes', 1, 120101, '2026-06-05'),
(120202, 'Why Would I Want to Hurt You?', 2, 120101, '2026-06-05'),
(120203, 'Phantom Sensations', 3, 120101, '2026-06-12'),
(120204, 'Pierced', 4, 120101, '2026-06-19'),
(120205, 'Faith', 5, 120101, '2026-06-26'),
(120206, 'Possum', 6, 120101, '2026-07-03'),
(120207, 'Mongrel', 7, 120101, '2026-07-10'),
(120208, 'Los tiempos de Dios son Perfectos', 8, 120101, '2026-07-17'),
(120209, 'The Scar', 9, 120101, '2026-07-24'),
(120210, 'The Executioners', 10, 120101, '2026-07-31');

SELECT setval(pg_get_serial_sequence('shows', 'id'), (SELECT MAX(id) FROM shows));
SELECT setval(pg_get_serial_sequence('seasons', 'id'), (SELECT MAX(id) FROM seasons));
SELECT setval(pg_get_serial_sequence('episodes', 'id'), (SELECT MAX(id) FROM episodes));
