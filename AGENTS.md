# AGENTS.md

## Project Overview

This repository is a Python 3.11 FastAPI backend for tracking TV shows,
seasons, episode release dates, and per-user viewing state. It uses async
SQLAlchemy with PostgreSQL, Pydantic v2 schemas, bearer-token authentication,
Flyway SQL migrations, pytest, and Docker Compose.

## Repository Map

- `app/main.py`: FastAPI application, route handlers, and nested-resource
  lookup helpers.
- `app/auth.py`: PBKDF2 password hashing, JWT creation/validation, and auth
  dependencies.
- `app/models.py`: SQLAlchemy declarative models and relationships.
- `app/schemas.py`: Pydantic request and response models.
- `app/database.py`: async engine, session factory, and FastAPI dependency.
- `app/config.py`: environment-backed settings and local defaults.
- `migrations/`: versioned Flyway SQL migrations and seed data.
- `tests/test_unit.py`: tests that do not require a database.
- `tests/test_integration.py`: API tests against a database.
- `tests/conftest.py`: async clients, database lifecycle, users, auth headers,
  and shared domain fixtures.
- `.github/workflows/ci.yml`: authoritative CI commands and environment.

## Setup and Common Commands

Before starting anything, check whether the Compose stack is already running:

```bash
docker compose ps
```

If `api` and `db` are already running and `db` is healthy, reuse the existing
stack. Do not run `docker compose up` again or rebuild it unnecessarily. If the
services are not running, start them with:

```bash
docker compose up -d
```

Use `docker compose up -d --build` only when the image must change, such as
after editing `Dockerfile`, `Dockerfile.dev`, or Python dependencies in
`pyproject.toml`. The API is available at `http://localhost:8000`, with
interactive docs at `http://localhost:8000/docs`.

Run tests inside the existing API container. Do not invoke pytest with the host
or local `.venv` interpreter; this project expects the Compose environment and
its database hostname/network:

```bash
docker compose exec api pytest -m "not integration"
docker compose exec api pytest -m integration
```

`docker compose exec api ...` is the preferred Compose-aware form of Docker's
`exec`; it avoids hardcoding the generated container name. If direct Docker is
required, identify the current container with `docker compose ps` before using
`docker exec <api-container> pytest ...`.

To run a single test or file, keep the command in the container as well:

```bash
docker compose exec api pytest tests/test_unit.py::test_password_roundtrip
```

**Safety warning:** `db_session` in `tests/conftest.py` calls `drop_all()` and
`create_all()`. Never point integration tests at a shared, staging, production,
or otherwise valuable database. Integration tests recreate application tables
inside the Compose database and remove Flyway's seeded application data. To
restore a clean seeded development database afterward, recreate the stack:

```bash
docker compose down
docker compose up -d
```

## Implementation Conventions

- Keep all database I/O async. Route handlers and helpers that access the
  database should use `AsyncSession` and `await` SQLAlchemy operations.
- Acquire sessions through `Depends(get_session)` in application code. Tests
  replace this dependency with a fixture-scoped session.
- Use SQLAlchemy 2.x query forms such as `select(...)`, `session.scalar(...)`,
  and `session.execute(...)`; do not introduce the legacy query API.
- Define request and response contracts in `app/schemas.py`. ORM-backed
  response models need `ConfigDict(from_attributes=True)` and should be
  returned through `model_validate(...)`.
- Preserve nested-resource ownership checks. A season URL must verify that the
  season belongs to `show_id`, and an episode URL must verify both its season
  and show ancestry. Reuse or extend the `get_*_or_404` helpers.
- Public reads are currently unauthenticated. Show, season, and episode writes
  require `require_admin`; viewing-state routes require `get_current_user`.
- The first successfully registered user becomes an administrator. Treat any
  change to that behavior as an authentication-policy change and test it.
- After writes, commit explicitly. Refresh newly created or updated ORM objects
  before validating response schemas when server-generated fields are needed.
- Keep API status codes and error details consistent with neighboring routes:
  `201` for creation, `204` for deletion, `401` for authentication failures,
  `403` for insufficient privilege, `404` for missing nested resources, and
  `409` for conflicts such as an existing email.
- Follow the existing straightforward typed style. Add comments only where the
  reason for a non-obvious choice would otherwise be lost.

## Database Changes

- Keep `app/models.py` and the SQL schema in `migrations/` aligned.
- Never edit an applied Flyway migration. Add the next migration using the
  `V<number>__short_description.sql` naming convention.
- Preserve foreign-key cascade behavior and uniqueness constraints unless the
  feature explicitly changes those invariants.
- When seed rows use explicit integer IDs, account for PostgreSQL sequence
  values so later inserts cannot collide with seeded records.
- Production and Compose startup use Flyway. `Base.metadata.create_all()` is a
  test mechanism, not the application migration strategy.

## Testing Expectations

- Add focused unit tests for pure helpers, especially auth and validation logic.
- Add integration coverage for route behavior, persistence, authorization,
  response payloads, and parent-child boundary checks.
- Mark every database-dependent test with `pytest.mark.integration`; the module
  may apply the marker globally as `tests/test_integration.py` currently does.
- Prefer the existing fixtures (`integration_client`, users, auth headers, and
  `show_data`) over rebuilding common setup in each test.
- Test both the successful path and meaningful denial paths (`401`, `403`,
  `404`, or `409`) when changing an endpoint.
- Before any test command, run `docker compose ps`. Reuse a running, healthy
  stack; only run `docker compose up -d` when services are missing or stopped,
  and add `--build` only when the image needs rebuilding.
- At minimum, run `docker compose exec api pytest -m "not integration"` after
  every change. Run `docker compose exec api pytest -m integration` for API,
  model, schema, auth, or migration changes.
- Never run this repository's tests with the host Python or `.venv`; execute
  them inside the Compose `api` container so configuration, networking, and
  dependencies match the application environment.

## Change Discipline

- Keep changes scoped; do not refactor unrelated routes while implementing a
  feature or fix.
- Do not commit local artifacts or secrets such as `.env`, `.venv`, IDE files,
  caches, database data, or platform metadata.
- If behavior, setup, or operational commands change, update `README.md`, this
  file, and CI or Compose configuration as applicable.
- Before handing off, inspect `git diff`, report which checks ran, and call out
  any tests that could not be run.
