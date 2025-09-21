# TherapyBot

A therapy-focused conversational assistant providing text and voice chat, wellness logging, analytics dashboards, and escalation flows for clinicians.

This repository contains a full-stack demo of TherapyBot with a FastAPI backend, React frontend, Celery background workers, and integrations with Google Vertex AI (with an Ollama/local LLM fallback documented).

## At a glance
- Backend: FastAPI (Python), Celery for background tasks, Alembic migrations.
- Frontend: React SPA (JavaScript) with a Dashboard for patients, consultants and admins.
- AI: Google Vertex AI integration (primary), Ollama/local LLM fallback documented.
- Data: PostgreSQL for persistent storage and Redis for Celery/queues.
- Dev infra: Docker Compose, helper scripts in `scripts/`.

## Key features
- AI-driven chat (text + voice) endpoints (`/messages/chat`, `/messages/voice-chat`).
- Wellness logging and trend visualizations on the Dashboard.
- Escalation and audit logging workflows for high-risk conversations.
- Consultant and admin analytics routes and UI.
- Tests: pytest for backend, Playwright for E2E frontend tests with example reports included.

## Repository layout (high level)
- `backend/` — FastAPI app, routes, Celery worker, tests, Dockerfile.
- `frontend/` — React app, components, Playwright config and generated reports.
- `docs/` — Setup guides, AI integration notes, testing guidance and troubleshooting.
- `scripts/` — Helpful shell scripts for checks and Vertex AI setup.
- `infra/` and `docker-compose*.yml` — local dev and deployment compose files.

## Quickstart (development)
Prerequisites: Docker/Docker Compose, Node.js (for local frontend dev), Python 3.11+ (for local backend dev).

1. Copy the example env and fill secrets:

```powershell
cp .env.example .env
# Then edit .env and place any secret files under ./secrets/
```

2. Place Google Cloud service account JSON at `./secrets/gcp-credentials.json` (if using Vertex AI).

3. Start services with Docker Compose (recommended for local dev):

```powershell
# From repository root
docker compose up --build
```

4. Backend will be available at `http://localhost:8000` (unless changed in `.env`). Frontend at `http://localhost:3000`.

Alternatively run services individually during development:
- Backend: create a Python venv, install `requirements.txt`, and run `uvicorn backend.app.main:app --reload` (see `backend/README` if present).
- Frontend: `cd frontend && npm install && npm start`.

## Important environment variables
Use `.env.example` as the canonical list. Key variables includes (copy these into your `.env`):

- FRONTEND_PORT, FRONTEND_URL, BACKEND_URL
- BACKEND_PORT
- JWT_SECRET, SESSION_SECRET
- POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, DATABASE_URL
- REDIS_PORT, REDIS_URL
- GCP_PROJECT_ID, GCP_REGION, GOOGLE_APPLICATION_CREDENTIALS
- VERTEX_AI_MODEL (e.g. `gemini-2.0-flash`), VERTEX_AI_TEMPERATURE, VERTEX_AI_MAX_TOKENS
- SMTP_* for email, TWILIO_* for SMS (optional)
- CONSULTANT_EMAIL / CONSULTANT_PHONE for escalation defaults

For the full reference, see `.env.example` in the repository root.

## AI integration notes
- Vertex AI is the primary model provider. To enable it you must:
  - Place the GCP service account key at `./secrets/gcp-credentials.json` and set `GOOGLE_APPLICATION_CREDENTIALS` to that path in `.env`.
  - Set `GCP_PROJECT_ID` and `GCP_REGION` and the `VERTEX_AI_MODEL` you want to call.
- If Vertex AI is unavailable the app uses a documented fallback path for Ollama/local LLMs — see `docs/AI_FALLBACK_EXAMPLES.md` and `docs/VERTEX_AI_FIXES.md` for details.

## API endpoints (high level)
- `POST /messages/chat` — send a text message and receive an AI reply.
- `POST /messages/voice-chat` — send a message and request audio (returns base64-encoded audio when `return_audio` is true).
- `GET /health` — health checks for DB and AI connectivity.
- Analytics and dashboard routes live under `backend/app/routes/analytics.py` and are used by the frontend Dashboard.

Example request/response shapes for `/messages/chat` and `/messages/voice-chat` are available in `docs/AI_SETUP_GUIDE.md`.

## Running tests
- Backend unit/integration tests (pytest):

```powershell
# from repo root
pytest -q
```

- Frontend E2E tests (Playwright) — see `frontend/playwright.config.js` and reports under `frontend/playwright-report/`.

## Troubleshooting
- Vertex AI not working: ensure `google-cloud-aiplatform` is installed, the credentials file exists, and the service account has proper roles (see `docs/AI_SETUP_GUIDE.md`).
- Fallback responses: if you see placeholder or generic replies, confirm the app connected to Vertex AI or a configured fallback LLM.
- Flaky voice tests: Playwright voice tests have timing sensitivity; rerun and consult `reports/` for artifacts.

## Security & secrets
- Do not commit `.env` or any real credentials. The repo includes `secrets/` in git for example paths; replace with your own secure files locally and add to `.gitignore` as needed.

## Contributing
- See `docs/TESTING.md` for testing guidance and `docs/AI_SETUP_GUIDE.md` for AI-related changes.

If you plan to work on the backend, run the test suite after changes. If you modify the frontend, run Playwright tests and update the `frontend/playwright-report` artifacts.

## Useful commands

```powershell
# Build and run all services
docker compose up --build

# Run backend tests
pytest -q

# Start frontend dev server
cd frontend; npm install; npm start
```

## Where to look next
- Backend routes and business logic: `backend/app/`.
- Frontend dashboard and components: `frontend/src/components/` (primary: `Dashboard.js`).
- AI setup and troubleshooting: `docs/AI_SETUP_GUIDE.md`, `scripts/setup-vertex-ai.sh`.
- Deployment and infra: `docker-compose*.yml`, `infra/`, `nginx/`.# TherapyBot
