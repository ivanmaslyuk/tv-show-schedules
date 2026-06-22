# TV Show Schedules

FastAPI backend for tracking TV show release schedules with async SQLAlchemy, Flyway migrations, and GitHub Actions CI.

## Start Locally

This project is intended to run through Docker Compose.

1. Start the stack:

```bash
docker compose up -d
```

2. Open the API once the containers are up:

- App: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`

The Compose stack starts PostgreSQL, applies the Flyway migrations, and then boots the FastAPI app with the local source mounted into the container.

## Basic API Usage

The API uses bearer-token authentication for protected routes. Public read endpoints such as listing shows do not require authentication. The first successfully registered user becomes an admin and can create or update shows, seasons, and episodes. Logged-in users can also mark shows as watched and list their nearest upcoming episodes.

Create an account:

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123"
  }'
```

Log in and get a bearer token:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123"
  }'
```

Create a show with that token:

```bash
curl -X POST http://localhost:8000/shows \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example Show",
    "release_date": "2024-01-01"
  }'
```

List shows:

```bash
curl http://localhost:8000/shows
```

Mark an episode as viewed:

```bash
curl -X POST http://localhost:8000/shows/1/seasons/1/episodes/1/view \
  -H "Authorization: Bearer <access_token>"
```

Mark a show as watched:

```bash
curl -X POST http://localhost:8000/shows/1/watch \
  -H "Authorization: Bearer <access_token>"
```

List the nearest upcoming episode for each watched show:

```bash
curl http://localhost:8000/shows/upcoming \
  -H "Authorization: Bearer <access_token>"
```

## GitHub Actions

The GitHub Actions workflow currently runs two jobs:

- `lint`: checks the codebase with `ruff`.
- `tests`: provisions PostgreSQL, installs the project, runs non-integration tests, applies Flyway migrations, and then runs the integration test suite.

The workflow runs on every pull request and on pushes to `master`.

## Run Tests

Run tests inside the `api` container:

```bash
docker compose exec api pytest -m "not integration"
docker compose exec api pytest -m integration
```

To run a single test or file, keep the command inside the container as well:

```bash
docker compose exec api pytest tests/test_unit.py::test_password_roundtrip
```
