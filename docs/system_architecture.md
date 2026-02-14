# System Architecture

## Overview

Stellapply uses a **Modular Monolith** architecture: a single deployable unit with strict module boundaries, clean dependency management, and shared infrastructure.

```
┌─────────────────────────────────────────────────────────┐
│                   Next.js Frontend                       │
│              (React, TailwindCSS, Zustand)               │
└──────────────────────┬──────────────────────────────────┘
                       │ REST + WebSocket
┌──────────────────────┴──────────────────────────────────┐
│                    FastAPI Backend                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │                   API Layer                       │   │
│  │  auth │ persona │ resume │ jobs │ apps │ billing  │   │
│  │  gdpr │ agent │ settings │ admin                  │   │
│  └──────────────────────┬───────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────┐   │
│  │              Domain / Service Layer               │   │
│  │  Identity │ Persona │ Resume │ JobSearch │ Apps   │   │
│  │  Billing │ GDPR │ CoverLetter │ AutoApply        │   │
│  └──────────────────────┬───────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────┐   │
│  │               Agent Subsystem                     │   │
│  │  Brain │ Orchestrator │ Executor │ HITL │ Browser │   │
│  │  Scout │ Registrar │ Applicant │ Recovery         │   │
│  └──────────────────────┬───────────────────────────┘   │
│  ┌──────────────────────┴───────────────────────────┐   │
│  │                Core Infrastructure                │   │
│  │  Config │ Database │ Security │ AI (Gemini)       │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
          ┌────────────┼─────────────┐
     ┌────┴────┐  ┌────┴────┐  ┌────┴────┐
     │PostgreSQL│  │  Redis  │  │  MinIO  │
     │(pgvector)│  │ (cache) │  │(storage)│
     └─────────┘  └─────────┘  └─────────┘
```

## Module Communication

- Modules communicate through **service interfaces** (Python imports)
- No cross-module database access — each module owns its tables
- The Agent subsystem consumes Profile schemas as its data bridge

## Security Architecture

1. **Authentication**: Keycloak OIDC → JWT tokens → FastAPI middleware
2. **Encryption**: Fernet encryption via EncryptedString TypeDecorator
3. **Audit**: AuditMiddleware logs all API calls
4. **GDPR**: Full data export/deletion, encryption-at-rest for PII

## AI Architecture

1. **GeminiClient**: Central AI service with rate limiting
2. **Truth-Grounding**: All AI outputs verified against Persona facts
3. **Vector Search**: pgvector embeddings for semantic job matching
4. **RAG**: QuestionAnswerer uses Persona context for form answers

## Agent Pipeline

```
Scout → Brain (score) → HITL (approve) → Applicant (fill forms)
                                              │
                              Executor (browser actions)
                                              │
                              Verifier (DOM checks)
                                              │
                        ApplicationRecord + Credentials + FormData
```
