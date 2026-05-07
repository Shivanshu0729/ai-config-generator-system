# Quick Start

## 1. Set up the environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Set your API key

```bash
set GROQ_API_KEY=your_key_here
```

PowerShell:

```powershell
$env:GROQ_API_KEY="your_key_here"
```

## 3. Start the server

```bash
python -m uvicorn app.main:app --reload
```

## 4. Open the website

Go to:

```text
http://127.0.0.1:8000
```

## 5. Try the app

1. Type a prompt.
2. Click Compile.
3. Watch the live rate-limit badge.
4. After 5 calls, the 6th request will show rate limit exceeded.

## API endpoints you can test

- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/api/v1/rate-limit`
- `http://127.0.0.1:8000/docs`

## Example prompt

```text
Build a CRM with login, contacts list, lead pipeline, dashboard with analytics, role-based access, and Stripe payments.
```

## If something does not work

- Make sure the server is running.
- Make sure you are opening `http://127.0.0.1:8000`.
- Make sure `GROQ_API_KEY` is set.
- If the badge says unavailable, refresh after the backend starts.

