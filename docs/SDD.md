---
jinc-sdd-version: 1.0.0
project-name: EquiTracker
project-context: fullstack
status: locked
related-branch: feat/conversational-ui
tech-stack: React, Vite, TailwindCSS, FastAPI, Neo4j, Groq, Gemini
created-at: 2026-07-17
last-updated: 2026-07-17
authors: Orchestrator
---

# EquiTracker - SDD & Technical Spec

## 1. North Star & Functional Scope
**Core Purpose:** Provide journalists with a conversational, zero-latency tool to analyze source credibility and inclusion bias, adhering to a "Pragmatic Sovereignty" architecture (local data, external inference).
**Primary Users:** Inclusive Journalists & Researchers.
**Critical Flows:**
- User inputs a URL in the Conversational UI.
- System fetches history of previously analyzed sources in the Sidebar.
- Backend scrapes the URL, delegates inference to an abstracted LLM provider (Groq/Gemini), and persists the `inclusion_score` and `reasoning` in Neo4j.
- Frontend displays the score badge and reasoning, maintaining strict WCAG 2.2 AAA accessibility.

## 2. Architecture (C4)
See `docs/diagrams/c4-context.mmd` for the C4 Context map.
- **Frontend Container:** React + Vite SPA. Replaces the Dashboard with a Sidebar (Source History) and Main Chat Window.
- **Backend Container:** FastAPI. Exposes REST endpoints.
- **Data Layer:** Neo4j graph database.
- **Inference Layer:** Abstraction supporting Groq, Gemini, OpenRouter, and Ollama.

## 3. Data Model (Neo4j)
The core anchor node is `Source`.
**Node Labels:** `Source`
**Properties:**
- `id` (string)
- `url` (string)
- `inclusion_score` (int) - The calculated inclusion score.
- `reasoning` (string) - The paragraph justifying the score.
- `timestamp` (datetime)

*Note: Transient chat follow-ups will be handled in frontend state for the MVP.*

## 4. Business Rules & Accessibility (WCAG 2.2 AAA)
- **UI Navigation:** Full keyboard support between Sidebar and Chat Input. No keyboard traps.
- **ARIA:** Chat messages and real-time LLM responses must use `aria-live` and proper roles (`role="log"` or `role="status"`).
- **Contrast:** `inclusion_score` badges must pass AAA contrast checks, even against the `reasoning` container background.
- **Zero-Trust LLM Config:** LLM provider keys and dynamic model names (e.g., `LLM_PROVIDER`, `GROQ_API_KEY`, `GEMINI_API_KEY`) must strictly reside in `.env` and never be hardcoded.

## 5. API Contracts
See `docs/contracts/api-v1.yaml` for the OpenAPI specification. The primary endpoint `/api/v1/sources/analyze` will return the enriched `{ inclusion_score, reasoning }` payload.
