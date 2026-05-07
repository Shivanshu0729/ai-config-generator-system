# AI Config Generator System

AI Config Generator System converts a natural language prompt into a validated application configuration through a compiler-style pipeline.

The current app runs as a single FastAPI server that serves both the API and the frontend from `http://127.0.0.1:8000`.

## What it does

- Parses a prompt into structured intent
- Designs the application architecture
- Generates UI, API, database, and auth schemas
- Validates the output and applies targeted repair when needed
- Tracks a per-client daily rate limit
- Serves a browser UI for testing and viewing results

## Current runtime model

- Frontend: served from `frontend/` by FastAPI at `/`
- API base: `/api/v1`
- Generate endpoint: `POST /api/v1/generate`
- Rate-limit status endpoint: `GET /api/v1/rate-limit`
- Health endpoint: `GET /api/health`
- Default limit: 5 requests per day per client

## Pipeline

1. Intent extraction
2. System design
3. Schema generation
4. Validation
5. Repair
6. Final config output

## Repository layout

- `app/main.py` - FastAPI app, CORS, static frontend mount
- `app/routes/generate.py` - generate and rate-limit routes
- `app/utils/rate_limit.py` - SQLite-backed rate-limit storage
- `app/pipeline/` - intent, design, schema, validator, repair, orchestrator
- `app/services/llm_service.py` - Groq client wrapper
- `frontend/` - HTML, CSS, and JavaScript UI
- `tests/` - evaluation scripts and tests

## Features

- Local-first development experience
- Live rate-limit display in the UI
- Rate-limit enforcement before generation
- Structured outputs with repair-aware flow
- Browser-based prompt testing

## Environment variables

- `GROQ_API_KEY` - required for LLM generation
- `GROQ_MODEL` - optional model override
- `APP_GENERATION_LIMIT` - default `5`
- `APP_GENERATION_LIMIT_WINDOW_SECONDS` - default `86400`
- `APP_RATE_LIMIT_DB_PATH` - optional SQLite path override

## Example request

```json
{
	"prompt": "Build a CRM with login, contacts list, lead pipeline, dashboard with analytics, role-based access, and Stripe payments."
}
```

## Example response shape

```json
{
	"success": true,
	"config": { "...": "..." },
	"metrics": {
		"latency_seconds": 12.4,
		"api_retries": 1,
		"quality_score": 92,
		"rate_limit": {
			"total_limit": 5,
			"used": 1,
			"remaining": 4
		}
	}
}
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

## Notes

- The frontend and backend use the same local origin during development.
- The rate limit is checked on every generation request.
- On the 6th request inside the daily window, the API returns a rate-limit error.
