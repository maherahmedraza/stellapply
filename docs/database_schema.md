# 🗄️ Database Schema

## Overview
The database is **PostgreSQL 16**.
- **ORM:** SQLAlchemy 2.0 (Async)
- **Migration Tool:** Alembic
- **Key Extensions:**
    - `pgvector`: For storing embeddings (job descriptions, resumes).
    - `pgcrypto`: For cryptographic functions.

## Core Tables

### `users`
Stores user references (linked to Keycloak ID).
- `id` (UUID, PK)
- `email` (String, UQ)
- `external_id` (String, Keycloak Sub)
- `created_at` (Timestamp)

### `resumes`
Stores structured resume data.
- `id` (UUID, PK)
- `user_id` (UUID, FK)
- `content` (JSONB) - Full structured data
- `embedding` (VECTOR) - Semantic representation
- `is_active` (Boolean)

### `personas`
Career profiles for job matching.
- `id` (UUID, PK)
- `user_id` (UUID, FK)
- `skills` (JSONB/Array)
- `experience_level` (String)
- `target_query` (String)

### `jobs`
Cached/Scraped job listings.
- `id` (UUID, PK)
- `title` (String)
- `company` (String)
- `description` (Text)
- `embedding` (VECTOR) - For semantic matching
- `url` (String)

### `audit_logs`
Immutable logs for security/GDPR.
- `id` (UUID, PK)
- `user_id` (UUID, FK)
- `action` (String)
- `timestamp` (Timestamp)
- `ip_address` (String)
- `resource_id` (String)
- `previous_hash` (String) - For tamper-evidence

## Relationships
- **One User** has **One Persona** (Active).
- **One User** can have **Many Resumes**.
- **One User** has **Many Audit Logs**.
- **Audit Logs** are append-only.
