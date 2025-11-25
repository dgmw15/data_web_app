# DataCrunch
A high-performance data processing web application with an Excel-like user experience and AI-powered analysis.

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Add your AI API keys to .env file
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## AI Integration

This project includes a modular AI system supporting multiple providers:

### Supported AI Providers
- **Google Gemini** - Fast and efficient for data analysis
- **OpenAI GPT** - Powerful reasoning and complex tasks
- **Anthropic Claude** - Strong analytical capabilities
- **DeepSeek** - Cost-effective alternative
- **Google Vertex AI** - Enterprise-grade GCP integration with Gemini and foundation models

### API Endpoints

**Process AI Request**
```bash
POST /api/v1/ai/process
```

**Get Supported Providers**
```bash
GET /api/v1/ai/providers
```

**Get Prompt Templates**
```bash
GET /api/v1/ai/prompt-templates
```

### Example Usage

```python
import requests

request = {
    "provider": "vertex_ai",  # or "gemini", "openai", "claude", "deepseek"
    "instruction_prompt": "Analyze this dataset and provide insights",
    "input_data": {
        "sales": [100, 200, 150, 300],
        "dates": ["2024-01", "2024-02", "2024-03", "2024-04"]
    },
    "model_config": {
        "temperature": 0.7,
        "max_tokens": 1000
    }
}

response = requests.post("http://localhost:8000/api/v1/ai/process", json=request)
print(response.json())
```

## Environment Variables

Required environment variables for AI providers (add to `.env`):

```bash
# Google Gemini
GEMINI_API_KEY=your_gemini_key_here

# OpenAI
OPENAI_API_KEY=your_openai_key_here

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key_here

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Google Vertex AI (GCP)
VERTEX_AI_PROJECT_ID=your-gcp-project-id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_CREDENTIALS_PATH=/path/to/service-account.json
```

### Setting Up Vertex AI

1. **Create a GCP Project**: Go to [Google Cloud Console](https://console.cloud.google.com)
2. **Enable Vertex AI API**: Navigate to APIs & Services and enable Vertex AI API
3. **Create Service Account**: 
   - Go to IAM & Admin > Service Accounts
   - Create a new service account with "Vertex AI User" role
   - Download the JSON key file
4. **Set Environment Variables**: Add the project ID, location, and path to credentials in `.env`

Alternatively, use Application Default Credentials (ADC):
```bash
gcloud auth application-default login
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
**AI**: Google Gemini, OpenAI, Anthropic Claude, DeepSeek, Google Vertex AI

## Project Structure

```
data_web_app/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # API endpoints
│   │   ├── services/         # Business logic
│   │   │   └── ai_adapters/  # AI provider adapters
│   │   ├── schemas/          # Pydantic models
│   │   └── core/            # Configuration
│   ├── tests/               # Unit tests
│   └── requirements.txt     # Python dependencies
├── frontend/                # Svelte 5 application
├── data/                   # Data files (gitignored)
├── docs/                   # Additional documentation
└── instructions/           # Project guidelines
```

## Testing

Run backend tests:
```bash
cd backend
pytest tests/ -v
```

---

**Status**: In Development  
**Version**: 0.1.0
