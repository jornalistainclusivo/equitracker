# Changelog

All notable changes to the **EquiTracker** project will be documented in this file.

## [Unreleased]

### Added

- **Docs**: Comprehensive API Documentation (`docs/API_DOCS.md`).
- **Docs**: Contributing Guidelines (`CONTRIBUTING.md`).
- **Docs**: Markdown styling support in Chat Console.

### Changed

- **Docs**: Standardized `README.md` to professional English.
- **Docs**: Updated `project_status.md` to reflect Phase 3.5.

## [2026-01-19] - AI Logic & Intent Routing

### Added

- **Feat(AI)**: Implemented "Intent Router" to switch system prompts based on user input (Summary, Fact Check, Pauta).
- **Feat(AI)**: Integrated **DeepSeek-R1** model for reasoned analysis.
- **Feat(UX)**: Added "Dynamic Prompts" (Suggestion Chips) to the Chat Console.
- **Feat(Backend)**: Added endpoints for single and bulk source deletion.

### Fixed

- **Fix(AI)**: Enforced PT-BR output for all "Fact Check" responses.
- **Fix(UI)**: Resolved "missing text" hallucination in Chat Console.

## [2026-01-18] - Architecture Hardening

### Changed

- **Refactor(Infra)**: "Revived" Neo4j container with correct memory limits.
- **Refactor(Docs)**: Implemented `JINC_UNIVERSAL_PROTOCOL.md` as the supreme engineering standard.
- **Refactor(GitOps)**: Migrated to Trunk-Based Development; purged stale feature branches.

### Fixed

- **Fix(Backend)**: Resolved 500 Error caused by Neo4j datetime serialization.
- **Fix(Backend)**: Fixed `LangChainDeprecationWarning` by upgrading `langchain-neo4j`.

## [2026-01-17] - UI & Hybrid Brain

### Added

- **Feat(UI)**: Created persistent `ChatConsole` with markdown rendering.
- **Feat(UI)**: Implemented "History" page for source management.
- **Feat(AI)**: Broadened System Prompt to include Intersectional Analysis (Race, Gender, Class).
