# DataCrunch

A high-performance data processing web application with an Excel-like user experience.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Documentation

📖 **Full project instructions and guidelines**: [`instructions/PROJECT_INSTRUCTIONS.md`](instructions/PROJECT_INSTRUCTIONS.md)

This file contains:
- Complete tech stack details
- Project structure
- Development guidelines
- Code style conventions
- Architecture patterns
- Setup instructions
- API design principles
- Common commands

## Tech Stack

**Backend**: FastAPI + Polars + DuckDB + Celery + Redis  
**Frontend**: Svelte 5 + TypeScript + Tailwind CSS + Vite

## Project Structure

```
data_web_app/
├── backend/          # FastAPI application
├── frontend/         # Svelte 5 application
├── data/            # Data files (gitignored)
├── docs/            # Additional documentation
└── instructions/    # Project guidelines
```

---

**Status**: In Development  
**Version**: 0.1.0
