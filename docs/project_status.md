# 📰 Project Status: EquiTracker

> **Mission:** A Sovereign AI News Tracker for Equity & Inclusion.
> **Architecture:** Hybrid Brain (Neo4j + Ollama)
> **Current Phase:** v2.0 Alpha (Security & Foundation)
> **Last Updated:** 2026-01-20

## 📋 Executive Summary

EquiTracker is establishing a new paradigm in data analysis: **Radical Sovereignty**. By moving the full intelligence cycle—collection, analysis, and storage—to the local environment, we eliminate reliance on external commercial APIs.

Our current focus is stabilizing the **Hybrid Brain** architecture, which combines the deterministic power of Graph Databases (Neo4j) with the semantic understanding of Local LLMs (Ollama), ensuring privacy-first insights into media bias.

---

## ✅ Completed Features (Foundation)

### 🛡️ Sovereign Security & Core

* **SSRF Protection Layer:** Implemented rigorous IP and scheme validation in the `SovereignScraper` to prevent internal network attacks.
* **Graph Memory (Neo4j):** Successfully integrated Neo4j 5.x as the unified storage engine, binding strictly to `localhost` to ensure air-gapped security.
* **Error Containment:** Standardized API error responses to prevent infrastructure leakage while maintaining detailed internal logging.

### 🧠 Intelligence & Analysis

* **Local-First Analysis:** Integrated **Ollama** for inclusion auditing, enabling cost-zero operation.
* **Data Contracts:** Unified schema definitions (`inclusion_score`) across Backend and Frontend to ensure data integrity.

### 💻 User Experience (Dashboard)

* **Real-time Monitoring:** React-based dashboard for managing media sources.
* **Inclusion Scoring:** Visual representation of equity metrics in the History view.

---

## 🚧 In Progress (The "Hybrid" Shift)

* **Vector Memory Integration:** Configuring Neo4j to handle vector embeddings, completing the "Hybrid Brain" (Graph + Vector) vision to save RAM on WSL2 environments.
* **Dependency Locking:** hardening the supply chain by freezing `requirements.txt` and `package.json` versions.
* **CI/CD Governance:** Activating automated security scans (TruffleHog, Dependabot) via GitHub Actions.

---

## 🔮 Roadmap: Towards v2.0

* **Q1 2026: The Semantic Leap**
  * Implementation of **RAG (Retrieval-Augmented Generation)** using the stored vector embeddings.
  * Launch of the **Multi-Agent System** (ProductArchitect & InclusiAI personas).

* **Q2 2026: Expansion**
  * **Visual Bias Analysis:** Extending scrutiny to imagery within news articles.
  * **Browser Integration:** Chrome Extension for seamless source ingestion.

---

## 📚 Documentation & Protocols

This project adheres to strict engineering standards. Refer to:

* **[Architecture Guide](ARCHITECTURE.md):** Deep dive into the Hybrid Brain concept.
* **[JINC Universal Protocol](JINC_UNIVERSAL_PROTOCOL.md):** Our "Source of Truth" for engineering practices.
* **[Contributing](CONTRIBUTING.md):** How to join the engineering team.
