# Sentinel — Module Status

Last verified: local `pytest tests/ -v` run, 121 tests collected, 110 passed,
11 failed, 0 collection errors (after `pytest.ini` + import-path fixes below).

Status labels used below:
- **Verified** — confirmed by reading actual source/tests, not assumed.
- **Assumed** — stated in earlier project notes but not independently
  confirmed against source. Treat with caution until verified.

## Completed modules (Verified — source + tests exist and pass)

| Module | Source | Tests | Status |
|---|---|---|---|
| Knowledge Base (loader, chunker, embedder, vector store, retriever, ingestion pipeline) | `src/knowledge_base/` | `tests/llm/*`, `tests/knowledge_base_test/*` | Passing |
| Input Security Agent (prompt injection, jailbreak, similarity, PII, normalizer, rule engine, attack pack loader) | `src/input_security_agent/` | `tests/input_security_agent/*` | Passing |
| Assistant Agent (chat, document analysis, knowledge upload, retriever + LLM integration) | `src/assistant_agent/` | `tests/assistant_agent/*` | Passing (after import-path fix, see below) |
| Document Security Agent | `src/document_security_agent/` | `tests/document_security_agent/*` | Passing — **not mentioned in original project brief; exists and is out of current scope** |
| Orchestration | `src/orchestration/` | `tests/orchestrator/*` | Passing — **not mentioned in original project brief; exists and is out of current scope** |

## Current module — Output Validation Agent

**Phase: Integration Testing** (per project methodology: Implement →
Architecture Review → Critical Fixes Only → Unit Testing → Integration
Testing → Integration into Sentinel → System Integration Testing → Next
Module).

- Implementation: **Verified present** — `factory.py`, `models.py`,
  `output_validation_agent.py`, `policies/`, `risk/`, `sanitizer/`,
  `validators/` (all four validators + rules/safety/support subpackages)
  all exist in `src/output_validation_agent/`.
- Tests: **Verified present** — 12 test files in
  `tests/output_validation_agent/`, including
  `test_output_validation_integration.py`.
- **Known open bug (blocking this phase):**
  `HallucinationValidator._escalation_policy` is `None` at runtime, causing
  `AttributeError: 'NoneType' object has no attribute 'decide'` in
  `hallucination_validator.py` line ~196 (`_process_sentence` →
  `self._escalation_policy.decide(...)`).
  - Root cause not yet confirmed: could be the factory not injecting
    `EscalationPolicy` into `HallucinationValidator`'s constructor, a bad
    default value, or test fixtures not providing it.
  - This single root cause explains all 11 currently failing tests:
    - `tests/output_validation_agent/test_hallucination_validator.py` (6 tests)
    - `tests/assistant_agent/test_assistant_agent.py` (4 tests, fails
      downstream through `AssistantAgent` → `OutputValidationAgent` →
      `HallucinationValidator`)

**Do not move past this phase until:**
1. The `EscalationPolicy` injection bug is fixed with a reviewed diff.
2. `pytest tests/` shows 0 failures, 0 errors.
3. A gap audit confirms `test_output_validation_integration.py` actually
   uses real components (factory-built), not mocks, per
   `docs/development_rules.md`.

## Environment fixes already applied (do not redo)

- `pytest.ini` created at repo root:
  ```ini
  [pytest]
  pythonpath = .
  addopts = --import-mode=importlib
  ```
  (Fixes `ModuleNotFoundError: No module named 'src'` and duplicate
  `test_factory.py` collection collisions across module test folders.)
- `tests/assistant_agent/test_assistant_agent.py`: fixed import —
  `AgentDecision`, `PolicyEvaluation`, `RiskAssessment`, `RiskLevel` moved
  from wrong import (`src.knowledge_base.models`) to correct source
  (`src.input_security_agent.models`), where they're actually defined.
- `tests/llm/test_pipelineupto7.py`: fixed typo `src.assistent_agent` →
  `src.assistant_agent`.

## Known housekeeping items (not blocking, low priority)

- `requirments.txt` → should be renamed `requirements.txt` (typo).
- Stray `document_security_agent.zip` in `src/` alongside the real unzipped
  folder — likely safe to delete, not yet confirmed.
- `llm/parsers/tire2_response_parser.py` and
  `llm/prompts/tire2_security_prompt.py` — likely meant to say "tier2"
  (matches `tier2_judge.py`, `tier2_detection_engine.py` elsewhere).
  Renaming touches existing imports — confirm before changing.
- `temp_import_test.py` at repo root — appears to be a scratch file, not
  yet confirmed safe to delete.
- Mixed `cpython-311`/`cpython-312` `.pyc` artifacts were found in
  `__pycache__` before cleanup — confirm the project consistently uses one
  Python version (3.11, per `pytest` header) going forward.

## Explicitly out of scope right now

Per current objective: do not discuss or implement orchestrator
integration, end-to-end Sentinel tests, deployment, or any module beyond
Output Validation Agent, even though `orchestration/` already has code —
that code is not part of the active phase.