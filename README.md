# EquiTracker

**A Sovereign AI News Tracker for Equity & Inclusion.**

EquiTracker is a local-first, privacy-focused intelligence platform that monitors, ingests, and analyzes news sources to track equity and inclusion metrics. Built on a "Hybrid Brain" architecture, it combines the deterministic power of Graph Databases (Neo4j) with the semantic understanding of Local LLMs (Ollama) to provide sovereign insights without relying on external commercial APIs.

## Quick Start

Follow this exact sequence to launch the full stack.

### 1. Infrastructure (Docker)

Start the Neo4j Graph Database.

```bash
docker-compose up -d
```

### 2. Backend (Python/FastAPI)

Activate the environment and start the API server.

```bash
cd backend
# Windows
venv\Scripts\activate
# Start Server
uvicorn app.main:app --reload
```

### 3. Frontend (React/Vite)

Launch the dashboard interface.

```bash
cd frontend
npm run dev
```

## System Architecture

The system utilizes a "Sovereign Ingestion" pipeline (Crawl4AI) and a "Hybrid Brain" (Neo4j + Ollama).

- **Sovereign Ingestion**: Bypasses commercial APIs using local browser automation.
- **Hybrid Memory**: Combines Vector Search (Semantic) and Graph Traversal (Contextual).
- **Local Intelligence**: Powered by Ollama to ensure data privacy and zero egress costs.

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Documentation

- **[Project Status](docs/project_status.md)**: Current roadmap and completed features.
- **[API Documentation](docs/API_DOCS.md)**: detailed API endpoint reference.
- **[Contributing Guide](CONTRIBUTING.md)**: Engineering standards and GitOps protocols.
- **[Engineering & GitOps](docs/GITOPS.md)**: Environment management and technical guide.
- **[Changelog](CHANGELOG.md)**: History of changes.
