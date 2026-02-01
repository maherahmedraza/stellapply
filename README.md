# 🌟 StellarApply.ai

**Enterprise-Grade AI-Powered Career Platform**  
*GDPR-compliant career automation with intelligent resume building, job matching, and application tracking.*

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/fastapi-0.115-green.svg)]()
[![Next.js](https://img.shields.io/badge/next.js-16-black.svg)]()

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Resume Builder** | Upload PDF/DOCX, Gemini AI auto-extracts and fills all fields |
| 🎯 **Smart Job Matching** | Vector similarity search with persona-based matching scores |
| 📊 **ATS Optimization** | Real-time resume analysis with improvement suggestions |
| 🔒 **GDPR/DSGVO Compliance** | Full German data protection compliance with consent management |
| 🔐 **Enterprise Security** | Field-level encryption, immutable audit logs, Keycloak SSO |

---

## 🏗️ Architecture: Modular Monolith

```mermaid
graph TD
    subgraph "Frontend (Next.js 16)"
        UI["React 19 + TailwindCSS 4"]
        State["Zustand + TanStack Query"]
    end

    subgraph "API Gateway (FastAPI)"
        Auth["Auth Middleware (Keycloak)"]
        GDPR["GDPR APIs (Consent/Export/Erasure)"]
    end

    subgraph "Core Infrastructure"
        Security["Encryption (Fernet) + Audit Logs"]
        Database["PostgreSQL 16 (pgvector + pgcrypto)"]
        Cache["Redis + Meilisearch"]
    end

    subgraph "Business Modules"
        Identity["Identity (OAuth2/OIDC)"]
        Persona["Persona (Embeddings)"]
        Resume["Resume (AI Parser)"]
        JobSearch["Job Search (Matching)"]
    end

    subgraph "AI Layer"
        Gemini["Google Gemini API"]
    end

    UI --> Auth
    Auth --> Identity
    Auth --> Persona
    Auth --> Resume
    Auth --> JobSearch
    Auth --> GDPR
    
    Resume --> Gemini
    JobSearch --> Gemini
    
    Identity --> Database
    Persona --> Database
    Resume --> Database
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12+ | Core runtime |
| FastAPI | 0.115 | API framework |
| Pydantic | v2 | Data validation |
| SQLAlchemy | 2.0 | ORM |
| PostgreSQL | 16 | Database (pgvector, pgcrypto) |
| Redis | 7+ | Caching |
| Keycloak | 25+ | Identity & SSO |
| Google Gemini | 1.5+ | AI capabilities |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16 | React framework |
| React | 19 | UI library |
| TailwindCSS | 4 | Styling |
| Zustand | 5.0 | State management |
| TanStack Query | 5.90 | Server state |
| React Hook Form | 7.71 | Forms |
| Zod | 4.3 | Validation |
| Framer Motion | 12 | Animations |

### Security & Compliance
| Component | Implementation |
|-----------|----------------|
| Field Encryption | Fernet + PBKDF2 |
| Audit Logging | Immutable hash-chained logs |
| Authentication | Keycloak OAuth2/OIDC |
| GDPR Compliance | Consent management, data portability, erasure APIs |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ with Poetry
- Node.js 20+

### 1. Clone & Configure
```bash
git clone https://github.com/your-org/stellapply.git
cd stellapply

# Copy environment template (NEVER commit real secrets)
cp .env.example .env
```

### 2. Start Infrastructure
```bash
docker compose up -d
```

### 3. Run Backend
```bash
cd backend
poetry install
poetry run uvicorn src.api.main:app --reload --port 8000
```

### 4. Run Frontend
```bash
cd frontend
npm install
npm run dev
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Keycloak**: http://localhost:8080

---

## 📁 Project Structure

```
stellapply/
├── src/                     # Backend (Python/FastAPI)
│   ├── api/                 # Entry point & middleware
│   ├── core/                # Shared infrastructure
│   │   ├── ai/              # Gemini client
│   │   ├── database/        # DB connection & governance
│   │   └── security/        # Encryption & audit
│   └── modules/             # Domain modules
│       ├── identity/        # Auth & users
│       ├── persona/         # Career profile
│       ├── resume/          # Resume builder & AI
│       ├── job_search/      # Job matching
│       └── gdpr/            # GDPR compliance
├── frontend/                # Next.js 16 app
│   ├── src/app/             # App router pages
│   └── src/components/      # React components
├── docker-compose.yml       # Local infrastructure
└── scripts/                 # Utility scripts
```

---

## 🔐 Security & GDPR

### Environment Variables (Required in `.env`)
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/stellapply

# Security
SECRET_KEY=your-256-bit-secret-key
ENCRYPTION_KEY=your-fernet-encryption-key

# Keycloak
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=stellapply
KEYCLOAK_CLIENT_ID=stellapply-backend
KEYCLOAK_CLIENT_SECRET=your-client-secret

# AI
GEMINI_API_KEY=your-gemini-api-key
```

> ⚠️ **NEVER commit `.env` files!** The `.gitignore` already excludes them.

### GDPR APIs
| Endpoint | Right | Description |
|----------|-------|-------------|
| `GET /api/v1/gdpr/consent` | Art. 7 | View consent status |
| `PUT /api/v1/gdpr/consent` | Art. 7 | Grant/withdraw consent |
| `POST /api/v1/gdpr/export` | Art. 20 | Data portability |
| `POST /api/v1/gdpr/erasure` | Art. 17 | Right to erasure |

---

## 🧪 Testing

```bash
# Backend tests
poetry run pytest tests/ -v

# Frontend tests
cd frontend && npm test

# Type checking
poetry run mypy src/
```

---

## 📝 API Documentation

Interactive API docs available at `/docs` when server is running.

Key endpoints:
- `POST /api/v1/resume/upload` - Upload & parse resume with AI
- `GET /api/v1/jobs` - Search jobs with location/salary filters
- `POST /api/v1/persona` - Create career profile

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Follow [Conventional Commits](https://www.conventionalcommits.org/)
3. Run linting: `poetry run ruff check src/`
4. Submit PR for review

---

## ⚖️ License

Proprietary. All rights reserved © StellarApply.ai
