# GitOps & Engineering Guide

This document serves as the engineered "Source of Truth" for operational procedures, environment management, and the project's technical roadmap.

## 1. Environment Strategy

EquiTracker is designed to run in two primary modes: **Local (Sovereign)** and **Production (Sovereign)**. In both cases, the principle of data sovereignty remains paramount.

### 1.1. Environment Variables (`.env`)

The system relies on a `.env` file in the `backend/` directory.

* **Essential Variables**:
  * `NEO4J_URI`: Connection string for Neo4j (e.g., `bolt://localhost:7687`).
  * `NEO4J_USER`: Database username (default: `neo4j`).
  * `NEO4J_PASSWORD`: Database password.
  * `OLLAMA_BASE_URL`: URL for local LLM inference (e.g., `http://localhost:11434`).

* **Management**:
  * Do **NOT** commit `.env` to version control.
  * Use `.env.example` as a template for new setups.

### 1.2. Docker Safe Mode

The `docker-compose.yml` is tuned for "Safe Mode" to prevent WSL2 resource exhaustion:

* **Memory Limits**: Heap and Pagecache are explicitly limited (Total ~1GB).
* **Restart Policy**: `unless-stopped` to ensure resilience without infinite loops during configuration errors.

## 2. Dependency Management

We maintain strict separation of concerns for dependencies to ensure reproducibility.

### 2.1. Backend (Python)

* **File**: `backend/requirements.txt`
* **Philosophy**: Pin core framework versions (`fastapi`, `neo4j`) but allow minor updates for ecosystem tools (`langchain>=0.3.0`).
* **Key Dependencies**:
  * `fastapi`: API Framework.
  * `langchain-ollama`: Connection to local LLMs.
  * `crawl4ai`: Sovereign scraping wrapper.

### 2.2. Frontend (Node.js)

* **File**: `frontend/package.json`
* **Manager**: `npm`
* **Stack**: React 18, Vite, TailwindCSS.

### 2.3. Infrastructure

* **File**: `docker-compose.yml`
* **Image Strategy**: Use official images (`neo4j:5.26.0`) to ensure security and stability.

## 3. Future Roadmap: "JINC News Tracker"

The project is evolving towards the **"JINC News Tracker"** vision, moving from simple tracking to autonomous agency.

### Phase 1: Hybrid Foundation (Current)

* [x] Neo4j Vector + Graph setup.
* [x] Local Ingestion via Crawl4AI.
* [x] Basic RAG Chat.

### Phase 2: GraphRAG Implementation (Next)

* [ ] **Graph Construction**: Automatically extracting entities (People, Organizations) from text during ingestion.
* [ ] **Community Detection**: Using Neo4j Graph Data Science (GDS) to find clusters of related news.

### Phase 3: Autonomous Agents

* [ ] **Auto-Triage**: Agents that monitor reliable sources and alert on specific inclusion metrics without human intervention.
* [ ] **Self-Correction**: Mechanisms for the "Knowledge Base" to prune outdated or incorrect information.
