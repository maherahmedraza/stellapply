# Stellapply — Project Overview

## What is Stellapply?

Stellapply is an **autonomous job application platform** that applies to jobs on behalf of users. It combines a rich candidate identity system (Persona), AI-powered job matching, truth-grounded resume generation, and a browser-automation agent that fills out application forms — all while keeping the user in control via a Human-in-the-Loop approval flow.

## Architecture

**Modular Monolith** built with Python (FastAPI) and a Next.js frontend.

### Backend Modules

| Module | Purpose |
|--------|---------|
| **Identity** | User accounts, JWT auth via Keycloak, subscription tiers |
| **Persona** | Complete candidate profile — skills, experience, education, preferences (source of truth) |
| **Resume** | AI-enhanced resume generation with truth-grounding against Persona data |
| **Cover Letter** | Job-tailored cover letter generation using Persona context |
| **Job Search** | Job discovery, vector-similarity matching, weighted scoring |
| **Applications** | Application tracking, credential vault, form data snapshots |
| **Billing** | Subscription management, application-based usage tracking |
| **GDPR** | Data export, deletion, encryption-at-rest, audit logging |
| **Auto-Apply** | Question answering via RAG from Persona data |
| **Agent** | Browser automation pipeline — scout, register, apply |

### Agent System

The agent is the core differentiator. It operates as a pipeline:

1. **Scout Agent** — Discovers jobs from configured sources
2. **Brain** — Scores jobs against Persona for match quality
3. **HITL Gate** — Requests user approval before applying (approval_gate intervention)
4. **Applicant Agent** — Fills forms using Persona data, uploads resume
5. **Executor** — Executes browser actions with DOM verification
6. **Recovery** — Handles captchas, 2FA, and errors via HITL interventions

### Data Flow

```
Persona (Source of Truth)
    ├── JobMatcher → ScoredJobs → HITL Approval
    ├── ResumeGenerator → Truth-grounded CV
    ├── CoverLetterGenerator → Tailored letter
    └── QuestionAnswerer → RAG-based form answers
            │
            ▼
    Application Record
    ├── ApplicationCredential (encrypted portal login)
    ├── ApplicationFormData (per-page form snapshots)
    └── ApplicationEvent (status change audit trail)
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16 (pgvector, pgcrypto) |
| Cache | Redis 7 |
| AI | Google Gemini 3.0 (flash/pro), Langchain |
| Auth | Keycloak (OIDC/JWT) |
| Storage | MinIO (S3-compatible) |
| Browser | Playwright (stealth mode) |
| Frontend | Next.js 14, React, TailwindCSS, Zustand |
| Testing | Pytest, Testcontainers, Playwright |

## Key Design Principles

1. **Persona is the Source of Truth** — All AI outputs, form answers, and resume content are grounded in the user's verified Persona data
2. **Truth-Grounding** — AI enhancements include confidence scores and defensibility ratings; nothing is fabricated
3. **Human-in-the-Loop** — The agent requests approval before applying, and surfaces ambiguous decisions to the user
4. **Encryption at Rest** — All PII (emails, phone, credentials) is encrypted using Fernet with PBKDF2-derived keys
5. **Audit Trail** — Every application event, form field filled, and credential created is logged

## Getting Started

See [installation.md](installation.md) for setup instructions.
See [configuration.md](configuration.md) for environment variable reference.
See [api_documentation.md](api_documentation.md) for API endpoints.
