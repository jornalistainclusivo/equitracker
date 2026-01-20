# Contributing to EquiTracker

Welcome to the EquiTracker engineering team. This project follows strict engineering standards to ensure sovereignty, privacy, and code quality.

## Core Protocols

All contributors must adhere to the **[JINC Universal Protocol](docs/JINC_UNIVERSAL_PROTOCOL.md)**.

### 1. GitOps & Branching

We use a **Trunk-Based Development** workflow with strict lifespan limits.

- **Main Branch**: `main` is the single source of truth and must always be deployable.
- **Feature Branches**:
  - Naming: `feat/name`, `fix/issue`, `docs/topic`.
  - **Max Lifespan**: 4 Hours. If a branch lives longer than 4 hours, it is considered drift.
  - **Merge Strategy**: Squash & Merge only.
- **Commit Messages**: Must follow [Conventional Commits](https://www.conventionalcommits.org/).
  - `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`.

### 2. Technology Stack (Sovereignty First)

- **AI**: Local models only (Ollama). No reliance on OpenAI/Anthropic APIs.
- **Database**: Neo4j (Graph + Vector) and PostgreSQL running in Docker.
- **Runtime**: Docker is the standard. "It works on my machine" is not a valid excuse.

### 3. Coding Standards

#### TypeScript (Frontend)

- **Strict Typing**: `noImplicitAny` is enforced. Do not use `any`.
- Define Interfaces for all data structures.

#### Python (Backend)

- **Pydantic**: All data exchange must be validated with Pydantic models.
- **Typing**: Type hints are mandatory for all function arguments and return values.
- **Error Handling**: No silent failures. Every `try/except` block must log the error.

## Development Setup

1. **Infrastructure**: `docker-compose up -d`
2. **Backend**:

   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

3. **Frontend**:

   ```bash
   cd frontend
   npm run dev
   ```

## Documentation

Documentation is treated as code. Any code change that alters behavior must include a corresponding update to `README.md` or `docs/`.
