# AI Config Generator System

A production-grade system that converts natural language into complete, validated, and executable application configurations using a multi-stage compiler-like pipeline.

This project is designed as an engineering system rather than a prompt-based script, focusing on reliability, control, and execution readiness.

## Demo
🔗 Live Demo: (https://ai-config-builder.netlify.app/)

---

## Highlights

- Multi-stage pipeline: intent → design → schema → validation → repair → output
- Deterministic, schema-driven outputs using Pydantic models
- Intelligent repair system (no blind retries)
- Evaluation framework with metrics tracking
- Execution-ready configuration generation
- Simple frontend for testing and visualization

---

## Overview

The system transforms open-ended user instructions into structured application configurations, including:

- UI schema (pages, components, layouts)
- API schema (endpoints, methods, validation)
- Database schema (tables, relationships)
- Authentication and authorization rules
- Business logic constraints

The generated output is validated and designed to be directly usable in downstream runtime systems.

---

## System Architecture

The system follows a modular multi-stage pipeline:

### 1. Intent Extraction
Parses natural language into structured intent.

### 2. System Design
Converts intent into application architecture (entities, roles, flows).

### 3. Schema Generation
Generates DB, API, UI, and authentication configurations.

### 4. Validation Layer
Ensures structural correctness, type safety, and cross-layer consistency.

### 5. Repair Engine
Fixes inconsistencies using targeted corrections.

### 6. Execution Awareness
Ensures output is complete and usable for runtime systems.

---

## Key Design Principles

### Multi-Stage Pipeline
Each stage is independent, improving control and reducing hallucination.

### Strict Schema Enforcement
All outputs follow predefined Pydantic models ensuring:

- Valid JSON
- Required fields
- Type safety
- Cross-layer consistency

### Intelligent Repair System
Instead of full regeneration:

- Missing fields are added
- Invalid references are corrected
- Logical gaps are resolved

### Deterministic Behavior
Structured prompting + controlled temperature ensures consistent outputs.

### Execution Awareness
Outputs are:

- Structurally valid
- Logically complete
- Ready for execution

---

## Architecture Overview

Core pipeline modules:

- `app/pipeline/intent.py` — Intent extraction  
- `app/pipeline/design.py` — System design  
- `app/pipeline/schema.py` — Schema generation  
- `app/pipeline/validator.py` — Validation  
- `app/pipeline/repair.py` — Repair engine  
- `app/pipeline/orchestrator.py` — Pipeline coordinator  

FastAPI backend:

- `POST /api/v1/generate`
- `GET /api/v1/health`

---

## Quickstart

### 1. Clone Repository

```bash
git clone https://github.com/Shivanshu0729/ai-config-generator-system.git
cd ai-config-generator-system
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
GROQ_API_KEY=your_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

### 5. Run Backend
```bash
uvicorn app.main:app --reload --port 8001
```
Access API docs:

http://127.0.0.1:8001/docs

### Frontend
cd frontend
python -m http.server 5500

Evaluation Framework

Includes:

10 production prompts
10 edge-case prompts
Metrics Tracked
Success rate
Repair attempts
Latency
Failure types
Reliability Features
Structured prompting
Validation before output
Repair loop (max 3 attempts)
Type-safe schema enforcement
Metrics tracking
Cost vs Performance Tradeoffs
Latency

Multi-stage pipeline increases latency but improves reliability.

Cost

Repair-based approach reduces unnecessary LLM calls.

Quality

Lower temperature improves consistency at the cost of variability.

Project Structure
app/
├── main.py
├── models/
├── services/
├── utils/
├── routes/
└── pipeline/

frontend/
tests/
requirements.txt
README.md
What Makes This System Strong
Modular pipeline architecture
Controlled LLM interaction
Validation and repair mechanisms
Execution-ready outputs
Evaluation framework
Conclusion

This system demonstrates system-level engineering by combining structured generation, validation, and execution awareness. It is designed to handle real-world ambiguity while maintaining reliability, consistency, and control over outputs.
