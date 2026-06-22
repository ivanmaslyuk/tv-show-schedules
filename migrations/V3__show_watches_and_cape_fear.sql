CREATE TABLE show_watches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    show_id INTEGER NOT NULL REFERENCES shows(id) ON DELETE CASCADE,
    watching BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_show_watch_user_show UNIQUE (user_id, show_id)
);

INSERT INTO shows (id, title, release_date) VALUES
(120001, 'Cape Fear', '2026-06-05'),
(130001, 'House of the Dragon', '2022-08-21');

INSERT INTO seasons (id, number, show_id, release_date) VALUES
(120101, 1, 120001, '2026-06-05'),
(130101, 1, 130001, '2022-08-21'),
(130102, 2, 130001, '2024-06-16'),
(130103, 3, 130001, '2026-06-21');

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
(120210, 'The Executioners', 10, 120101, '2026-07-31'),
-- House of the Dragon S1
(130201, 'The Heirs of the Dragon', 1, 130101, '2022-08-21'),
(130202, 'The Rogue Prince', 2, 130101, '2022-08-28'),
(130203, 'Second of His Name', 3, 130101, '2022-09-04'),
(130204, 'King of the Narrow Sea', 4, 130101, '2022-09-11'),
(130205, 'We Light the Way', 5, 130101, '2022-09-18'),
(130206, 'The Princess and the Queen', 6, 130101, '2022-09-25'),
(130207, 'Driftmark', 7, 130101, '2022-10-02'),
(130208, 'The Lord of the Tides', 8, 130101, '2022-10-09'),
(130209, 'The Green Council', 9, 130101, '2022-10-16'),
(130210, 'The Black Queen', 10, 130101, '2022-10-23'),
-- House of the Dragon S2
(130211, 'A Son for a Son', 1, 130102, '2024-06-16'),
(130212, 'Rhaenyra the Cruel', 2, 130102, '2024-06-23'),
(130213, 'The Burning Mill', 3, 130102, '2024-06-30'),
(130214, 'The Red Dragon and the Gold', 4, 130102, '2024-07-07'),
(130215, 'Regent', 5, 130102, '2024-07-14'),
(130216, 'Smallfolk', 6, 130102, '2024-07-21'),
(130217, 'The Red Sowing', 7, 130102, '2024-07-28'),
(130218, 'The Queen Who Ever Was', 8, 130102, '2024-08-04'),
-- House of the Dragon S3
(130219, 'The Flame Monster', 1, 130103, '2026-06-21');

SELECT setval(pg_get_serial_sequence('shows', 'id'), (SELECT MAX(id) FROM shows));
SELECT setval(pg_get_serial_sequence('seasons', 'id'), (SELECT MAX(id) FROM seasons));
SELECT setval(pg_get_serial_sequence('episodes', 'id'), (SELECT MAX(id) FROM episodes));
