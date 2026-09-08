# Sentinel — Secure Multi-Agent RAG Framework

![Java](https://img.shields.io/badge/Java-21-007396?logo=openjdk)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.4.5-6DB33F?logo=springboot)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql)
![License](https://img.shields.io/badge/license-MIT-green)

A production-grade secure AI question-answering system. Every request passes through a multi-agent security pipeline before reaching the LLM. Four specialized agents handle input screening, document validation, RAG generation, and output validation.

---

## Architecture

React Frontend (Vite + TypeScript — port 5173)
│ JWT-authenticated REST
▼
Spring Boot Backend (Java 21 — port 8080)
AuthController │ ChatController │ DocumentController │ AuditController
JWT Filter → RBAC (@PreAuthorize) → GlobalExceptionHandler
Flyway Migrations → PostgreSQL
│ Internal HTTP
▼
FastAPI AI Engine (Python 3.11 — port 8000)
LangGraph Orchestration
security_node → chat_generation_node → validation_node
│
blocked_node

Agents:
InputSecurityAgent — prompt injection, jailbreak, PII, semantic similarity
DocumentSecurityAgent — MIME, malware, extension, size, content injection
AssistantAgent — RAG retrieval + Gemini LLM generation
OutputValidationAgent — hallucination, PII, prompt leakage, safety policy

ChromaDB (vector store) + all-MiniLM-L6-v2 embeddings


---

## Security Features

| Feature | Detail |
|---|---|
| Prompt injection defense | Five attack-pack indexes, Unicode normalization, semantic similarity scoring |
| Jailbreak detection | Pattern-based and embedding-similarity detection |
| PII detection | On both input queries and LLM responses |
| Document security pipeline | MIME, extension, size, malware validation before any document reaches the AI engine |
| Hallucination detection | Multi-metric scoring (semantic, lexical, entity, numeric) with Tier-2 Gemini judge escalation |
| Response grounding | System prompt enforces context-only answers, strips metadata from injected chunks |
| Path traversal prevention | File path validation on every upload |
| JWT + refresh token rotation | Stateless auth with silent refresh |
| RBAC | Method-level access control via `@PreAuthorize` with cached permission lookups |
| Audit logging | Every significant action logged with user, timestamp, request ID via AOP aspect |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Zustand, Axios |
| Backend | Java 21, Spring Boot 3.4.5, Spring Security, Spring Cloud OpenFeign |
| Build | Gradle 8 |
| AI Engine | Python 3.11, FastAPI, LangChain, LangGraph |
| LLM | Google Gemini 2.5 Flash via LangChain |
| Vector Store | ChromaDB, all-MiniLM-L6-v2 |
| Database | PostgreSQL 15, Flyway migrations |
| Auth | JWT (JJWT 0.12.6), BCrypt, refresh token rotation |

---

## Project Structure

sentinel/
├── sentinel-frontend/ # React + TypeScript SPA
│ └── src/
│ ├── pages/ # ChatPage, AnalyzePage, UploadPage, AuditPage
│ ├── components/ # ChatMessage, Navbar, AuditTable
│ ├── context/ # AuthContext (JWT state + Axios wiring)
│ └── api/ # axiosInstance (silent refresh interceptor)
│
├── sentinel-backend/ # Spring Boot backend
│ └── src/main/java/com/sentinel/
│ ├── auth/ # JWT, refresh tokens, registration, login
│ ├── chat/ # Chat controller, session management
│ ├── document/ # Document analysis and knowledge upload
│ ├── audit/ # AOP-based audit logging
│ ├── rbac/ # Role-permission model and cache
│ └── fastapi/ # OpenFeign client to AI engine
│
└── sentinel-Ai/ # FastAPI AI Engine
└── src/
├── assistant_agent/ # RAG generation agent
├── input_security_agent/ # Query-level threat detection
├── document_security_agent/# Document threat detection
├── output_validation_agent/# Response validation
├── knowledge_base/ # Embedder, retriever, ChromaDB, ingestion
├── llm/ # Gemini client
└── orchestration/ # LangGraph graph, nodes, orchestrator


---

## Prerequisites

- Java 21
- Python 3.11
- Node.js 18+
- PostgreSQL 15
- Google Gemini API key — https://aistudio.google.com/app/apikey

---

## Setup

### 1. FastAPI AI Engine

```bash
cd sentinel-Ai
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then edit .env with your values
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Verify:
```bash
curl http://localhost:8000/internal/health
```

---

### 2. PostgreSQL Database

```bash
createdb sentinel_db
```

---

### 3. Spring Boot Backend

```bash
cd sentinel-backend
cp .env.example .env               # then edit .env with your values
./gradlew bootRun --args='--spring.profiles.active=dev'
```

Flyway runs migrations automatically on startup. Verify:
```bash
curl http://localhost:8080/actuator/health
```

---

### 4. React Frontend

```bash
cd sentinel-frontend
npm install
# Create .env with:
# VITE_API_BASE_URL=http://localhost:8080
npm run dev
```

Open http://localhost:5173

---

## Environment Variables

### sentinel-Ai/.env

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key from Google AI Studio |
| `LLM_PROVIDER` | Set to `gemini` |
| `LLM_MODEL` | e.g. `gemini-2.5-flash` |
| `LLM_TEMPERATURE` | `0` for deterministic output |

### sentinel-backend/.env

| Variable | Description |
|---|---|
| `DB_HOST` | PostgreSQL host (default: `localhost`) |
| `DB_PORT` | PostgreSQL port (default: `5432`) |
| `DB_NAME` | Database name (default: `sentinel_db`) |
| `DB_USERNAME` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `JWT_SECRET` | Base64 secret, minimum 32 bytes |
| `JWT_ACCESS_EXPIRY_MS` | Access token TTL in ms (default: `900000` = 15 min) |
| `JWT_REFRESH_EXPIRY_MS` | Refresh token TTL in ms (default: `604800000` = 7 days) |
| `FASTAPI_BASE_URL` | AI engine URL (default: `http://localhost:8000`) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins |

---

## API Reference

### Auth — `/api/v1/auth`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register` | None | Register new user |
| POST | `/login` | None | Login, receive access + refresh tokens |
| POST | `/refresh` | None | Silent token refresh |
| POST | `/logout` | Bearer | Revoke refresh token |

### Chat — `/api/v1/chat`

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/` | Bearer | VIEWER+ | Send query through security pipeline |

### Documents — `/api/v1/documents`

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| POST | `/analyze` | Bearer | ANALYST+ | Analyze document for security threats |
| POST | `/upload` | Bearer | ANALYST+ | Ingest document into knowledge base |

### Audit — `/api/v1/audit`

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| GET | `/` | Bearer | ADMIN | Retrieve audit log |

---

## Roles

| Role | Permissions |
|---|---|
| `VIEWER` | Chat only |
| `ANALYST` | Chat, document analysis, knowledge upload |
| `ADMIN` | All permissions + audit log |

New users are assigned `VIEWER` by default.

---

## Testing

### Python tests

```bash
cd sentinel-Ai
source .venv/bin/activate
pytest
```

### Java tests

```bash
cd sentinel-backend
./gradlew test
```

Test profile uses H2 in-memory database. No PostgreSQL required for tests.

---

## Domain Packs

The `sentinel-Ai/domain_packs/` directory contains two pre-built knowledge domains:

- `banking/` — account policies, transaction FAQs, fraud policy, loan policy, KYC
- `enterprise_hr/` — employee handbook, leave, payroll, recruitment, travel policy

Each domain includes benign prompts for testing and malicious document samples for red-team evaluation.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
