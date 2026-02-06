# ⚙️ Configuration Guide

The application is configured via environment variables. Copy `.env.example` to `.env`.

## Core Settings
| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `APP_ENV` | Environment (dev/prod) | `dev` |
| `SECRET_KEY` | Security key for signing | **CHANGE THIS** |

## Database
| Variable | Description | Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | Async Postgres DSN | `postgresql+asyncpg://user:pass@localhost/db` |

## Authentication (Keycloak)
| Variable | Description | Default |
| :--- | :--- | :--- |
| `KC_URL` | Keycloak Server URL | `http://localhost:8081` |
| `KC_REALM` | Realm Name | `stellapply` |
| `KC_CLIENT_ID` | Client ID | `stellapply-backend` |
| `KC_CLIENT_SECRET` | Client Secret (Confidential Clients) | *Required in Prod* |

## AI Services
| Variable | Description | Required? |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini API Key | **YES** |

## Infrastructure
| Variable | Description | Default |
| :--- | :--- | :--- |
| `EVENTS_REDIS_URL` | Redis URL for Celery/Events | `redis://localhost:6379/0` |
| `ALLOWED_ORIGINS` | CORS Allowed Origins | `["http://localhost:3000"]` |
