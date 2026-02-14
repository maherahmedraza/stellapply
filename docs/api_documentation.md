# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except `/health` and `/auth/login`) require a Bearer JWT token.

```
Authorization: Bearer <access_token>
```

Tokens are issued by Keycloak and validated by the backend.

---

## Endpoints

### Identity (`/auth`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns JWT |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Current user info |

### Settings (`/settings`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/settings/` | Get user settings (auto-apply config) |
| PUT | `/settings/` | Update user settings |

### Persona (`/persona`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/persona/` | Get full persona with all relations |
| POST | `/persona/` | Create persona |
| PUT | `/persona/` | Update persona fields |
| POST | `/persona/skills` | Add skill |
| DELETE | `/persona/skills/{id}` | Remove skill |
| POST | `/persona/experience` | Add experience |
| PUT | `/persona/experience/{id}` | Update experience |
| POST | `/persona/education` | Add education |

### Resume (`/resume`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/resume/` | List user's resumes |
| POST | `/resume/` | Create resume |
| GET | `/resume/{id}` | Get specific resume |
| POST | `/resume/enhance` | Truth-grounded AI enhancement |
| GET | `/resume/verification-context` | Get persona facts for verification |

### Job Search (`/jobs`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/jobs/` | List/search jobs |
| GET | `/jobs/{id}` | Get job details |
| GET | `/jobs/matches` | Get matches for user's persona |
| POST | `/jobs/match/{job_id}` | Score a specific job |

### Applications (`/applications`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/applications/` | List user's applications |
| POST | `/applications/` | Create application |
| GET | `/applications/{id}` | Get application with events, credentials, form data |
| PUT | `/applications/{id}` | Update application |
| POST | `/applications/{id}/events` | Add status change event |

### Billing (`/billing`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/billing/` | Get plan, usage, and invoices |
| GET | `/billing/usage` | Get current month usage counters |
| POST | `/billing/change-plan` | Change subscription tier |
| POST | `/billing/cancel` | Cancel (downgrade to free) |

### GDPR (`/gdpr`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/gdpr/export` | Export all user data |
| DELETE | `/gdpr/delete` | Delete all user data |
| GET | `/gdpr/audit-log` | View audit trail |

### Agent (`/agent`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/agent/start` | Start agent pipeline |
| GET | `/agent/status/{session_id}` | Get pipeline status |
| POST | `/agent/stop/{session_id}` | Stop running pipeline |
| GET | `/agent/interventions` | List pending HITL requests |
| POST | `/agent/interventions/{id}/respond` | Respond to intervention |
| WS | `/agent/ws/{session_id}` | Real-time pipeline events |

### Admin (`/admin`) — Admin Only

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/ai-config` | Get current AI model config |
| PUT | `/admin/ai-config` | Update AI model at runtime |
| GET | `/admin/status` | System overview (users, apps, features) |

---

## Subscription Tiers & Limits

| Tier | Price | Application Limit | Auto-Apply |
|------|-------|-------------------|------------|
| Free | €0 | 5/month | No |
| Plus | €9.99 | 50/month | No |
| Pro | €19.99 | Unlimited | Yes |
