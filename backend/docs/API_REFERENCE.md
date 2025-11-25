# API Reference Documentation

## Overview

Complete API reference for the DataCrunch backend, including all endpoints, request/response formats, and error codes.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. Future versions will implement API key authentication.

## Common Response Formats

### Success Response
```json
{
  "provider": "gemini",
  "content": "Analysis result...",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 200,
    "total_tokens": 300
  },
  "model": "gemini-pro"
}
```

### Error Response
```json
{
  "error_type": "invalid_input",
  "message": "Human-readable error message",
  "provider": "gemini",
  "timestamp": "2024-01-15T10:30:00Z",
  "is_retryable": false,
  "details": {
    "field": "temperature",
    "value": 3.0
  }
}
```

## Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Invalid input, missing required fields, validation error |
| 401 | Unauthorized | Missing or invalid API key (future) |
| 429 | Too Many Requests | Rate limit or quota exceeded |
| 500 | Internal Server Error | Unexpected server error |

## Endpoints

### Health Check

#### `GET /`
Root endpoint for basic health check.

**Response:**
```json
{
  "message": "DataCrunch API",
  "version": "0.1.0",
  "status": "operational"
}
```

#### `GET /health`
Detailed health check for monitoring.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### AI Operations

#### `POST /api/v1/ai/process`

Process data using specified AI provider.

**Request Body:**
```json
{
  "provider": "gemini",
  "instruction_prompt": "Analyze this dataset",
  "input_data": {
    "sales": [100, 200, 150, 300],
    "dates": ["2024-01", "2024-02", "2024-03", "2024-04"]
  },
  "ai_config": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  },
  "model_name": "gemini-pro"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider` | string | Yes | AI provider: `gemini`, `openai`, `claude`, `deepseek`, `vertex_ai` |
| `instruction_prompt` | string | Yes | Instructions for the AI (min length: 1) |
| `input_data` | object | Yes | JSON data to process (can be nested) |
| `ai_config` | object | No | Model configuration (uses defaults if not provided) |
| `model_name` | string | No | Specific model override (e.g., "gpt-4", "claude-3") |

**AI Config Fields:**

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `temperature` | float | 0.7 | 0.0-2.0 | Sampling temperature (higher = more creative) |
| `max_tokens` | integer | 1000 | ≥1 | Maximum tokens to generate |
| `top_p` | float | 1.0 | 0.0-1.0 | Nucleus sampling parameter |
| `frequency_penalty` | float | 0.0 | -2.0 to 2.0 | Reduce repetition (OpenAI/DeepSeek) |
| `presence_penalty` | float | 0.0 | -2.0 to 2.0 | Encourage new topics (OpenAI/DeepSeek) |

**Success Response (200):**
```json
{
  "provider": "gemini",
  "content": "Based on the sales data provided:\n\n1. Total sales: 750\n2. Average: 187.5\n3. Trend: Increasing with slight dip in March",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 120,
    "total_tokens": 165
  },
  "model": "gemini-pro",
  "raw_response": null
}
```

**Error Responses:**

**400 Bad Request - Invalid Input:**
```json
{
  "error_type": "invalid_input",
  "message": "Temperature must be between 0.0 and 2.0",
  "provider": null,
  "timestamp": "2024-01-15T10:30:00Z",
  "is_retryable": false,
  "details": {
    "field": "temperature",
    "value": 3.0
  }
}
```

**401 Unauthorized - Missing API Key:**
```json
{
  "error_type": "missing_api_key",
  "message": "Gemini API key not configured",
  "provider": "gemini",
  "timestamp": "2024-01-15T10:30:00Z",
  "is_retryable": false,
  "details": {}
}
```

**429 Too Many Requests - Quota Exceeded:**
```json
{
  "error_type": "quota_exceeded",
  "message": "Provider gemini is currently blocked due to quota exceeded",
  "provider": "gemini",
  "timestamp": "2024-01-15T10:30:00Z",
  "is_retryable": false,
  "details": {
    "blocked_providers": {
      "gemini": "2024-01-15T11:30:00Z"
    }
  }
}
```

**500 Internal Server Error:**
```json
{
  "error_type": "processing_error",
  "message": "Unexpected error during AI processing",
  "provider": "gemini",
  "timestamp": "2024-01-15T10:30:00Z",
  "is_retryable": true,
  "details": {
    "original_error": "Connection timeout"
  }
}
```

---

#### `GET /api/v1/ai/providers`

Get list of supported AI providers.

**Response:**
```json
{
  "providers": [
    "gemini",
    "openai",
    "claude",
    "deepseek",
    "vertex_ai"
  ]
}
```

---

#### `GET /api/v1/ai/status`

Get status of all providers including quota blocks.

**Response:**
```json
{
  "providers": [
    "gemini",
    "openai",
    "claude",
    "deepseek",
    "vertex_ai"
  ],
  "blocked_providers": {
    "gemini": "2024-01-15T11:30:00Z"
  },
  "available_providers": [
    "openai",
    "claude",
    "deepseek",
    "vertex_ai"
  ]
}
```

---

#### `POST /api/v1/ai/unblock/{provider}`

Manually unblock a provider (admin operation).

**Path Parameters:**
- `provider` (string): Provider name to unblock

**Response:**
```json
{
  "message": "Provider gemini has been unblocked",
  "provider": "gemini"
}
```

---

#### `GET /api/v1/ai/prompt-templates`

Get available prompt templates.

**Response:**
```json
{
  "templates": {
    "data_analysis": "Analyze and summarize datasets",
    "data_cleaning": "Identify data quality issues",
    "data_transformation": "Transform data structure",
    "categorization": "Categorize items into groups",
    "sentiment_analysis": "Analyze text sentiment",
    "custom": "Use custom instructions"
  }
}
```

---

## Provider-Specific Details

### Google Gemini

**Models:**
- `gemini-pro` (default)
- `gemini-pro-vision`

**Configuration:**
```bash
GEMINI_API_KEY=your_key_here
```

**Rate Limits:** 60 requests/minute

---

### OpenAI

**Models:**
- `gpt-4-turbo-preview` (default)
- `gpt-4`
- `gpt-3.5-turbo`

**Configuration:**
```bash
OPENAI_API_KEY=your_key_here
```

**Rate Limits:** Varies by plan

---

### Anthropic Claude

**Models:**
- `claude-3-opus-20240229` (default)
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`

**Configuration:**
```bash
ANTHROPIC_API_KEY=your_key_here
```

**Rate Limits:** Varies by plan

---

### DeepSeek

**Models:**
- `deepseek-chat` (default)
- `deepseek-coder`

**Configuration:**
```bash
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

**Rate Limits:** 60 requests/minute (free tier)

---

### Google Vertex AI

**Models:**
- `gemini-pro` (default)
- `gemini-pro-vision`
- Other foundation models via Vertex AI

**Configuration:**
```bash
VERTEX_AI_PROJECT_ID=your-gcp-project-id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_CREDENTIALS_PATH=/path/to/service-account.json
```

**Authentication:**
- Service Account JSON file
- OR Application Default Credentials (ADC)

---

## Usage Examples

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/ai/process" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "instruction_prompt": "Analyze this sales data",
    "input_data": {
      "sales": [100, 200, 150, 300]
    }
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/ai/process",
    json={
        "provider": "openai",
        "instruction_prompt": "Summarize these customer reviews",
        "input_data": {
            "reviews": [
                "Great product!",
                "Not satisfied with quality",
                "Excellent service"
            ]
        },
        "ai_config": {
            "temperature": 0.5,
            "max_tokens": 500
        }
    }
)

print(response.json())
```

### JavaScript/TypeScript

```typescript
const response = await fetch('http://localhost:8000/api/v1/ai/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    provider: 'claude',
    instruction_prompt: 'Analyze sentiment of these comments',
    input_data: {
      comments: ['Love it!', 'Could be better', 'Amazing experience']
    }
  })
});

const result = await response.json();
console.log(result);
```

---

## Error Handling Best Practices

1. **Always check `is_retryable` flag** - If true, implement exponential backoff
2. **Monitor quota status** - Use `/api/v1/ai/status` to check blocked providers
3. **Handle 429 errors** - Switch to alternative provider or wait for unblock
4. **Log error details** - The `details` object contains debugging information
5. **Validate input** - Check constraints before sending to avoid 400 errors

---

## Rate Limiting Strategy

When quota is exceeded:
1. Provider is automatically blocked for 60 minutes (default)
2. All subsequent requests to that provider return 429
3. Use `/api/v1/ai/status` to check when unblock occurs
4. Admin can manually unblock via `/api/v1/ai/unblock/{provider}`

---

## SOLID Principles in API Design

The API follows SOLID principles:

- **SRP**: Each endpoint has single responsibility
- **OCP**: New providers added without changing endpoints
- **LSP**: All providers return same response format
- **ISP**: Minimal, focused endpoint interfaces
- **DIP**: API depends on abstractions, not implementations
