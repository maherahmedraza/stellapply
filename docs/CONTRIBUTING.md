# 🤝 Contributing to StellarApply

Thank you for your interest in contributing! We want to make this platform the best AI career automation tool available.

## Code of Conduct
Please communicate with respect and professionalism. Constructive feedback is welcome; harassment is not.

## Development Workflow

### 1. Branching Strategy
We use **Main-based Development**.
- `main`: The stable, deployable branch.
- Feature branches: `feature/your-feature-name`
- Fix branches: `fix/issue-description`
- Chore: `chore/maintenance-task`

### 2. Commit Messages
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: add new resume parser`
- `fix: resolve login timeout`
- `docs: update installation guide`
- `chore: bump dependencies`

### 3. Local Development
Ensure you have the environments set up (see `docs/installation.md`).

#### Backend
- Run linting: `poetry run ruff check src`
- Run type checking: `poetry run mypy src`
- Run tests: `poetry run pytest`

#### Frontend
- Run linting: `npm run lint`
- Run tests: `npm test`

## Pull Request Process
1.  Fork the repo and create your branch from `main`.
2.  Ensure all tests pass locally.
3.  Add tests for any new functionality.
4.  Open a Pull Request with a clear description of changes.
5.  Wait for code review and address feedback.

## Reporting Issues
Please use the GitHub Issues tab to report bugs or request features. Include:
- Steps to reproduce
- Expected behavior
- Screenshots (if UI related)
