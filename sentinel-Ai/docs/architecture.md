# Sentinel — Architecture (Frozen)

Sentinel is a Secure Multi-Agent Retrieval-Augmented Generation (RAG)
framework. It securely answers user queries, analyzes uploaded documents,
ingests trusted knowledge, validates LLM outputs, and supports red-team
evaluation.

**This architecture is final. Do not redesign it without explicit
instruction.**

## Overall system flow

```
                    Authentication + RBAC
                             │
                             ▼
                  ┌───────────────────────┐
                  │ Three Entry Points     │
                  │----------------------- │
                  │ 1. Chat Request        │
                  │ 2. Document Analysis   │
                  │ 3. Knowledge Upload    │
                  └───────────────────────┘
                             │
                             ▼
                  Input Security Agent
                             │
                             ▼
                    Assistant Agent
                   /        |         \
                  /         |          \
                 ▼          ▼           ▼
        Chat Response   Document     Knowledge
                         Analysis     Ingestion
                             │
                             ▼
                         Retriever
                             │
                             ▼
                          ChromaDB
                             │
                             ▼
                             LLM
                             │
                             ▼
                 Output Validation Agent
                             │
                             ▼
                     Final Response
                             │
                             ▼
                      Red-Team Agent
```

## Output Validation Agent architecture (frozen)

```
ValidationContext
        │
        ▼
OutputValidationAgent
        │
        ├───────────────┬───────────────┬───────────────┬───────────────┐
        ▼               ▼               ▼               ▼
Hallucination    Prompt Leakage      PII         Safety Policy
 Validator          Validator      Validator      Validator
        │               │               │               │
        └───────────────┴───────────────┴───────────────┘
                        │
                        ▼
              OutputPolicyEngine
                        │
                        ▼
               OutputRiskEngine
                        │
                        ▼
             ResponseSanitizer
                        │
                        ▼
              ValidationDecision
```

### Output Validation Factory builds

- Embedder
- SentenceSplitter
- SemanticSimilarityScorer
- KeywordOverlapScorer
- EntityOverlapScorer
- NumericConsistencyScorer
- CitationMatchScorer
- SupportScoreAggregator
- EscalationPolicy
- Tier2Judge
- ResultAggregator
- HallucinationValidator
- PromptLeakageValidator
- PIIValidator
- SafetyPolicyValidator
- OutputPolicyEngine
- OutputRiskEngine
- ResponseSanitizer
- OutputValidationAgent

Always use the factory in integration tests. Never manually recreate
dependencies by hand in a test.

## Repository layout (as of last audit)

```
src/
├── assistant_agent/
├── common/
├── document_security_agent/
│   ├── aggregation/ chunking/ detector/ escalation/ factory/
│   ├── file_guard/ parser/ preprocessing/ tier2/
├── input_security_agent/
│   ├── attack_packs/ detectors/ execution/ factory/
│   ├── loader/ policies/ preprocessing/ scoring/ semantic/
├── knowledge_base/
│   └── ingestion/
├── llm/
│   ├── parsers/ prompts/
├── orchestration/
├── output_validation_agent/
│   ├── policies/ risk/ sanitizer/
│   └── validators/
│       ├── rules/ safety/ support/ (scores/)
└── shared/

tests/            (mirrors src/ structure, one folder per module)
domain_packs/      (ingestion/red-team fixture data: banking, enterprise_hr)
```

**Note:** `orchestration/` and `document_security_agent/` already have real
implementation and tests in this repo, even though they are out of scope for
the current phase. Do not touch them unless the current objective says so.