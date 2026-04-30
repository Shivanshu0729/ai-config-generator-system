# Web Maker Bot - Setup & Deployment Guide

## Local Development Setup

### 1. Prerequisites
- Python 3.9+
- Virtual environment
- Groq API key

### 2. Installation

```bash
# Clone or navigate to project
cd web_maker_bot

# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your Groq API key
GROQ_API_KEY="gsk_..."
```

### 4. Run Server

```bash
# Start FastAPI server
python app/main.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`
Docs at: `http://localhost:8000/docs`

---

## API Usage

### Generate Application Config

**Endpoint**: `POST /api/v1/generate`

**Request**:
```json
{
  "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
}
```

**Response** (Success):
```json
{
  "success": true,
  "config": {
    "app_name": "CRM System",
    "app_description": "...",
    "entities": { ... },
    "db_schema": { ... },
    "ui_schema": { ... },
    "api_schema": { ... },
    "auth_config": { ... },
    "assumptions": [ ... ],
    "notes": "..."
  },
  "metrics": {
    "repair_attempts": 0,
    "total_time": 18.5,
    "success": true
  }
}
```

**Response** (Failure):
```json
{
  "success": false,
  "error": "Validation failed after 3 attempts",
  "metrics": {
    "repair_attempts": 3,
    "total_time": 55.2,
    "success": false
  }
}
```

---

## Running Evaluation

### Run Full Test Suite

```bash
# Run all 20 tests
python -m tests.run_evaluation

# Output saved to: evaluation_results.json
```

### Run Custom Test

```python
from tests.evaluation import EvaluationRunner, TestCase

runner = EvaluationRunner()

# Add custom test
custom_test = TestCase(
    id="custom-001",
    category="production",
    prompt="Your custom prompt here",
    description="Test description"
)

runner.results = []
result = runner._run_test(custom_test)
print(f"Success: {result.success}, Time: {result.total_time}s")
```

---

## Frontend Integration

### React Example

```tsx
import { useState } from 'react';

export function AppGenerator() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState(null);

  const generateApp = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your app..."
      />
      <button onClick={generateApp} disabled={loading}>
        {loading ? 'Generating...' : 'Generate'}
      </button>
      
      {config && (
        <pre>{JSON.stringify(config, null, 2)}</pre>
      )}
    </div>
  );
}
```

### Next.js API Route

```typescript
// pages/api/generate.ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') return res.status(405).end();

  try {
    const response = await fetch('http://localhost:8000/api/v1/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: req.body.prompt })
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    res.status(500).json({ error: String(error) });
  }
}
```

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV GROQ_API_KEY=${GROQ_API_KEY}

EXPOSE 8000

CMD ["python", "app/main.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  web-maker-bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./logs:/app/logs

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web-maker-bot
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

