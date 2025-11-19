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

## 2. Backend Architecture (FastAPI)
- **Async First:** Routes must be `async def`.
- **Structure:** Service-Repository pattern. Logic goes in `services/`, not routes.
- **Security:** AES-GCM encryption for API Keys.

## 3. Testing Strategy (CI/CD Ready)
- **Location:** All tests reside in `tests/` folder (mirrors `src/` structure).
- **Unit Tests:** Mock all external dependencies (DB, API calls). Focus on algorithm logic.
- **Integration Tests:** Test full API endpoints using a test DB.
- **Command:** Ensure all tests run via `pytest` (Backend) and `npm test` (Frontend).

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

    Source/Caller:
        - Called by: `services.sorting_service.execute_sort`
        - Input Source: User upload (Parquet file)
    """