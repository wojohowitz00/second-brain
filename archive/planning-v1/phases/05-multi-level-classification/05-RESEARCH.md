# Research: Multi-Level Classification

## Objective
Design a classification pipeline that assigns domain, PARA type, subject, and category to each message using local LLM (Ollama) with vault vocabulary from VaultScanner.

## Requirements
- CLASS-01: Classify message domain (Personal, CCBH, Just Value) — folding Phase 4 into this
- CLASS-02: Classify PARA type (Projects, Areas, Resources, Archives)
- CLASS-03: Classify subject within the PARA folder
- CLASS-04: Assign category tag to each note
- CLASS-06: Use vault vocabulary from scanner

## Key Questions

### 1. Single-Shot vs Sequential Classification?

**Option A: Single-Shot (Recommended)**
- One LLM call returns all four fields
- Pros: Faster, coherent reasoning, simpler implementation
- Cons: Longer prompt, harder to parse failures

**Option B: Sequential**
- Domain → PARA → Subject → Category (4 calls)
- Pros: Constrained choices at each step
- Cons: 4x latency, cold start multiplied, error propagation

**Decision: Single-Shot**
- Cold start is 10-30s; sequential would be 40-120s unacceptable
- Single JSON response with all fields
- Validate each field independently

### 2. How to Structure the Prompt?

```
You are classifying notes for a personal knowledge management system.

Available vocabulary:
- Domains: {domains}
- PARA Types: 1_Projects, 2_Areas, 3_Resources, 4_Archive
- Subjects: {subjects_for_context}
- Categories: meeting, task, idea, reference, journal, question

Classify this message:
"{message}"

Respond ONLY with JSON:
{
  "domain": "<domain from list>",
  "para_type": "<PARA type>",
  "subject": "<subject from list or 'general'>",
  "category": "<category from list>",
  "confidence": <0.0-1.0>,
  "reasoning": "<brief explanation>"
}
```

### 3. What Categories to Use?

Categories are message-type tags (not folder-based). Common patterns:
- **meeting**: Notes from meetings, syncs, calls
- **task**: Action items, todos, assignments
- **idea**: Brainstorms, concepts, possibilities
- **reference**: Facts, links, information to save
- **journal**: Reflections, daily notes, thoughts
- **question**: Questions to research or ask

These map to frontmatter tags, not vault structure.

### 4. How to Handle Subject Classification?

The vault has subjects nested under domain/PARA:
```
Personal/1_Projects/apps
Personal/1_Projects/writing
CCBH/2_Areas/clients
Just-Value/2_Areas/properties
```

**Approach:**
1. After domain+PARA are classified, filter subjects to that path
2. If exact subject not found, use "general" or closest match
3. Include all subjects in prompt but note the hierarchy

### 5. Error Handling Strategy?

| Failure Mode | Handling |
|--------------|----------|
| Invalid JSON | Regex fallback extraction |
| Unknown domain | Return "Personal" (default) with low confidence |
| Unknown PARA | Return "3_Resources" (default) |
| Unknown subject | Return "general" |
| Invalid category | Return "reference" |
| LLM timeout | Raise OllamaTimeout, let caller retry |
| LLM not running | Raise OllamaServerNotRunning |

### 6. Performance Targets?

From Phase 4 success criteria:
- Cold start: < 30 seconds
- Warm: < 5 seconds

Single-shot approach should meet these easily.

## Architecture Decision

```
┌─────────────────────────────────────────────────────────────┐
│                     MessageClassifier                        │
├─────────────────────────────────────────────────────────────┤
│ __init__(ollama_client, vault_scanner)                      │
│ classify(message: str) -> ClassificationResult              │
│ _build_prompt(message, vocabulary) -> str                   │
│ _parse_response(response, vocabulary) -> ClassificationResult│
│ _validate_domain(domain, valid_domains) -> str              │
│ _validate_para(para, valid_paras) -> str                    │
│ _validate_subject(subject, domain, para, structure) -> str  │
│ _validate_category(category) -> str                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ClassificationResult                       │
├─────────────────────────────────────────────────────────────┤
│ domain: str                                                 │
│ para_type: str                                              │
│ subject: str                                                │
│ category: str                                               │
│ confidence: float                                           │
│ reasoning: str                                              │
│ raw_response: Optional[str]                                 │
└─────────────────────────────────────────────────────────────┘
```

## Dependencies

- `ollama_client.py`: OllamaClient for LLM calls (Phase 3 ✓)
- `vault_scanner.py`: VaultScanner for vocabulary (Phase 2 ✓)

## Test Strategy (TDD)

1. **Unit tests with mocked LLM**:
   - Valid JSON response → correct ClassificationResult
   - Each field validated against vocabulary
   - Invalid fields normalize to defaults
   - JSON parse failures handled
   - Ollama exceptions propagate correctly

2. **Integration tests with real LLM**:
   - End-to-end classification
   - Performance within bounds
   - Various message types

## Implementation Plan

**Single plan (05-01-PLAN.md)**:
- MessageClassifier class
- ClassificationResult dataclass  
- All four classification levels
- Validation and normalization
- Unit tests (15-20 tests)
- Integration tests (3-5 tests)

## References

- Phase 3 OllamaClient: `backend/_scripts/ollama_client.py`
- Phase 2 VaultScanner: `backend/_scripts/vault_scanner.py`
- Phase 4 design inspiration: `.planning/phases/04-basic-classification/04-01-PLAN.md`
