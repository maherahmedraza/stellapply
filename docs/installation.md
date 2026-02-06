# 📦 Installation Guide

## Option 1: Docker (Recommended)
The easiest way to get started is using Docker Compose.

### Prerequisites
- Docker Desktop or Docker Engine + Compose Plugin

### Steps
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/maherahmedraza/stellapply.git
    cd stellapply
    ```
2.  **Configure Environment:**
    ```bash
    cp .env.example .env
    # Edit .env and add your GEMINI_API_KEY
    ```
3.  **Start Services:**
    ```bash
    docker compose up -d
    ```
    This starts Postgres, Redis, Keycloak, and running migrations may handle automagically or need a manual step.

4.  **Verify:**
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend: [http://localhost:8000/docs](http://localhost:8000/docs)

## Option 2: Manual Setup

### 1. Database & Infrastructure
You still need Postgres, Redis, and Keycloak.
```bash
docker compose up -d db redis keycloak
```

### 2. Backend (Python/FastAPI)
1.  Install **Poetry**: `pip install poetry`
2.  Install dependencies:
    ```bash
    poetry install
    ```
3.  Run migrations:
    ```bash
    poetry run alembic upgrade head
    ```
4.  Start server:
    ```bash
    poetry run uvicorn src.api.main:app --reload
    ```

### 3. Frontend (Next.js)
1.  Navigate to proper directory: `cd frontend`
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start dev server:
    ```bash
    npm run dev
    ```
