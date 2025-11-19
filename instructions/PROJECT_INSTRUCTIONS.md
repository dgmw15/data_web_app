# DataCrunch - Project Instructions & Guidelines

## Project Overview
**DataCrunch** is a high-performance data processing web application with an Excel-like user experience, built for handling large datasets efficiently.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Data Processing**: 
  - Polars (main engine for data manipulation)
  - DuckDB (SQL queries on large datasets)
- **Task Queue**: Celery with Redis broker
- **Server**: Uvicorn (ASGI server)

### Frontend
- **Framework**: Svelte 5 (latest with runes)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Language**: TypeScript

### Architecture
- **Pattern**: Repository Pattern with Service Layer
- **API**: RESTful with FastAPI
- **State Management**: Svelte 5 runes ($state, $derived, $effect)

---

## Project Structure

```
data_web_app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/             # API route handlers
│   │   │       └── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py           # Settings & configuration
│   │   ├── db/
│   │   │   └── __init__.py         # Database connection
│   │   ├── models/
│   │   │   └── __init__.py         # Data models (Pydantic)
│   │   ├── repositories/
│   │   │   └── __init__.py         # Data access layer
│   │   ├── schemas/
│   │   │   └── __init__.py         # Request/Response schemas
│   │   ├── services/
│   │   │   └── __init__.py         # Business logic layer
│   │   └── utils/
│   │       └── __init__.py         # Helper functions
│   ├── tests/
│   │   └── __init__.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/         # Reusable Svelte components
│   │   │   ├── state/              # Global state stores (runes)
│   │   │   └── utils/              # Utility functions
│   │   ├── routes/                 # Page routes
│   │   └── assets/                 # Static assets
│   ├── tests/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
│
├── data/                           # Data files (gitignored)
├── docs/                           # Documentation
├── instructions/                   # This file and related docs
├── .gitignore
└── README.md
```

---

## Development Guidelines

### Code Style & Documentation

#### Python (Backend)
1. **Docstring Format**: Use Google-style docstrings for all functions/classes
2. **Type Hints**: Always include type hints for function parameters and returns
3. **Imports**: Group imports (stdlib, third-party, local) with blank lines
4. **Source/Caller Comments**: Add `Source/Caller:` section in docstrings to track data flow

Example:
```python
def process_data(df: pl.DataFrame, filters: dict[str, Any]) -> pl.DataFrame:
    """
    Process dataframe with given filters.
    
    Args:
        df (pl.DataFrame): Input dataframe
        filters (dict[str, Any]): Filter conditions
    
    Returns:
        pl.DataFrame: Filtered dataframe
    
    Source/Caller:
        - Called by: DataService.get_filtered_data()
        - Calls: FilterRepository.apply_filters()
    """
    pass
```

#### TypeScript/Svelte (Frontend)
1. **TypeScript**: Use strict mode, define interfaces for all props
2. **Svelte 5 Runes**: Use `$state`, `$derived`, `$effect` for reactivity
3. **Components**: Keep components small and focused
4. **Comments**: Add JSDoc comments for exported functions

Example:
```typescript
interface DataGridProps {
  data: any[];
  columns: Column[];
  onCellEdit?: (row: number, col: string, value: any) => void;
}

/**
 * DataGrid component with Excel-like editing
 * Source/Caller: Used in routes/data/+page.svelte
 */
export function DataGrid(props: DataGridProps) {
  let { data, columns, onCellEdit } = $props();
  let selectedCell = $state<{row: number, col: string} | null>(null);
  // ...
}
```

### Architecture Patterns

#### Backend: Repository Pattern
```
Controller (Routes) → Service Layer → Repository Layer → Data Source
```

- **Routes**: Handle HTTP requests/responses, validation
- **Services**: Business logic, orchestration
- **Repositories**: Data access, queries

#### Frontend: Component-Based
```
Route → Page Component → Feature Components → UI Components
```

- **Routes**: Top-level pages
- **Feature Components**: Domain-specific logic
- **UI Components**: Reusable, presentational

### Performance Considerations

1. **Data Processing**:
   - Use Polars for in-memory operations (lazy evaluation when possible)
   - Use DuckDB for SQL queries on large files
   - Offload heavy tasks to Celery workers

2. **Frontend**:
   - Virtual scrolling for large datasets
   - Debounce user inputs
   - Lazy load components

3. **API**:
   - Implement pagination
   - Use streaming responses for large data
   - Cache frequently accessed data

---

## Getting Started

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Redis (for Celery)
```bash
# Install Redis on macOS
brew install redis
brew services start redis
```

---

## API Design Principles

1. **RESTful conventions**: Use appropriate HTTP methods
2. **Versioning**: Prefix routes with `/api/v1/`
3. **Response format**: Consistent JSON structure
4. **Error handling**: Proper HTTP status codes and error messages
5. **Documentation**: Auto-generated with FastAPI/OpenAPI

Example endpoint:
```
POST /api/v1/data/upload
GET /api/v1/data/{id}
PUT /api/v1/data/{id}
DELETE /api/v1/data/{id}
GET /api/v1/data/{id}/filter
```

---

## Testing

### Backend Testing
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend Testing
```bash
cd frontend
npm run test
npm run test:ui
```

---

## Environment Variables

Backend `.env`:
```
APP_NAME="DataCrunch API"
DEBUG=True
API_VERSION=v1
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./datacrunch.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ALLOWED_ORIGINS=http://localhost:5173
```

---

## Key Features to Implement

1. **Data Upload**: CSV, Excel, Parquet support
2. **Data Grid**: Excel-like interface with editing
3. **Filtering**: Complex filter builder
4. **Aggregations**: Pivot tables, grouping
5. **Export**: Multiple format support
6. **Real-time Updates**: WebSocket for long operations
7. **Undo/Redo**: Operation history

---

## Git Workflow

1. Keep commits atomic and well-described
2. Branch naming: `feature/`, `bugfix/`, `hotfix/`
3. Always test before committing
4. Update documentation with code changes

---

## Common Commands

### Backend
```bash
# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker
celery -A app.celery_app worker --loglevel=info

# Run tests
pytest -v
```

### Frontend
```bash
# Dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run check
```

---

## Notes

- **Data files** in `/data` are gitignored - use for local testing
- **SQLite** is used by default; configure PostgreSQL for production
- **Redis** required for Celery background tasks
- **Polars** is preferred over Pandas for better performance
- **Svelte 5** uses new runes syntax - no `$:` reactive statements

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Polars Documentation](https://pola-rs.github.io/polars/)
- [Svelte 5 Documentation](https://svelte-5-preview.vercel.app/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [DuckDB](https://duckdb.org/docs/)

---

**Last Updated**: 2024
**Project Status**: In Development
