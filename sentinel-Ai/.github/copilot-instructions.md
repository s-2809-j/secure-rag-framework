# Sentinel - GitHub Copilot Instructions

## Project Overview

Sentinel is a production-quality Secure Multi-Agent Retrieval-Augmented Generation (RAG) Framework.

The project emphasizes security, modularity, maintainability, and enterprise-grade software engineering practices.

Always preserve the existing architecture and implementation decisions unless explicitly instructed otherwise.

---

# Technology Stack

- Python 3.11
- LangChain
- ChromaDB
- Sentence Transformers
- GitHub Models (LLM)
- Pytest

---

# High-Level Architecture

Authentication + RBAC
        │
        ▼
Three Entry Points
    • Chat Request
    • Document Analysis
    • Knowledge Upload
        │
        ▼
Input Security Agent
        │
        ▼
Assistant Agent
        │
        ├── Chat
        ├── Document Analysis
        └── Knowledge Upload
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

The architecture is frozen.

Do not redesign it.

---

# Current Module

Only the Output Validation Agent is under active development.

Current phase:

Integration Testing

Do not work on:

- Orchestrator
- Deployment
- UI
- End-to-End Sentinel
- Future modules

unless explicitly instructed.

---

# Stable Modules

The following modules are complete and should be treated as stable:

- Knowledge Base
- Input Security Agent
- Assistant Agent
- Document Security Agent

Do not refactor or redesign completed modules.

---

# Output Validation Architecture

ValidationContext
        │
        ▼
OutputValidationAgent
        │
        ├── HallucinationValidator
        ├── PromptLeakageValidator
        ├── PIIValidator
        ├── SafetyPolicyValidator
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

This architecture is fixed.

---

# Factory Usage

Always use the project's factories.

Never manually construct dependencies during integration tests if a factory already exists.

---

# Coding Standards

Always:

- Follow SOLID principles.
- Use dependency injection.
- Preserve existing public APIs.
- Add type hints.
- Add meaningful docstrings.
- Write production-quality code.
- Follow existing project style.
- Keep implementations modular.
- Reuse existing components.
- Keep methods focused on a single responsibility.

---

# Things You MUST NOT Do

Never:

- Redesign the architecture.
- Rename public classes.
- Rename public methods.
- Rename folders.
- Rename modules.
- Change existing public APIs.
- Introduce unnecessary abstractions.
- Add new third-party dependencies unless requested.
- Modify unrelated files.
- Refactor completed modules.
- Duplicate existing functionality.
- Assume missing APIs.

If an API is unknown, inspect the existing implementation before using it.

---

# Implementation Workflow

Before coding:

1. Read the relevant files.
2. Understand dependencies.
3. Produce an implementation plan.
4. Wait for approval if requested.

During implementation:

- Modify only the allowed files.
- Keep changes minimal.
- Follow existing patterns.

After implementation:

- Review for architecture compliance.
- Review for SOLID.
- Review for edge cases.
- Preserve backward compatibility.

---

# Testing Rules

Use real production components whenever practical.

Prefer:

- OutputValidationAgentFactory
- GeminiLLMClient
- Real validators
- Real policy engine
- Real risk engine
- Real sanitizer

Avoid mocks unless interaction with an external dependency makes them necessary.

---

# Response Style

Do not redesign the project.

Do not suggest unrelated improvements.

Stay within the current task.

If additional project files are required, identify the complete set at once.

Separate verified facts from assumptions.

If unsure about behavior, inspect the implementation instead of guessing.