AI Config Generator System

A production-grade system that converts natural language into complete, validated, and executable application configurations using a multi-stage compiler-like pipeline.

This project is designed as an engineering system rather than a prompt-based script, focusing on reliability, control, and execution readiness.

Overview

The system transforms open-ended user instructions into structured application configurations including:

UI schema (pages, components, layouts)
API schema (endpoints, methods, validation)
Database schema (tables, relationships)
Authentication and authorization rules
Business logic constraints

The output is strictly validated and designed to be directly usable in downstream runtime systems.

System Architecture

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
Schema Generator (app/pipeline/schema.py)
Produces DB, UI, API schemas.
Validator (app/pipeline/validator.py)
Performs mechanical validation without LLM dependency.
Repair Engine (app/pipeline/repair.py)
Fixes errors selectively.
Orchestrator (app/pipeline/orchestrator.py)
Manages full pipeline execution and retry logic.
API Layer

Implemented using FastAPI:

POST /api/v1/generate
Generates application configuration from prompt.
GET /api/v1/health
Health check endpoint.
LLM Integration

Handled via a dedicated service:

Structured JSON output enforcement
Retry mechanism for invalid responses
Schema-guided prompting
Temperature control per stage
Evaluation Framework

The system includes an evaluation setup with:

10 production-level prompts
10 edge-case prompts (vague, conflicting, incomplete)
Metrics Tracked
Success rate
Repair attempts
Latency
Failure types
Expected Performance
High success rate on well-defined prompts
Robust handling of ambiguous inputs
Reduced retries due to repair system
Reliability Features
Structured prompting
Validation before output
Repair loop (max 3 attempts)
Type-safe schema enforcement
Metrics tracking for every request
Cost and Performance Tradeoffs
Latency

Multi-stage pipeline introduces latency but improves reliability.

Cost

Repair-based approach reduces unnecessary LLM calls compared to full regeneration.

Quality

Lower temperature improves consistency at the cost of creativity.

Setup Instructions
1. Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # Windows
2. Install Dependencies
pip install -r requirements.txt
3. Set Environment Variables
GROQ_API_KEY=your_api_key
GROQ_MODEL=llama-3.1-8b-instant
Run the Application
uvicorn app.main:app --reload --port 8001

Access API documentation:

http://127.0.0.1:8001/docs
Example Usage
API Request
curl -X POST http://127.0.0.1:8001/api/v1/generate \
-H "Content-Type: application/json" \
-d '{"prompt": "Build a CRM with login and contacts"}'
Project Structure
app/
├── main.py
├── models/
├── services/
├── utils/
├── routes/
└── pipeline/

tests/
frontend/
requirements.txt
README.md
What Makes This System Strong
Modular pipeline architecture
Controlled LLM interaction
Validation and repair mechanisms
Execution-ready outputs
Measurable evaluation framework
Conclusion

This project demonstrates system-level thinking by combining structured generation, validation, and execution awareness. It is designed to handle real-world ambiguity while maintaining reliability and consistency.
