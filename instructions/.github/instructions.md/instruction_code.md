# Project Context
You are a Senior Full Stack Data Engineer building "DataCrunch API."
The goal is to process 100k+ row datasets using AI and algorithmic sorting with an Excel-like UX.

# Tech Stack Constraints (STRICT)
- **Frontend:** Svelte 5 (Runes Mode ONLY), TypeScript, Tailwind CSS.
- **Backend:** Python 3.12, FastAPI, Celery (Redis Broker).
- **Data Engine:** Polars (Primary), DuckDB.
- **Testing:** `pytest` (Backend), `vitest` (Frontend) in a `tests/` folder.

# 🧠 The "Twin Readme" Protocol (MANDATORY)
You must maintain TWO readme files at the root. Update these after every major feature.
1. **`README.md`** (For Humans): Installation, running instructions, env setup.
2. **`AI_CONTEXT.md`** (For AI): Technical summary.
   - Log architectural decisions, DB schema snapshots, and global constants.
   - **Goal:** Any AI reading this must understand the project state without chat history.

# 📐 SOLID Principles (MANDATORY)
All code MUST adhere to SOLID principles. Enforce these in every design decision:

## 1. Single Responsibility Principle (SRP)
- **Rule:** Each class/function should have ONE reason to change.
- **Example:** 
  - ✅ `UserRepository` only handles DB operations for users.
  - ❌ `UserService` should NOT handle HTTP responses AND business logic.
- **Implementation:**
  - Separate **Routes** (HTTP handling), **Services** (business logic), **Repositories** (data access).
  - Each adapter class (e.g., `GeminiAdapter`) only handles communication with its specific AI provider.

## 2. Open/Closed Principle (OCP)
- **Rule:** Open for extension, closed for modification.
- **Example:**
  - ✅ Adding a new AI provider should NOT require modifying `AIService` core logic.
  - ✅ Use factory patterns and interfaces (abstract base classes).
- **Implementation:**
  - All AI adapters inherit from `BaseAIAdapter` abstract class.
  - New adapters register in the `_adapters` dictionary without changing orchestrator logic.

## 3. Liskov Substitution Principle (LSP)
- **Rule:** Subtypes must be substitutable for their base types.
- **Example:**
  - ✅ Any `BaseAIAdapter` subclass (Gemini, OpenAI, Claude) can be used interchangeably.
  - ❌ An adapter should NOT throw unexpected exceptions that break the contract.
- **Implementation:**
  - All adapters return `AIResponse` in the same format.
  - Consistent error handling across all implementations.

## 4. Interface Segregation Principle (ISP)
- **Rule:** Don't force classes to implement unused interfaces.
- **Example:**
  - ✅ `BaseAIAdapter` only requires `call_ai()` method, not unused methods.
  - ❌ Don't create a bloated interface with 10 methods if only 2 are used.
- **Implementation:**
  - Keep interfaces minimal and focused.
  - Use optional methods or separate interfaces for specialized behavior.

## 5. Dependency Inversion Principle (DIP)
- **Rule:** Depend on abstractions, not concrete implementations.
- **Example:**
  - ✅ `AIService` depends on `BaseAIAdapter` interface, not specific adapters.
  - ❌ Don't hardcode `GeminiAdapter()` in business logic.
- **Implementation:**
  - Use dependency injection where possible.
  - Factory pattern to resolve concrete implementations at runtime.
  - Configuration-driven adapter selection.

# 📏 Naming Conventions (STRICT)
- **Variables/Functions:** `snake_case` (e.g., `get_user_details`, `total_amount`).
  *Note: Apply strictly to Python. For JS/TS, prefer `camelCase` per industry standard, unless instructed otherwise.*
- **Classes:** `PascalCase` (e.g., `UserModel`, `OrderProcessor`).
- **Constants:** `UPPER_CASE` (e.g., `MAX_RETRY_COUNT`).
- **Files/Directories:** `snake_case` (e.g., `user_profile.py`, `data_processing/`).
- **Database Tables:** `snake_case` (e.g., `user_accounts`, `order_items`).
- **Booleans:** Prefix with `is_` or `has_` (e.g., `is_active`, `has_permissions`).

# Core Coding Rules

## 1. Frontend Architecture (Svelte 5)
- **State Management (Caching):**
  - Use **Global Shared Runes** in `src/lib/state/` (e.g., `cache_state.svelte.ts`).
  - Implement a "fetch-once" pattern: Check if data exists in the state class before triggering an API call.
- **Theming:** All colors defined in `app.css` variables. Mapped in `tailwind.config.ts`.
- **SOLID Application:**
  - Components should follow SRP (one responsibility per component).
  - Use composition over inheritance for shared logic.

## 2. Backend Architecture (FastAPI)
- **Async First:** Routes must be `async def`.
- **Structure:** Service-Repository pattern. Logic goes in `services/`, not routes.
- **Security:** AES-GCM encryption for API Keys.
- **SOLID Application:**
  - **Routes:** Only handle HTTP requests/responses (SRP).
  - **Services:** Contain business logic, orchestrate operations (SRP + DIP).
  - **Repositories:** Only handle data access (SRP).
  - **Adapters:** Follow adapter pattern for external services (OCP + LSP).

## 3. Testing Strategy (CI/CD Ready)
- **Location:** All tests reside in `tests/` folder (mirrors `src/` structure).
- **Unit Tests:** Mock all external dependencies (DB, API calls). Focus on algorithm logic.
- **Integration Tests:** Test full API endpoints using a test DB.
- **Command:** Ensure all tests run via `pytest` (Backend) and `npm test` (Frontend).
- **SOLID Testing:**
  - Test interfaces, not implementations (DIP).
  - Mock dependencies to test in isolation (ISP).

## 4. Documentation & Data Lineage (MANDATORY)
Every function MUST have a Docstring following this format:
```python
def process_data(df: pl.DataFrame, sort_col: str) -> pl.DataFrame:
    """
    Short description of function.

    Args:
        df (pl.DataFrame): The input data (Expected shape: N x M).
        sort_col (str): Column name to sort by.

    Returns:
        pl.DataFrame: The sorted dataframe.

    Raises:
        ValueError: If sort_col doesn't exist in dataframe.

    Source/Caller:
        - Called by: `services.sorting_service.execute_sort`
        - Input Source: User upload (Parquet file)
    
    SOLID Principle Applied:
        - SRP: Only handles sorting logic, no data validation or HTTP handling.
    """
```

# Design Pattern Requirements

## Factory Pattern (MANDATORY for Extensibility)
- Use for creating AI adapters, data processors, etc.
- Example: `AIService._get_adapter()` factory method.

## Adapter Pattern (MANDATORY for External Services)
- Wrap external APIs (AI providers, databases) with consistent interfaces.
- Example: `BaseAIAdapter` with provider-specific implementations.

## Strategy Pattern (RECOMMENDED for Algorithms)
- Use for interchangeable algorithms (sorting, filtering, transformations).
- Example: Different data processing strategies.

## Repository Pattern (MANDATORY for Data Access)
- Separate data access logic from business logic.
- Example: `UserRepository`, `DataRepository`.

# Code Review Checklist
Before committing any code, verify:
- [ ] Does this follow SOLID principles?
- [ ] Is each class/function doing ONE thing only? (SRP)
- [ ] Can I add new features without modifying existing code? (OCP)
- [ ] Are all implementations substitutable? (LSP)
- [ ] Are interfaces minimal and focused? (ISP)
- [ ] Am I depending on abstractions, not concrete classes? (DIP)
- [ ] Does it follow naming conventions?
- [ ] Is there proper documentation with Source/Caller info?
- [ ] Are there unit tests with proper mocking?