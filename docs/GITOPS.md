# GitOps & Engineering Guide

This document serves as the engineered "Source of Truth" for operational procedures, environment management, and the project's technical roadmap.

## 1. Environment Strategy

EquiTracker is designed to run in two primary modes: **Local (Sovereign)** and **Production (Sovereign)**. In both cases, the principle of data sovereignty remains paramount.

### 1.1. Environment Variables (.env)

The system relies on a `.env` file in the `backend/` directory.

* **Essential Variables:** `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `OLLAMA_BASE_URL`.
* **Management:** Do NOT commit `.env` to version control. Use `.env.example` as a template.

### 1.2. Docker Safe Mode

The `docker-compose.yml` is tuned for "Safe Mode" to prevent WSL2 resource exhaustion:

* **Memory Limits:** Heap and Pagecache are explicitly limited.
* **Restart Policy:** `unless-stopped`.

## 2. Dependency Management

We maintain strict separation of concerns for reproducibility.

* **Backend (Python):** `backend/requirements.txt`. Core frameworks pinned (fastapi, neo4j), minor updates allowed for ecosystem tools.
* **Frontend (Node.js):** `frontend/package.json`. Stack: React 18, Vite, TailwindCSS.
* **Infrastructure:** `docker-compose.yml`. Official images preferred.

## 3. Future Roadmap: "JINC News Tracker"

The project is evolving towards the "JINC News Tracker" vision.

* **Phase 1: Hybrid Foundation (Current):** Neo4j Vector + Graph setup, Local Ingestion, Basic RAG Chat.
* **Phase 2: GraphRAG Implementation (Next):** Graph Construction (Entity Extraction), Community Detection (Neo4j GDS).
* **Phase 3: Autonomous Agents:** Auto-Triage & Self-Correction mechanisms.
