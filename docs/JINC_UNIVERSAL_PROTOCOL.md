# JINC UNIVERSAL PROTOCOL
>
> **Status:** ACTIVE
> **Role:** Master Engineering Standard
> **Scope:** DevOps, Architecture, Code Hygiene

This document establishes the **Source of Truth** for all engineering practices within the EquiTracker project. It is immutable unless updated via a specific "Protocol Amendment" task.

---

## 1. GitOps & Branching Strategy (Solo Trunk-Based)

### 1.1 The Golden Rule of Trunk

* **`main` is the Single Source of Truth.** It must always be deployable.
* Direct commits to `main` are permitted ONLY for documentation (`docs:`) or minor configuration tweaks (`chore:`). Code changes require a branch.

### 1.2 The "4-Hour Rule" (Short-Lived Branches)

* **Maximum Lifespan:** No feature branch shall exist for more than **4 hours**.
* **Lifecycle:**
    1. `git checkout -b feat/descriptive-name`
    2. **Code** (Focused implementation)
    3. **Test** (Local verification)
    4. **Merge** (Squash & Merge to `main`)
    5. **DELETE** (Immediate destruction of local and remote branch)
* *Rationale:* Long-lived branches drift. Kill them young.

### 1.3 Atomic Semantics

* **Prohibited:** `git add .` (The "Blind Add"). You must intentionally stage files.
* **Commit Format:** Conventional Commits are mandatory.
  * `feat:` New features
  * `fix:` Bug fixes
  * `refactor:` Code change that neither fixes a bug nor adds a feature
  * `docs:` Documentation only
  * `chore:` Build process or auxiliary tool changes
* *Atomic Principle:* One commit should represent one logical unit of work.

### 1.4 Context Hygiene

* **Context Switching:** NEVER switch branches with a dirty working tree.
* **Mandatory Action:** Use `git stash` before checkout if work is incomplete.

    ```bash
    git stash push -m "pausing feat/xyz to fix ab-123"
    ```

---

## 2. Coding Standards (Sovereignty First)

### 2.1 Technology Stack Sovereignty

* **Local First:** Always prioritize local, self-hosted solutions over external/paid dependencies.
  * **AI:** Ollama (Local) > OpenAI/Anthropic.
  * **DB:** Neo4j/Postgres (Docker) > Cloud DBs.
* **Docker:** The runtime environment is king. If it doesn't run in Docker, it doesn't exist.

### 2.2 Strict Typing (Zero Tolerance)

* **Frontend (TypeScript):**
  * `noImplicitAny`: **True**.
  * **Banned:** The usage of `any`. Define an Interface or Type.
* **Backend (Python):**
  * **Banned:** Untyped `dict` or `json` passing.
  * **Mandatory:** Use **Pydantic Models** for all data exchange.
  * Typing hints are required for all function arguments and return values.

### 2.3 Error Handling & Observability

* **The "No Silent Failures" Rule:**
  * Empty `except:` blocks are strictly forbidden.
  * Every `try/catch` must include explicit logging.
  * *Bad:* `pass`
  * *Good:* `logger.error(f"Failed to process source {uid}: {str(e)}")`

---

## 3. Governance & Protocol Enforcement

### 3.1 The "Technical Debt Alert" Protocol

* **Scenario:** The USER requests a "quick fix", a hack, or a violation of these standards to save time.
* **Agent Responsibility:**
    1. **OBEY:** Execute the user's request (User Command Authority > Protocol).
    2. **WARN:** Immediately append a visible warning to the response:
        > **⚠️ Technical Debt Alert:** This solution violates JINC Protocol [Section X]. Refactoring is required immediately after stability is restored.

### 3.2 Documentation as Code

* Documentation (`README.md`, `ARCHITECTURE.md`) is considered **Production Code**.
* A PR is not complete until the documentation accurately reflects the changes.
