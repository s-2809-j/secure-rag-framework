# Sentinel Orchestration Layer

## Overview

The **Orchestration Layer** is the central coordination component of the Sentinel platform.

It is responsible for routing incoming requests to the appropriate agent, coordinating the execution of the workflow, and returning a unified response.

The orchestrator **does not implement business logic**. Instead, it delegates responsibilities to specialized agents while maintaining a clear separation of concerns.

This package follows the project's architectural principles:

- Clean Architecture
- SOLID Principles
- Dependency Injection
- Factory Pattern
- High Cohesion
- Low Coupling
- Production-Quality Design

---

# Responsibilities

The orchestration layer is responsible for:

- Receiving application requests
- Determining the appropriate workflow
- Coordinating agent execution
- Normalizing responses
- Centralizing logging
- Centralizing exception handling
- Providing a single entry point into the Sentinel AI engine

---

# Non-Responsibilities

The orchestration layer must **never** implement logic that belongs to another module.

It must not:

- Detect prompt injections
- Detect jailbreaks
- Parse documents
- Validate uploaded files
- Chunk documents
- Generate embeddings
- Retrieve knowledge
- Call the LLM directly
- Perform output validation
- Execute Red Team evaluation

These responsibilities remain inside their respective agents.

---

# High-Level Architecture

```text
                         Authentication / RBAC
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
             User Query                    Document Upload
                    │                             │
                    ▼                             ▼
             Input Security Agent      Document Security Agent
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                        Sentinel Orchestrator
                                   │
                                   ▼
                          Assistant Agent
                      ┌────────────┴────────────┐
                      │                         │
                Chat Response          Knowledge Upload
                      │
                      ▼
             Output Validation Agent
                      │
                      ▼
                Final Safe Response
```

---

# Request Flow

## Chat Workflow

```text
Chat Request
      │
      ▼
Input Security Agent
      │
      ▼
Sentinel Orchestrator
      │
      ▼
Assistant Agent
      │
      ▼
Retriever
      │
      ▼
LLM
      │
      ▼
Output Validation Agent (Future)
      │
      ▼
Final Response
```

---

## Document Analysis Workflow

```text
Document Upload
      │
      ▼
Document Security Agent
      │
      ▼
Sentinel Orchestrator
      │
      ▼
Assistant Agent
      │
      ▼
Analysis Result
```

---

## Knowledge Upload Workflow

```text
Document Upload
      │
      ▼
Document Security Agent
      │
      ▼
ParsedDocument
      │
      ▼
Sentinel Orchestrator
      │
      ▼
Knowledge Ingestion Pipeline
      │
      ▼
Chunker
      │
      ▼
Embedder
      │
      ▼
Vector Store
```

---

# Package Structure

```text
orchestration/

├── __init__.py
├── factory.py
├── models.py
├── exceptions.py
├── sentinel_orchestrator.py
└── README.md
```

---

# File Responsibilities

## factory.py

Constructs and wires together all orchestration dependencies using Dependency Injection.

Responsible for creating:

- Input Security Agent
- Document Security Agent
- Assistant Agent
- (Future) Output Validation Agent
- Sentinel Orchestrator

---

## models.py

Defines orchestration-level request and response models.

Examples include:

- WorkflowType
- ChatRequest
- DocumentAnalysisRequest
- KnowledgeUploadRequest
- SentinelResponse

These models should remain independent of lower-level module models.

---

## exceptions.py

Defines orchestration-specific exception types.

Examples:

- OrchestrationError
- WorkflowRoutingError
- UnsupportedWorkflowError
- AgentExecutionError

The orchestrator should translate lower-level exceptions into these higher-level exceptions.

---

## sentinel_orchestrator.py

Implements the central workflow coordinator.

Responsibilities:

- Route incoming requests
- Invoke the correct agent
- Normalize responses
- Handle logging
- Handle orchestration-level exceptions

The orchestrator must remain lightweight and free of business logic.

---

# Design Principles

The orchestration layer follows these design principles:

- Single Responsibility Principle (SRP)
- Dependency Inversion Principle (DIP)
- Separation of Concerns
- Dependency Injection
- Factory Pattern
- Open/Closed Principle
- High Cohesion
- Low Coupling

---

# Logging

The orchestrator serves as the root logging point for request execution.

Typical log information includes:

- Request Identifier
- Workflow Type
- Processing Duration
- Agent Execution Status
- Success or Failure
- Error Information

Business-level logging should remain within the respective agents.

---

# Error Handling

The orchestration layer centralizes exception management.

Lower-level exceptions should be wrapped into orchestration-specific exceptions before propagating them to the caller.

This ensures a consistent error contract across the platform.

---

# Future Integration

The orchestrator is designed to support future integrations without requiring architectural changes.

Planned integrations include:

- Output Validation Agent
- Red Team Agent
- LangGraph-based workflow orchestration
- FastAPI application layer
- Spring Boot enterprise backend
- Frontend application
- MCP (Model Context Protocol) client integration
- Sentinel MCP Server

---

# Extension Guidelines

When extending this package:

- Do not duplicate functionality from existing agents.
- Keep orchestration logic separate from business logic.
- Prefer composition over inheritance.
- Preserve backward compatibility.
- Follow the existing Dependency Injection pattern.
- Avoid introducing circular dependencies.

---

# Current Status

| Component | Status |
|-----------|--------|
| Request Routing | Planned |
| Dependency Injection | Planned |
| Response Normalization | Planned |
| Logging | Planned |
| Exception Handling | Planned |
| Output Validation Hook | Planned |
| Red Team Hook | Planned |
| LangGraph Integration | Planned |

---

# Goal

The orchestration layer provides a single, consistent entry point into the Sentinel platform by coordinating specialized agents while preserving modularity, maintainability, extensibility, and production-quality design.