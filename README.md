<<<<<<< HEAD
AI Config Generator System

A production-grade system that converts natural language into complete, validated, and executable application configurations using a multi-stage compiler-like pipeline.

This project is designed as an engineering system rather than a prompt-based script, focusing on reliability, control, and execution readiness.
=======
# AI Config Generator System

A production-oriented toolchain that converts natural-language requirements into validated, executable application configurations using a multi-stage, compiler-like pipeline.

This repository contains the API backend, the pipeline implementation, an evaluation harness, and a small frontend for local testing.

**Repository**: https://github.com/Shivanshu0729/ai-config-generator-system
>>>>>>> 91c0769 (docs: polished README with usage, architecture, and quickstart)

Overview

<<<<<<< HEAD
The system transforms open-ended user instructions into structured application configurations including:

UI schema (pages, components, layouts)
API schema (endpoints, methods, validation)
Database schema (tables, relationships)
Authentication and authorization rules
Business logic constraints

The output is strictly validated and designed to be directly usable in downstream runtime systems.
=======
## Highlights

- Multi-stage pipeline: intent → design → schema → validation → repair → output
- Deterministic, schema-driven outputs (Pydantic models enforce correctness)
- Intelligent repair loop (selective fixes rather than blind regeneration)
- Metrics & evaluation framework for measuring success, latency and repairs
- Simple frontend for rapid testing and previewing generated configs
>>>>>>> 91c0769 (docs: polished README with usage, architecture, and quickstart)

System Architecture

<<<<<<< HEAD
The system follows a multi-stage pipeline:

Intent Extraction
Parses natural language into structured intent.
System Design
Converts intent into application architecture, including entities, roles, and flows.
Schema Generation
Generates database, API, UI, and authentication configurations.
Validation Layer
Ensures structural correctness, type safety, and cross-layer consistency.
Repair Engine
Fixes inconsistencies without full regeneration using targeted corrections.
Execution Awareness
Ensures output is usable and logically complete for runtime systems.
Key Design Principles
Multi-Stage Pipeline

Each stage is modular and independent, improving control and reducing hallucination.

Strict Schema Enforcement

All outputs conform to predefined Pydantic models ensuring:

Valid JSON
Required fields
Type safety
Cross-layer consistency
Intelligent Repair System

Instead of retrying entire generations:

Missing fields are added
Invalid references are corrected
Logical gaps are resolved incrementally
Deterministic Behavior

Structured prompting and controlled temperature ensure consistent outputs for the same input.

Execution Awareness

Generated configurations are:

Structurally valid
Logically complete
Ready for execution
Core Components
Pipeline Modules
Intent Extractor (app/pipeline/intent.py)
Converts natural language into structured intent.
System Designer (app/pipeline/design.py)
Builds application architecture.
# AI Config Generator System

A production-oriented toolchain that converts natural-language requirements into validated, executable application configurations using a multi-stage, compiler-like pipeline.

This repository contains the API backend, the pipeline implementation, an evaluation harness, and a small frontend for local testing.

**Repository**: https://github.com/Shivanshu0729/ai-config-generator-system

---

## Highlights

- Multi-stage pipeline: intent → design → schema → validation → repair → output
- Deterministic, schema-driven outputs (Pydantic models enforce correctness)
- Intelligent repair loop (selective fixes rather than blind regeneration)
- Metrics & evaluation framework for measuring success, latency and repairs
- Simple frontend for rapid testing and previewing generated configs

---

## Quickstart

Prerequisites:
- Python 3.10+ (recommended)
- Git

1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your LLM key (set `GROQ_API_KEY` or the provider key used by your LLM wrapper):

```bash
# PowerShell example
$env:GROQ_API_KEY = "gsk_..."
```

4. Start the API server (default port used in development is 8001):

```bash
uvicorn app.main:app --reload --port 8001
```

5. Open the frontend for quick manual tests:

```bash
# from the project root
pushd frontend
python -m http.server 5500
# then open http://localhost:5500/index.html
popd
```

The API docs are available at `http://127.0.0.1:8001/docs` after the server starts.

---

## Architecture Overview

The pipeline is intentionally modular to improve reliability and observability:

- `app/pipeline/intent.py` — Convert prompt → structured intent
- `app/pipeline/design.py` — Map intent → architectural design
- `app/pipeline/schema.py` — Produce DB / UI / API schemas
- `app/pipeline/validator.py` — Mechanical validation of results
- `app/pipeline/repair.py` — Targeted fixes for common failures
- `app/pipeline/orchestrator.py` — Orchestrates stages, metrics, and repair loop

The FastAPI backend (`app/main.py` and `app/routes/generate.py`) exposes `POST /api/v1/generate` and returns a JSON payload containing `success`, `config`, and `metrics`.

Sample output and schema expectations are provided in `SAMPLE_OUTPUT.json`.

---

## Usage Examples

Simple curl example to generate a config (replace prompt as needed):

```bash
curl -X POST http://127.0.0.1:8001/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a CRM with login, contacts, dashboard, and role-based access"}'
```

Python example using the orchestrator directly:

```python
from app.pipeline.orchestrator import Orchestrator

orch = Orchestrator()
result = orch.run("Simple todo app with authentication and notes")
if result["success"]:
    cfg = result["config"]
    print(cfg.get("app_name"))
```

---

## Testing & Evaluation

- Run unit tests and evaluation scripts with:

```bash
pytest -q
python -m tests.run_evaluation
```

- The evaluation harness records metrics such as `success`, `repair_attempts`, and `total_time` for each case.

---

## Development Notes

- The system favors structured prompting and lower temperature settings for schema stages to reduce hallucination.
- Validation is mechanical and runs before any repair attempts.
- Repair attempts are limited (default max 3) to avoid runaway generation costs.

If you add new pipeline stages, ensure the Pydantic models in `app/models` are updated and test coverage is extended.

---

## Project Structure

See the primary folders:

- `app/` — FastAPI server, pipeline, services, and models
- `frontend/` — Static UI for quick testing and previews
- `tests/` — Evaluation and test harness
- `SAMPLE_OUTPUT.json` — Example generated config

---

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository
2. Create a feature branch
3. Add tests for new behavior
4. Open a pull request with a clear description

---

## License

This project is provided under the MIT License. See `LICENSE` for details (add a `LICENSE` file if you publish this publicly).

---

If you'd like, I can also add a GitHub Actions CI workflow that runs linting and tests on PRs.
  -d '{"prompt": "Build a CRM with login, contacts, dashboard, and role-based access"}'
```

Python example using the orchestrator directly:

```python
from app.pipeline.orchestrator import Orchestrator

orch = Orchestrator()
result = orch.run("Simple todo app with authentication and notes")
if result["success"]:
    cfg = result["config"]
    print(cfg.get("app_name"))
```

---

## Testing & Evaluation

- Run unit tests and evaluation scripts with:

```bash
pytest -q
python -m tests.run_evaluation
```

- The evaluation harness records metrics such as `success`, `repair_attempts`, and `total_time` for each case.

---

## Development Notes

- The system favors structured prompting and lower temperature settings for schema stages to reduce hallucination.
- Validation is mechanical and runs before any repair attempts.
- Repair attempts are limited (default max 3) to avoid runaway generation costs.

If you add new pipeline stages, ensure the Pydantic models in `app/models` are updated and test coverage is extended.

---

## Project Structure

See the primary folders:

- `app/` — FastAPI server, pipeline, services, and models
- `frontend/` — Static UI for quick testing and previews
- `tests/` — Evaluation and test harness
- `SAMPLE_OUTPUT.json` — Example generated config

---

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository
2. Create a feature branch
3. Add tests for new behavior
4. Open a pull request with a clear description

---

## License

This project is provided under the MIT License. See `LICENSE` for details (add a `LICENSE` file if you publish this publicly).

---

If you'd like, I can also add a GitHub Actions CI workflow that runs linting and tests on PRs.
>>>>>>> 91c0769 (docs: polished README with usage, architecture, and quickstart)
