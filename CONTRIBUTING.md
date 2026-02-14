# Contributing to Stellapply

Welcome to Stellapply! This guide defines our git workflow, commit standards, and development practices.

---

## Git Workflow

We use a **trunk-based development** model. `main` is the production branch. All work happens on short-lived branches created from `main`.

### Branch Naming

| Prefix | Use Case | Example |
|--------|----------|---------|
| `feature/` | New functionality | `feature/stripe-billing` |
| `fix/` | Bug fixes | `fix/login-timeout` |
| `hotfix/` | Critical production fixes | `hotfix/payment-crash` |
| `chore/` | Maintenance, deps, CI | `chore/update-deps` |
| `docs/` | Documentation only | `docs/api-reference` |
| `refactor/` | Code restructuring | `refactor/billing-service` |
| `test/` | Adding or fixing tests | `test/agent-pipeline` |

### When to Create a Branch

- **Every change** starts as a branch off `main`
- A branch should address **one concern** (one feature, one bug, one chore)
- Branches should live **max 3 days** — break large work into smaller PRs
- Never work directly on `main`

### Creating a branch

```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature
```

---

## Commit Standards

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Maintenance (deps, config) |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes nor adds |
| `test` | Adding or updating tests |
| `ci` | CI/CD pipeline changes |
| `perf` | Performance improvement |
| `style` | Formatting, whitespace (no logic change) |

### Scopes

Use the module name: `agent`, `persona`, `resume`, `billing`, `auth`, `jobs`, `apps`, `infra`, `frontend`, `gdpr`, `ci`

### Examples

```
feat(agent): implement HITL approval gate
fix(billing): correct usage query for free tier
ci(docker): add multi-stage API Dockerfile
docs(api): update endpoint reference for admin routes
chore(deps): update fastapi to 0.115.0
refactor(resume): extract truth-grounding into service
test(persona): add skill verification unit tests
```

### Rules

1. **Subject line** ≤ 72 characters
2. **Imperative mood**: "add feature" not "added feature"
3. **No period** at the end of the subject
4. **Body** (optional): explain *why*, not *what*
5. **Breaking changes**: add `BREAKING CHANGE:` footer or `!` after type

---

## When and How to Commit

- Commit after each **logical unit of work** (not at end of day)
- Each commit should build and pass linting
- **Never commit**: `.env` files, API keys, passwords, secret keys, credentials

### Pushing

```bash
# Push your branch
git push origin feature/my-feature

# Force push (only on your own branch, never on main)
git push --force-with-lease origin feature/my-feature
```

---

## Pull Requests

### Creating a PR

1. Push your branch
2. Open PR against `main`
3. Fill in the PR template (if available)
4. Assign a reviewer
5. Ensure CI is green

### Merge Strategy

- All PRs use **squash merge** into `main` (clean linear history)
- PR title becomes the squash commit message (use conventional format)
- Delete branch after merge

### Requirements to Merge

- [ ] CI pipeline passes (lint + test + security)
- [ ] At least 1 approval from code owner
- [ ] No unresolved conversations
- [ ] Branch is up-to-date with `main`

---

## Hotfix Process

For critical production issues:

```bash
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix
# ... fix and test ...
git push origin hotfix/critical-fix
# Open PR → expedited review → squash merge
```

---

## Secret Protection

### Never Commit

- `.env` files (use `.env.example` as template)
- API keys, passwords, tokens
- Private keys (`.pem`, `.key`)
- Credential files

### Pre-commit Hooks

We use pre-commit hooks to catch issues before they reach CI:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

Hooks will automatically:
- Run ruff linting and formatting
- Check for secrets/credentials
- Validate commit message format
- Remove trailing whitespace

---

## Development Commands

Use the `Makefile` for common tasks:

```bash
make dev           # Start docker-compose + backend + frontend
make test          # Run all tests
make lint          # Run linting
make format        # Auto-format code
make docker-up     # Start infrastructure services
make docker-down   # Stop infrastructure services
make migration     # Create new Alembic migration
make migrate       # Run pending migrations
```
