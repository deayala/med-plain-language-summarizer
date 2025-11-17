# Repository Guidelines

## Project Structure & Module Organization
`app/` contains the FastAPI surface (entrypoint `app/main.py`, config, generator, and `app/tests/`). Shared utilities live in `src/`, automation helpers in `scripts/`, and classifier artifacts in `models/`. Research artifacts land in `artifacts/`, evaluation outputs in `results/`, and supporting notebooks in `notebooks/`. Terraform lives in `infra/`, and `docker-compose*.yml` plus the `Makefile` coordinate local and remote runtime flows.

## Build, Test, and Development Commands
- `make install` — create `.venv/` and install dependencies.
- `make serve` — run `uvicorn app.main:app --reload` on `localhost:8080`.
- `make test` / `tox -e test_app` — execute pytest.
- `make checks` — run `ruff` and `mypy` via the `checks` tox env.
- `make docker-build-api`, `make up`, `make down`, and `scripts/smoke_test.sh` — build the API image, spin up Compose, and hit `/health` + `/summarize`.

## Coding Style & Naming Conventions
Use 4-space indentation, `snake_case` identifiers, and type hints on public functions. Pydantic DTOs belong in `app/schemas.py`, routers stay in `app/main.py`, and HF endpoint helpers remain isolated in `app/generator.py`. Run `ruff check app src` to enforce formatting, import order, and docstring tone; fix violations locally before committing. `mypy` (Python 3.11 per `mypy.ini`) expects explicit types on shared payloads, so prefer `TypedDict` or dataclasses when passing data between modules.

## Testing Guidelines
Mirror production modules with pytest files (`app/tests/test_generator.py`, `test_health.py`, etc.). Parametrize cases to cover DRY_RUN vs. HF-endpoint paths so CI stays backend-agnostic. Always run `make test && make checks` before opening a PR; failures must reproduce via `tox -e test_app` inside a clean virtualenv.

## Commit & Pull Request Guidelines
Because this bundle lacks Git history, default to Conventional Commits (`feat:`, `fix:`, `chore:`) and keep each commit scoped to a passing logical change. PRs should include a summary, linked issue, validation evidence (pytest output or `curl` trace), and callouts for infrastructure touchpoints.

## Security & Deployment Notes
Secrets belong in `.env` (clone from `.env.example`) and are loaded by `app/config.py`; never store credentials under version control. Before `make ec2-deploy`, push the latest image via `make ecr-push-api` and review `terraform -chdir=infra plan`. Keep `docker compose ps` clean locally so automation scripts can detect healthy services, and provision IAM roles with only the permissions needed for logging/metrics plus the managed Hugging Face endpoint.
