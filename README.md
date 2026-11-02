# EOR Compliance Copilot

An internal AI assistant prototype for Employer of Record (EOR)
compliance questions. It is designed to help Operations, Legal, and
Customer Success teams find relevant policy evidence and produce
traceable answers with confidence, follow-up questions, and escalation
recommendations.

> **Prototype status:** The current foundation includes a FastAPI
> application and an Ollama integration using `qwen3:1.7b`. Document
> ingestion, retrieval-augmented generation (RAG), verification,
> persistence, and the frontend are planned implementation phases---not
> completed features yet.

## Problem

EOR operations span multiple countries, each with different onboarding,
employment lifecycle, payroll, and benefits requirements. The copilot
aims to make internal policy information easier to find while avoiding
unsupported legal conclusions.

## Core capabilities

The target application is designed to:

-   Answer questions using approved, country-specific policy documents.
-   Return evidence citations identifying the document, section,
    version, and effective date.
-   Explain confidence based on evidence quality and coverage.
-   Ask for missing facts when they materially affect an answer.
-   Escalate high-risk or ambiguous cases to a qualified human reviewer.
-   Record an auditable evidence trail while minimizing unnecessary
    personal data.

## Current implementation

-   FastAPI application.
-   Health-check endpoints.
-   Ollama connectivity check.
-   Chat endpoint calling the local `qwen3:1.7b` model.

The current chat endpoint is a connectivity milestone only. It is **not
yet a compliance-grade RAG answer flow** and should not be used to make
real employment or legal decisions.

## Target technology stack

  -----------------------------------------------------------------------
  Area                    Technology              Responsibility
  ----------------------- ----------------------- -----------------------
  API                     FastAPI                 HTTP endpoints and
                                                  orchestration entry
                                                  point

  Runtime validation      Pydantic                Request and response
                                                  contracts

  Local LLM               Ollama + Qwen3 1.7B     Constrained language
                                                  generation

  PDF extraction          pypdf                   Extract text from
                                                  policy PDFs

  Embeddings              Sentence Transformers   Convert chunks and
                                                  queries into vectors

  Vector store            ChromaDB                Similarity retrieval
                                                  with metadata filters

  Relational persistence  PostgreSQL + SQLAlchemy Document registry,
                                                  versions, audit records

  Frontend                React + TypeScript +    Chat and
                          Vite                    evidence-review
                                                  interface

  Tests                   Pytest                  Unit and integration
                                                  tests

  Local environment       Docker Compose          Run supporting services
                                                  consistently
  -----------------------------------------------------------------------

Dependencies should be introduced when their implementation phase begins
rather than installing the entire stack at once.

## Architecture overview

``` mermaid
flowchart TD
    U[Internal user] --> FE[React frontend]
    FE --> API[FastAPI API]
    API --> ORCH[Workflow orchestrator]

    ORCH --> QA[Query analysis and risk classification]
    QA --> RET[Retrieval service]
    RET --> CH[(ChromaDB)]
    RET --> PG[(PostgreSQL document metadata)]
    RET --> EVID[Ranked evidence and provenance]

    EVID --> GEN[Compliance answer generation]
    GEN --> LLM[Ollama / Qwen3 1.7B]
    GEN --> VERIFY[Deterministic citation and policy checks]
    VERIFY --> SAFE[Safety and escalation rules]
    SAFE --> RESP[Structured response]
    RESP --> FE

    ING[Document ingestion] --> EX[PDF text extraction]
    EX --> CHUNK[Chunking and metadata enrichment]
    CHUNK --> EMB[Embedding model]
    EMB --> CH
    CHUNK --> PG

    ORCH --> AUD[(Audit events)]
    SAFE --> AUD
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for component responsibilities,
query flow, data model, safety controls, and implementation boundaries.

## Repository layout

The following is the intended project layout. Some directories are
scaffolding for upcoming phases.

``` text
eor-compliance-copilot/
├── backend/
│   ├── app/
│   │   ├── api/           # HTTP routes
│   │   ├── agents/        # Workflow roles and orchestration
│   │   ├── core/          # Settings and shared configuration
│   │   ├── database/      # SQLAlchemy models and database access
│   │   ├── rag/           # Ingestion, chunking, embeddings, retrieval
│   │   ├── safety/        # Risk rules, escalation, citation validation
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   └── services/      # Ollama and application services
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/              # React application (planned)
├── knowledge_base/
│   ├── onboarding/
│   ├── employment/
│   ├── payroll/
│   └── benefits/
├── infrastructure/        # Docker and deployment configuration
├── ARCHITECTURE.md
└── README.md
```

## Getting started

### Prerequisites

-   Python 3.12+
-   Ollama installed and running
-   The `qwen3:1.7b` model pulled locally
-   Git

### 1. Start Ollama

``` bash
ollama serve
```

In another terminal, verify the model is available:

``` bash
ollama list
```

If it is not installed:

``` bash
ollama pull qwen3:1.7b
```

### 2. Set up the backend

From the repository root:

``` bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` is not yet populated with the current foundation
dependencies, install them with:

``` bash
pip install fastapi "uvicorn[standard]" pydantic-settings httpx python-multipart pytest
```

### 3. Configure environment variables

Create a local `.env` file from the example:

``` bash
cp .env.example .env
```

Expected initial settings:

``` dotenv
APP_NAME=EOR Compliance Copilot
APP_VERSION=0.1.0
API_V1_PREFIX=/api/v1
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:1.7b
```

Do not commit `.env` or secrets to Git.

### 4. Run the API

From the `backend/` directory:

``` bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Check the API

-   API root: http://localhost:8000/
-   Health: http://localhost:8000/health
-   LLM health: http://localhost:8000/health/llm
-   Swagger UI: http://localhost:8000/docs

Example chat request:

``` bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain what an Employer of Record is."}'
```

The chat endpoint currently checks basic local model connectivity and
response generation. It does not yet retrieve policy evidence.

## Planned answer contract

The compliance workflow should eventually return a structured object
similar to:

``` json
{
  "answer": "A concise answer supported by retrieved policy evidence.",
  "citations": [
    {
      "document_id": "POL-FR-001",
      "section": "Notice period",
      "version": "1.0",
      "effective_date": "2026-01-01",
      "chunk_id": "POL-FR-001-chunk-004"
    }
  ],
  "confidence": {
    "level": "medium",
    "reason": "Relevant evidence was retrieved, but a required employment detail is missing."
  },
  "escalation": {
    "required": true,
    "reason": "Human review is needed before action."
  },
  "follow_up_questions": [
    "What is the employee's contract type?"
  ]
}
```

This is an illustrative target contract, not a claim that these fields
are already implemented.

## Knowledge-base principles

Each ingested document and chunk should retain provenance metadata,
including:

-   Stable document ID and source filename.
-   Country and topic/category.
-   Section heading and page number when available.
-   Document version and effective date.
-   Publication/approval status and ingestion timestamp.
-   Source authority and supersession status.

Retrieval should apply country and status filters in addition to
semantic similarity. Conflicting or expired sources must be surfaced for
review rather than silently blended. A citation must point to evidence
actually retrieved for the answer.

Only approved, appropriately licensed documents should be used as
operational policy sources. Synthetic examples used for development must
be clearly labeled as fictional test data.

## Safety and limitations

-   The model is not a lawyer and must not be treated as a legal
    authority.
-   No answer should state a legal or company-policy rule as fact
    without supporting evidence.
-   High-risk topics such as termination, discrimination, protected
    leave, and conflicting legal sources should trigger human review
    according to configured policy.
-   Missing material facts should produce follow-up questions or
    escalation.
-   Citation existence and chunk provenance should be validated in code,
    not entrusted solely to the LLM.
-   Confidence should reflect evidence coverage, freshness, authority,
    and consistency---not the model's self-reported certainty.
-   Minimize personal data in prompts, logs, and stored records. Define
    retention and access controls before production use.

This project is a prototype and does not provide legal advice.

## Development roadmap

1.  **Foundation:** FastAPI, settings, Ollama client, health checks, and
    basic chat (current milestone).
2.  **Document ingestion:** PDF extraction, document registry, metadata,
    and chunking.
3.  **Embeddings and retrieval:** embedding model, ChromaDB persistence,
    country/category filters, and retrieval tests.
4.  **Grounded answer generation:** build prompts from retrieved
    evidence and return citations.
5.  **Safety and verification:** risk classification,
    missing-information checks, citation validation, escalation, and
    audit events.
6.  **Evaluation:** easy, tricky, conflicting-source, stale-source, and
    adversarial test cases.
7.  **Frontend:** chat, citations/evidence panel, confidence, and
    escalation status.
8.  **Packaging:** Docker Compose, operational documentation,
    monitoring, and demo workflow.

## Evaluation direction

The prototype should include at least ten test questions covering:

-   Straightforward onboarding requirements.
-   Country-specific bank-account or documentation questions.
-   Probation and notice-period questions.
-   Payroll cutoff and benefits questions.
-   Missing tenure or contract type.
-   Conflicting policy versions.
-   Expired documents.
-   High-risk termination or discrimination scenarios.
-   Prompt injection or requests to ignore policy evidence.

Evaluate groundedness, citation correctness, retrieval recall,
appropriate clarification, escalation precision, refusal behavior,
latency, and regressions.

## Contributing

-   Keep API schemas separate from business logic.
-   Keep retrieval separate from answer generation.
-   Prefer deterministic safety checks for rules that can be checked in
    code.
-   Add tests when introducing a new behavior.
-   Never add real employee personal data or secrets to fixtures, logs,
    or Git.
-   Update this README and `ARCHITECTURE.md` when the implemented
    architecture changes.
