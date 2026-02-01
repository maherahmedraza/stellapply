# Stellapply Architecture: Modular Monolith (Python)

## Overview
The Stellapply backend is designed as a **Modular Monolith**. This approach balances the simplicity of a single codebase with the scalability and clear boundaries of microservices.

## Directory Structure

### `src/core` (Shared Kernel)
Contains cross-cutting concerns that are shared across all business modules.
- **Config**: Environment and application configuration.
- **Database**: Connection pooling and base model definitions.
- **Security**: Field-level encryption, hashing, and JWT management.
- **Events**: Internal event bus for inter-module communication.

### `src/modules` (Business Domains)
Each business unit lives in its own module. Modules are isolated and communicate only through their public APIs or the Internal Event Bus.
- **Identity**: Authentication and authorization.
- **Persona**: User profile and vector embedding management.
- **Resume**: Document generation and ATS analysis.
- **Job Search**: Job scraping and AI matching.
- **Auto-Apply**: Playwright-based browser automation.
- **Analytics/Billing/Notifications**: Supporting business services.

### `src/api` (Gateway Layer)
Entry point for the application. Handles routing, global middleware (auth, rate limiting, logging), and dependency injection.

### `src/workers` (Background Jobs)
Execution layer for long-running tasks using Celery.

## Development Principles
1. **Modules must not depend on each other's domain models**. Use DTOs or Events for communication.
2. **Core should remain thin**. Only infrastructure-level code belongs in `core`.
3. **Internal Event Bus**: Use local events to trigger side-effects in other modules (e.g., "RegistrationComplete" triggers "WelcomeEmail").
