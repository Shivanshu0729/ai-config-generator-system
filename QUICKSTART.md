# Quick Start Guide

## 60-Second Setup

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
export GROQ_API_KEY="gsk_..."

# 3. Run
python -m app.main

# 4. Visit http://localhost:8000/docs
```

## 5-Minute First Request

### Via Browser (Swagger UI)

1. Go to `http://localhost:8000/docs`
2. Click "Try it out" on `/api/v1/generate`
3. Paste in the JSON request body:

```json
{
  "prompt": "Build a CRM with login, contacts, dashboard, and role-based access"
}
```

4. Click "Execute"
5. See generated config in response!

### Via cURL

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Build a simple todo app with user accounts and task lists"
  }'
```

### Via Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={"prompt": "Build a CRM with contacts and dashboard"}
)

config = response.json()
print(f"Success: {config['success']}")
if config['success']:
    print(f"App: {config['config']['app_name']}")
    print(f"Entities: {list(config['config']['entities'].keys())}")
```

---

## Understanding the Output

Generated config has this structure:

```json
{
  "success": true,
  "config": {
    "app_name": "CRM System",
    "app_description": "Customer relationship management platform...",
    
    "entities": {
      "User": {"fields": {...}},
      "Contact": {"fields": {...}},
      "Task": {"fields": {...}}
    },
    
    "db_schema": {
      "entities": {...},
      "relations": [...]
    },
    
    "ui_schema": {
      "pages": {
        "dashboard": {...},
        "contacts": {...}
      }
    },
    
    "api_schema": {
      "endpoints": [
        {
          "path": "/api/v1/contacts",
          "method": "GET",
          "name": "list_contacts",
          "auth_required": true,
          "allowed_roles": ["user", "admin"]
        },
        ...
      ],
      "base_path": "/api/v1"
    },
    
    "auth_config": {
      "auth_type": "jwt",
      "roles": {
        "user": ["read", "write"],
        "admin": ["read", "write", "delete", "manage_users"]
      },
      "premium_features": ["advanced_analytics"]
    },
    
    "assumptions": [
      "Used JWT for authentication",
      "Assumed role-based access control",
      "Premium users get analytics access"
    ],
    
    "notes": "Generated with 0 repair iterations"
  },
  
  "metrics": {
    "repair_attempts": 0,
    "total_time": 18.5,
    "success": true
  }
}
```

---

## Common Prompts to Try

### Simple
```
"Build a todo app with lists and tasks"
```

### Medium
```
"Create a blog with posts, comments, and user accounts"
```

### Complex
```
"Build an e-commerce platform with products, shopping cart, checkout, orders, and admin dashboard"
```

### With Specific Requirements
```
"Create a CRM for managing sales: 
- Leads table
- Contacts table  
- Only sales managers can see all contacts
- Sales reps can only see their own contacts
- Admin can see everything"
```

---

## What's Happening Behind the Scenes

The system processes your request through these stages:

1. **Intent Extraction** - Parse your requirements into structured data
2. **Design** - Create application architecture from intent  
3. **Schema Generation** - Generate DB schema, UI pages, and API endpoints
4. **Validation** - Check that all schemas are valid and consistent
5. **Repair** - Fix any errors without full regeneration (if needed)
6. **Output** - Return complete, ready-to-use configuration

---

## Troubleshooting

### "Connection refused"
```
Server isn't running. Try:
python app/main.py
```

### "GROQ_API_KEY not set"
```bash
export GROQ_API_KEY="gsk_..."
# or on Windows:
set GROQ_API_KEY=gsk_...
```

### "JSON decode failed"
Wait for retry (up to 3 times). If it fails:
- Check your API key is valid
- Try a simpler prompt
- Check your Groq model access

### "Validation failed"
The system tried to repair but couldn't fix all issues. This means:
- Prompt is too vague/contradictory
- Try being more specific
- Break complex requirements into simpler steps

---

## Next Steps

- **Learn the system**: Read `README.md` for architecture overview
- **Deep dive**: Read `ARCHITECTURE.md` for design decisions
- **Deploy**: See `DEPLOYMENT.md` for production setup
- **Evaluate**: Run `python -m tests.run_evaluation` to test on 20 cases
- **Integrate**: Add the API to your frontend

---

## Architecture at a Glance

Natural Language Prompt
-> Intent Extraction (parse what you want)
-> System Design (plan the architecture)
-> Schema Generation (generate DB/UI/API)
-> Validate & Repair (check & fix errors)
-> Complete, Validated Application Config (ready to use)

---

## Questions?

- Check `README.md` for comprehensive overview
- Check `ARCHITECTURE.md` for design thinking
- Run evaluation to see how it handles edge cases
- Try with your own prompts!

