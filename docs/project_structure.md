# Project Directory Structure

This document provides a comprehensive view of the `stellarapply` project structure as of the latest generation.

## Directory Graph

```text
.
├── alembic.ini
├── docker-compose.yml
├── docs/
│   ├── api_documentation.md
│   ├── architecture/
│   │   ├── modular_monolith.md
│   │   └── system_diagram.mermaid
│   ├── database_schema.md
│   ├── deployment.md
│   ├── installation.md
│   ├── project_structure.md
│   ├── system_architecture.md
│   └── technical_requirements.md
├── poetry.lock
├── pyproject.toml
├── README.md
├── scripts/
│   ├── generate_tree.py
│   ├── seed_db.py
│   ├── start-chrome-debug.sh
│   ├── test_agent_profile_integration.py
│   └── test_browser_engine.py
├── src/
│   ├── agent/
│   │   ├── agents/
│   │   │   ├── applicant.py
│   │   │   ├── base.py
│   │   │   ├── registrar.py
│   │   │   └── scout.py
│   │   ├── api.py
│   │   ├── brain.py
│   │   ├── browser/
│   │   │   ├── capture.py
│   │   │   ├── engine.py
│   │   │   ├── pool.py
│   │   │   ├── proxy.py
│   │   │   ├── session_store.py
│   │   │   └── stealth.py
│   │   ├── form/
│   │   │   ├── filler.py
│   │   │   └── mapper.py
│   │   ├── models/
│   │   │   └── task.py
│   │   ├── orchestrator.py
│   │   └── tasks/
│   │       ├── application.py
│   │       ├── celery_app.py
│   │       └── discovery.py
│   ├── api/
│   │   └── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database/
│   │   │   ├── alembic/
│   │   │   │   ├── env.py
│   │   │   │   └── versions/
│   │   │   ├── all_models.py
│   │   │   ├── base_model.py
│   │   │   └── connection.py
│   │   ├── logging.py
│   │   └── security/
│   │       ├── auth.py
│   │       └── encryption.py
│   └── modules/
│       ├── applications/
│       │   ├── models.py
│       │   ├── router.py
│       │   ├── schemas.py
│       │   └── service.py
│       ├── identity/
│       │   ├── domain/
│       │   │   └── models.py
│       │   └── service/
│       ├── job_search/
│       │   └── domain/
│       │       └── models.py
│       ├── persona/
│       │   └── domain/
│       │       └── models.py
│       ├── profile/
│       │   ├── models.py
│       │   ├── router.py
│       │   ├── schemas.py
│       │   └── service.py
│       └── resume/
│           └── domain/
│               └── models.py
└── tests/
    └── modules/
        └── applications/
```
