# 🛠️ Technical Requirements

## Hardware Requirements
- **CPU:** 2+ vCPUs recommended for backend/AI processing.
- **RAM:** 4GB+ (8GB recommended for full stack with Docker).
- **Storage:** 10GB+ free space (PostgreSQL + Vectors).

## Software Prerequisites
### Development Environment
- **Operating System:** Linux (Ubuntu 22.04+), macOS, or WSL2.
- **Containerization:** Docker & Docker Compose (v2.20+).
- **Backend Runtime:** Python 3.12+ (managed via Poetry).
- **Frontend Runtime:** Node.js 20+ (LTS) & npm 10+.

### Infrastructure Services (Dockerized)
These are automatically provisioned via `docker-compose.yml`:
- **Database:** PostgreSQL 16 (extensions: `pgvector`, `pgcrypto`).
- **Cache:** Redis 7.2.
- **Identity Provider:** Keycloak 25+.
- **Search Engine:** Meilisearch (optional).

### External APIs
- **Google Gemini API:** Required for AI features (Get key from Google AI Studio).

## Network Requirements
- **Ports:**
    - `3000`: Frontend (Next.js)
    - `8000`: Backend API (FastAPI)
    - `5432`: PostgreSQL
    - `6379`: Redis
    - `8080`: Keycloak
- **Connectivity:** Outbound HTTPS access to Google APIs.
