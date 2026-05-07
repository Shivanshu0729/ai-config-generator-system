# Deployment Guide

## Local development

### Requirements

- Python 3.9+
- Virtual environment
- `GROQ_API_KEY`

### Install and run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

## Environment variables

- `GROQ_API_KEY` - required for generation
- `GROQ_MODEL` - optional model override
- `APP_GENERATION_LIMIT` - defaults to `5`
- `APP_GENERATION_LIMIT_WINDOW_SECONDS` - defaults to `86400`
- `APP_RATE_LIMIT_DB_PATH` - optional override for the SQLite file

## API endpoints

- `GET /api/health` - app health check
- `GET /api/v1/rate-limit` - current daily quota status
- `POST /api/v1/generate` - generate config from prompt

## Frontend behavior

- The frontend is served by the backend from `/`.
- The JavaScript client calls `http://127.0.0.1:8000/api/v1` in local development.
- The UI shows the live rate-limit counter beside the prompt box.

## Deployment notes

### Render or similar PaaS

- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Ensure `GROQ_API_KEY` is set in the service environment.
- Make sure the instance can write to the SQLite rate-limit file path.

### Docker

Recommended container start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Important operational detail

The daily limit is enforced server-side. If the app is restarted, the rate-limit database file remains the source of truth unless you intentionally change `APP_RATE_LIMIT_DB_PATH`.

## Troubleshooting

- If the UI shows `API limit: unavailable`, confirm the backend is running at `127.0.0.1:8000`.
- If generation fails, check `GROQ_API_KEY` and the selected Groq model.
- If the 6th request is not blocked, make sure the request is reaching the local backend and not a stale remote URL.
```

**Run**:
```bash
GROQ_API_KEY="gsk_..." docker-compose up
```

---

## Production Deployment

### On Heroku

```bash
# Login
heroku login

# Create app
heroku create web-maker-bot

# Set environment
heroku config:set GROQ_API_KEY="gsk_..." --app web-maker-bot

# Deploy
git push heroku main
```

### On AWS Lambda

Use AWS SAM or Serverless Framework:

```yaml
# serverless.yml
service: web-maker-bot

provider:
  name: aws
  runtime: python3.11
  timeout: 60
  memorySize: 2048
  environment:
    GROQ_API_KEY: ${env:GROQ_API_KEY}

functions:
  api:
    handler: app.main.app
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

### On Google Cloud Run

```bash
# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/web-maker-bot

# Deploy
gcloud run deploy web-maker-bot \
  --image gcr.io/PROJECT_ID/web-maker-bot \
  --platform managed \
  --set-env-vars GROQ_API_KEY="gsk_..." \
  --memory 2Gi \
  --timeout 60
```

---

## Monitoring & Logging

### Application Logs

Logs are printed to stdout with timestamps:
```
[INFO] 2024-01-15 10:30:45 - app.pipeline.orchestrator - === STARTING GENERATION PIPELINE ===
[INFO] 2024-01-15 10:30:45 - app.pipeline.intent - Intent extracted: CRM System
```

### Metrics Collection

Results are stored in memory during runtime. For persistent metrics:

```python
# Save metrics periodically
import json
from datetime import datetime

def save_metrics(result):
    timestamp = datetime.now().isoformat()
    with open("metrics.jsonl", "a") as f:
        f.write(json.dumps({
            "timestamp": timestamp,
            "success": result["success"],
            "time": result["metrics"]["total_time"],
            "repairs": result["metrics"]["repair_attempts"]
        }) + "\n")
```

---

## Troubleshooting

### 1. "GROQ_API_KEY not set"
```bash
export GROQ_API_KEY="gsk_..."
```

### 2. "JSON decode failed"
This means the LLM didn't return valid JSON. The system will retry automatically up to 3 times. If still failing:
- Check that your API key is valid
- Verify your Groq model has access
- Try with a simpler prompt first

### 3. "Validation failed after 3 attempts"
The repair engine couldn't fix the generated config. This suggests:
- The prompt was too vague or contradictory
- Try being more specific about requirements
- Break complex requirements into simpler ones

### 4. Slow generation (> 60s)
- Could be API rate limits
- Could be complex prompt requiring multiple retries
- Check network connectivity
- Consider using a faster Groq model

---

## Performance Optimization

### 1. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def generate_app(prompt: str):
    # Cache prevents re-generation of identical prompts
    return orchestrator.run(prompt)
```

### 2. Batch Processing
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(orchestrator.run, prompt) for prompt in prompts]
    results = [f.result() for f in futures]
```

### 3. Model Selection
- `llama-3.1-70b-versatile` (good balance of speed and quality)
- `llama-3.1-8b-instant` (faster, lower cost)
- Use faster model for validation stage only

---

## Support & Feedback

Issues? Questions?
- Check the README.md for architecture overview
- Run evaluation to verify setup
- Test with simple prompts first
- Increase logging verbosity for debugging

