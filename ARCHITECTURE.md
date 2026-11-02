# EOR Compliance Copilot --- Application Architecture

## 1. Purpose and scope

The EOR Compliance Copilot is an internal assistant concept for teams
supporting Employer of Record operations. It helps users locate
country-specific policy evidence and prepares concise, traceable
responses.

The design prioritizes evidence-grounded answers, explicit uncertainty,
safe escalation, and auditability. It is not an autonomous legal
decision-maker.

### Current implementation boundary

Implemented foundation: - FastAPI application and basic health routes. -
Ollama connectivity check. - Chat endpoint that sends a prompt to
`qwen3:1.7b`.

Target architecture (planned): - Document ingestion and metadata
registry. - Embedding generation and ChromaDB retrieval. - Query
analysis and controlled orchestration. - Evidence-grounded answer
generation. - Deterministic verification and escalation. - Audit
persistence and React frontend.

Do not represent planned components as implemented until their code and
tests exist.

## 2. High-level architecture

``` mermaid
flowchart TB
    subgraph Client
        USER[Internal user]
        WEB[React + TypeScript UI]
        USER --> WEB
    end

    subgraph Backend["FastAPI application"]
        API[API routes]
        ORCH[Workflow orchestrator]
        ANALYZER[Query analyzer]
        RISK[Risk classifier]
        RETRIEVER[Retrieval service]
        ANSWER[Compliance answer generator]
        VALIDATOR[Citation and evidence validator]
        ESCALATE[Escalation policy]
        AUDIT[Audit service]

        API --> ORCH
        ORCH --> ANALYZER
        ANALYZER --> RISK
        ORCH --> RETRIEVER
        RETRIEVER --> ANSWER
        ANSWER --> VALIDATOR
        VALIDATOR --> ESCALATE
        ESCALATE --> AUDIT
        AUDIT --> API
    end

    subgraph Knowledge["Knowledge and persistence"]
        FILES[Approved policy documents]
        INGEST[Ingestion pipeline]
        EXTRACT[Text extraction]
        CHUNK[Chunking and metadata]
        EMBED[Embedding model]
        VECTOR[(ChromaDB)]
        META[(PostgreSQL)]
        FILES --> INGEST --> EXTRACT --> CHUNK --> EMBED --> VECTOR
        CHUNK --> META
    end

    subgraph Model["Local model runtime"]
        OLLAMA[Ollama API]
        QWEN[Qwen3 1.7B]
        OLLAMA --> QWEN
    end

    WEB <--> API
    RETRIEVER <--> VECTOR
    RETRIEVER <--> META
    ANALYZER <--> OLLAMA
    ANSWER <--> OLLAMA
    RISK <--> OLLAMA
```

## 3. Components and responsibilities

  -----------------------------------------------------------------------
  Component               Responsibility          Design notes
  ----------------------- ----------------------- -----------------------
  React frontend          Collect questions and   Planned client; should
                          display answers,        not contain compliance
                          citations, confidence,  rules
                          and escalation          

  FastAPI routes          Validate requests and   Thin HTTP layer
                          expose API operations   

  Workflow orchestrator   Coordinate the steps    Controlled workflow,
                          and determine whether   not unconstrained
                          to clarify, answer, or  autonomous agents
                          escalate                

  Query analyzer          Extract country, topic, LLM extraction must be
                          relevant dates, and     schema-validated;
                          known facts             deterministic
                                                  validation follows

  Risk classifier         Identify high-risk      Use explicit rules for
                          categories and missing  known high-risk cases
                          critical facts          

  Document ingestion      Register and process    Preserve original
                          approved source         source and provenance
                          documents               

  Text extraction         Extract text and page   Flag scanned/image-only
                          references from PDFs    or extraction-poor PDFs

  Chunking                Split content into      Prefer section-aware
                          retrievable units       chunks; retain page and
                                                  heading metadata

  Embedding service       Embed chunks and user   Use a dedicated
                          queries                 embedding model; do not
                                                  use Qwen generation
                                                  embeddings by
                                                  assumption

  ChromaDB                Store vectors and chunk Filter by country,
                          metadata for semantic   category, status, and
                          retrieval               version

  PostgreSQL              Store document          Source of truth for
                          registry, version       structured metadata
                          relationships,          
                          ingestion status, and   
                          audit events            

  Retrieval service       Retrieve and rank       Return chunk text plus
                          evidence                provenance; enforce
                                                  metadata filters

  Compliance answer       Draft a response using  Explicitly state when
  generator               only supplied evidence  evidence is
                                                  insufficient

  Citation validator      Check that cited        Deterministic code
                          chunk/document IDs      validation
                          exist in retrieved      
                          evidence                

  Escalation policy       Require human review    Rules should be
                          for defined risks,      testable and
                          conflicts, or           configurable
                          insufficient evidence   

  Audit service           Record request          Avoid storing
                          metadata, evidence IDs, unnecessary personal
                          decisions, and outcome  data

  Ollama/Qwen             Local language          Small model; constrain
                          generation and          output and validate it
                          structured extraction   
  -----------------------------------------------------------------------

## 4. Request lifecycle

1.  **Receive request:** API validates the message and optional context.
2.  **Analyze query:** identify country, topic (onboarding, employment,
    payroll, benefits), dates, and relevant facts.
3.  **Check required facts:** if a material field is missing, ask a
    focused follow-up question rather than guessing.
4.  **Classify risk:** apply deterministic escalation rules for
    high-risk topics and known sensitive cases.
5.  **Retrieve evidence:** search approved documents using semantic
    similarity plus metadata filters.
6.  **Assess evidence:** inspect source authority, effective dates,
    version status, country match, and conflicts.
7.  **Generate draft:** ask Qwen to answer only from the retrieved
    evidence and to identify unsupported points.
8.  **Validate citations:** verify every cited ID and section against
    the retrieved evidence set.
9.  **Apply safety policy:** escalate if evidence is missing,
    conflicting, stale, low quality, or the case is high risk.
10. **Return response:** answer, citations, confidence rationale,
    escalation state, and follow-up questions.
11. **Audit:** record the relevant evidence IDs, source versions,
    workflow outcome, and timestamps.

The orchestrator should be able to stop before generation or
finalization when required facts or evidence are absent.

## 5. Knowledge representation

### Document-level metadata

Recommended fields:

  -----------------------------------------------------------------------
  Field                               Description
  ----------------------------------- -----------------------------------
  `document_id`                       Stable identifier for a source
                                      document

  `title`                             Human-readable title

  `country_code`                      ISO country code where applicable

  `category`                          Onboarding, employment, payroll,
                                      benefits, or other

  `source_type`                       Internal policy, official source,
                                      guidance, or test fixture

  `authority_level`                   Configured source-authority
                                      classification

  `version`                           Source document version

  `effective_from` / `effective_to`   Validity interval, when known

  `approval_status`                   Draft, approved, superseded,
                                      expired, or rejected

  `published_at`                      Source publication date, when known

  `ingested_at`                       System ingestion timestamp

  `checksum`                          File hash for duplicate/change
                                      detection

  `supersedes_document_id`            Prior version, when applicable
  -----------------------------------------------------------------------

### Chunk-level metadata

Each chunk should retain: - Stable `chunk_id`. - `document_id` and
document version. - Country and category. - Section heading and page
number/page range. - Chunk sequence number. - Effective dates and
approval status inherited from the document. - Original source
reference.

Chunk IDs should be stable for a specific document version and content.
Re-ingesting a changed source should not silently overwrite the
provenance of the previous version.

### Chunking strategy

-   Extract text while preserving page boundaries and headings where
    possible.
-   Split by sections/paragraphs before applying a token or character
    limit.
-   Use a modest overlap to avoid losing context at boundaries.
-   Avoid mixing countries or unrelated policy sections in one chunk.
-   Store source metadata with every chunk.
-   Detect empty or low-quality extraction and mark the document for
    manual review.

## 6. Retrieval and source conflict handling

Retrieval should combine: - Semantic similarity. - Country and topic
filters. - Approved/current status filters. - Effective-date
applicability. - Source authority and version information.

Do not assume that the highest similarity score means the source is
authoritative or current.

### Conflict policy

1.  Detect when retrieved sources disagree on a material point.
2.  Compare country scope, source authority, approval status, effective
    dates, and version relationships.
3.  Do not silently merge contradictory statements.
4.  If a conflict cannot be resolved using configured governance rules,
    return an uncertainty explanation and escalate to Legal/Policy
    owners.
5.  Preserve all relevant source IDs in the audit trail.

### Outdated documents

Superseded or expired documents should normally be excluded from
current-answer retrieval. They may be retrieved for historical questions
if explicitly requested and clearly labeled as historical. Missing
effective dates should lower confidence and may require review.

### Country-specific overrides

Country must be an explicit retrieval filter when the question is
country-specific. Global policies may be included only when their scope
is applicable. Country-specific rules should not be overwritten by
generic global content without an explicit precedence policy.

## 7. Prompting and model strategy

The local Qwen3 1.7B model is a constrained generation component, not a
legal authority.

### Query analysis prompt

Ask for structured extraction only: - Country. - Topic. - Relevant
dates. - Facts explicitly stated by the user. - Missing facts required
by configured policy. - Potential risk indicators.

Validate the output against a Pydantic schema. Never treat
model-extracted facts as verified if the user did not provide them.

### Answer generation prompt

Provide: - The user question. - Relevant retrieved evidence with chunk
IDs. - Source metadata and effective dates. - Explicit instruction to
use only supplied evidence. - Required response schema. - Instruction to
state insufficient evidence rather than fill gaps.

Do not include unrelated retrieved chunks just to increase context
length.

### Verification strategy

Use deterministic code for: - Citation ID membership in the retrieved
set. - Required response fields and types. - Source status and country
match. - High-risk escalation rules. - Missing required facts. -
Detection of empty retrieval results.

An LLM verifier may provide an additional critique, but it must not
override deterministic failures or approve unsupported claims.

## 8. Response contract

A successful response should contain:

``` json
{
  "answer": "Concise, actionable response grounded in retrieved evidence.",
  "citations": [
    {
      "document_id": "POL-COUNTRY-001",
      "chunk_id": "POL-COUNTRY-001-v1-004",
      "section": "Relevant section",
      "page": 3,
      "version": "1.0",
      "effective_from": "2026-01-01"
    }
  ],
  "confidence": {
    "level": "medium",
    "reason": "Relevant evidence exists, but one material fact remains unknown."
  },
  "escalation": {
    "required": true,
    "reason": "Human review is required before an operational decision."
  },
  "follow_up_questions": [
    "Please confirm the employee's contract type."
  ]
}
```

This is a target schema example. The exact fields and enums should be
implemented and versioned in the backend.

### Confidence policy

Confidence must be derived from evidence quality, not from the LLM's
self-assessment. Consider: - Retrieval relevance and coverage. - Source
authority and approval status. - Effective-date applicability. -
Agreement or conflict among sources. - Whether material user facts are
missing. - Citation validation results.

A high-risk case may require escalation even when evidence retrieval is
strong.

## 9. Safety, privacy, and governance

-   Do not present unsupported legal claims as facts.
-   Ask follow-up questions when missing facts materially change the
    answer.
-   Escalate termination, discrimination, protected-class, and other
    configured high-risk matters.
-   Escalate unresolved conflicts and stale/unknown source status.
-   Validate citations in code.
-   Treat uploaded documents as untrusted content; document text must
    never override system instructions.
-   Minimize personal data in prompts and logs.
-   Avoid retaining full chat content unless there is a documented
    business need and approved retention policy.
-   Restrict access to source documents and audit records.
-   Keep human reviewers responsible for legal/operational decisions.

## 10. Audit trail

For each request, record the minimum information needed to reconstruct
the result:

-   Request ID and timestamp.
-   Workflow version.
-   Model name/version and relevant generation settings.
-   Query classification and risk decision.
-   Retrieved document/chunk IDs and versions.
-   Citation validation result.
-   Escalation decision and reason.
-   Final outcome/status and latency.

Avoid logging unnecessary employee names, IDs, health details, or other
sensitive personal information. Define retention, access, and deletion
procedures before production.

## 11. Evaluation plan

Create a versioned offline test set with at least ten cases:

  -----------------------------------------------------------------------
  Test type                           Expected behavior
  ----------------------------------- -----------------------------------
  Straightforward onboarding question Retrieve applicable country policy
                                      and cite it

  Country-specific bank account       Answer only if evidence addresses
  question                            the condition

  Probation question                  Retrieve relevant policy and
                                      identify missing contract facts

  Notice period with tenure           Use evidence and confirm all
                                      required conditions

  Payroll cutoff                      Retrieve current country-specific
                                      operational policy

  Benefits requirement                Distinguish policy evidence from
                                      unsupported assumptions

  Missing tenure or contract type     Ask a focused follow-up or escalate

  Conflicting policy versions         Surface conflict and escalate

  Expired source                      Do not present it as current policy

  Adversarial prompt                  Ignore instructions embedded in the
                                      question or documents that attempt
                                      to bypass policy controls
  -----------------------------------------------------------------------

Suggested scoring dimensions: - Retrieval recall@k. - Answer
groundedness. - Citation precision and validity. - Correct
country/version applicability. - Clarification quality. - Escalation
precision and recall. - Unsafe unsupported-answer rate. - Latency and
tool failure rate.

For online evaluation, begin with a limited internal pilot and human
review. Compare answer usefulness, reviewer correction rate, escalation
rate, latency, and user feedback. Do not A/B test unreviewed legal
conclusions against users.

## 12. Production considerations

### Latency and resource constraints

A 1.7B local model is useful for a low-cost prototype but may struggle
with complex legal language, long contexts, and strict structured
outputs. Keep prompts concise, retrieve a small number of high-quality
chunks, and measure actual latency and output validity on the target
hardware.

### Failure behavior

-   Ollama unavailable: return a controlled service-unavailable
    response; do not fabricate an answer.
-   Embedding service unavailable: do not silently fall back to model
    memory for compliance answers.
-   Vector database unavailable: stop the evidence workflow and report
    retrieval failure.
-   No evidence: ask for clarification if appropriate, otherwise
    abstain/escalate.
-   Invalid citations or malformed output: reject the draft and use a
    safe failure response.
-   Database/audit failure: apply a documented policy; high-risk
    workflows should fail closed.

### Rollout

1.  Local development with fictional policy fixtures.
2.  Offline evaluation and manual review.
3.  Internal demo using approved, non-sensitive documents.
4.  Limited pilot with human oversight.
5.  Production readiness review covering security, privacy, legal
    governance, reliability, and monitoring.

## 13. Suggested implementation sequence

1.  FastAPI foundation and Ollama client.
2.  PDF upload and text extraction.
3.  Document/chunk metadata and version registry.
4.  Chunking and embedding generation.
5.  ChromaDB persistence and filtered retrieval.
6.  Grounded answer generation.
7.  Citation validator and safety rules.
8.  PostgreSQL audit persistence.
9.  Evaluation suite.
10. React frontend.
11. Docker Compose and operational monitoring.

This sequence keeps each milestone testable and avoids building an agent
framework before the retrieval and safety foundations are reliable.
