# Model Registry Documentation

## Overview

The Model Registry is a centralized system that tracks all available AI models across providers, including their context windows, output limits, capabilities, and pricing. This enables intelligent token management, cost estimation, and prevents context window errors.

---

## Why Model Registry?

**Problem it solves:**
- Prevents hitting context window limits
- Enables cost-aware model selection
- Provides token validation before API calls
- Tracks model capabilities for task matching
- Centralizes model specifications for easy updates

---

## Architecture

### Components

1. **ModelSpec** - Data class for model specifications
2. **ModelCapability** - Enum of model capabilities
3. **MODEL_REGISTRY** - Master dictionary of all models
4. **Helper Functions** - Utility functions for model operations

### SOLID Principles Applied

- **SRP**: Each function has single responsibility (validate, estimate, filter)
- **OCP**: New models added without changing code
- **LSP**: All models follow same specification structure
- **ISP**: Minimal, focused interfaces for each operation
- **DIP**: Depends on ModelSpec abstraction

---

## Model Specifications

### Tracked Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `model_id` | str | Unique identifier (e.g., "gpt-4-turbo-preview") |
| `provider` | str | Provider name (gemini, openai, claude, etc.) |
| `display_name` | str | Human-readable name |
| `context_window` | int | Maximum total tokens (input + output) |
| `max_output_tokens` | int | Maximum tokens in response |
| `supports_system_message` | bool | Whether system messages supported |
| `capabilities` | List[ModelCapability] | Model capabilities |
| `cost_per_1k_input` | float | Cost per 1K input tokens (USD) |
| `cost_per_1k_output` | float | Cost per 1K output tokens (USD) |
| `recommended_for` | List[str] | Use cases model excels at |
| `notes` | str | Additional limitations or features |

---

## Available Models

### Google Gemini (4 models)

| Model | Context | Output | Cost/1K (in/out) | Best For |
|-------|---------|--------|------------------|----------|
| **gemini-pro** | 32K | 8K | $0.00025 / $0.0005 | General analysis, free tier |
| **gemini-pro-vision** | 16K | 8K | $0.00025 / $0.0005 | Image/chart analysis |
| **gemini-1.5-pro** | 1M | 8K | $0.0035 / $0.0105 | Large documents, complex reasoning |
| **gemini-1.5-flash** | 1M | 8K | $0.00035 / $0.00053 | High-volume, cost-sensitive |

### OpenAI (4 models)

| Model | Context | Output | Cost/1K (in/out) | Best For |
|-------|---------|--------|------------------|----------|
| **gpt-4-turbo-preview** | 128K | 4K | $0.01 / $0.03 | Complex reasoning, long docs |
| **gpt-4** | 8K | 4K | $0.03 / $0.06 | High-quality outputs |
| **gpt-4-vision-preview** | 128K | 4K | $0.01 / $0.03 | Image analysis |
| **gpt-3.5-turbo** | 16K | 4K | $0.0005 / $0.0015 | Simple tasks, high volume |

### Anthropic Claude (3 models)

| Model | Context | Output | Cost/1K (in/out) | Best For |
|-------|---------|--------|------------------|----------|
| **claude-3-opus** | 200K | 4K | $0.015 / $0.075 | Complex analysis, research |
| **claude-3-sonnet** | 200K | 4K | $0.003 / $0.015 | Balanced performance/cost |
| **claude-3-haiku** | 200K | 4K | $0.00025 / $0.00125 | Fast, cost-effective |

### DeepSeek (2 models)

| Model | Context | Output | Cost/1K (in/out) | Best For |
|-------|---------|--------|------------------|----------|
| **deepseek-chat** | 32K | 4K | $0.00014 / $0.00028 | Budget processing |
| **deepseek-coder** | 32K | 4K | $0.00014 / $0.00028 | Code generation |

### Vertex AI (4 models)

Same as Gemini models but with `vertex-` prefix for GCP integration.

**Total: 17 models across 5 providers**

---

## API Endpoints

### Get All Models

```bash
GET /api/v1/ai/models
```

**Response:**
```json
{
  "gemini": {
    "model_count": 4,
    "models": ["gemini-pro", "gemini-pro-vision", ...],
    "min_context": 16384,
    "max_context": 1048576,
    "avg_cost_per_1k_input": 0.00105
  },
  "openai": { ... },
  ...
}
```

---

### Get Models by Provider

```bash
GET /api/v1/ai/models/{provider}
```

**Example:**
```bash
GET /api/v1/ai/models/openai
```

**Response:**
```json
{
  "provider": "openai",
  "models": [
    {
      "model_id": "gpt-4-turbo-preview",
      "display_name": "GPT-4 Turbo Preview",
      "context_window": 128000,
      "max_output_tokens": 4096,
      "capabilities": ["text_generation", "code_generation", "function_calling", "json_mode"],
      "cost_per_1k_input": 0.01,
      "cost_per_1k_output": 0.03,
      "recommended_for": ["Complex reasoning", "Code generation", "Long document analysis"],
      "notes": "Latest GPT-4 with 128K context. Best overall reasoning capabilities."
    },
    ...
  ]
}
```

---

### Get Model Specification

```bash
GET /api/v1/ai/models/spec/{model_id}
```

**Example:**
```bash
GET /api/v1/ai/models/spec/gemini-1.5-pro
```

**Response:**
```json
{
  "model_id": "gemini-1.5-pro",
  "provider": "gemini",
  "display_name": "Gemini 1.5 Pro",
  "context_window": 1048576,
  "max_output_tokens": 8192,
  "supports_system_message": true,
  "capabilities": ["text_generation", "code_generation", "vision", "function_calling"],
  "cost_per_1k_input": 0.0035,
  "cost_per_1k_output": 0.0105,
  "recommended_for": ["Large document analysis", "Long conversation context"],
  "notes": "Extremely large context window. Higher cost but handles massive inputs."
}
```

---

### Validate Token Counts

```bash
POST /api/v1/ai/models/validate-tokens
```

**Request Body:**
```json
{
  "model_id": "gpt-4",
  "input_tokens": 7000,
  "requested_output_tokens": 2000
}
```

**Response (Invalid):**
```json
{
  "is_valid": false,
  "message": "Total tokens (9000) exceeds context window (8192) for GPT-4. Try reducing input or output token limit.",
  "model_id": "gpt-4",
  "input_tokens": 7000,
  "requested_output_tokens": 2000,
  "total_tokens": 9000
}
```

**Response (Valid):**
```json
{
  "is_valid": true,
  "message": "Token counts are valid",
  "model_id": "gemini-1.5-pro",
  "input_tokens": 50000,
  "requested_output_tokens": 2000,
  "total_tokens": 52000
}
```

---

### Estimate Cost

```bash
POST /api/v1/ai/models/estimate-cost
```

**Request Body:**
```json
{
  "model_id": "gpt-4-turbo-preview",
  "input_tokens": 1000,
  "output_tokens": 500
}
```

**Response:**
```json
{
  "model_id": "gpt-4-turbo-preview",
  "model_name": "GPT-4 Turbo Preview",
  "input_tokens": 1000,
  "output_tokens": 500,
  "total_tokens": 1500,
  "cost_breakdown": {
    "input_cost_usd": 0.01,
    "output_cost_usd": 0.015,
    "total_cost_usd": 0.025
  },
  "rate_per_1k": {
    "input": 0.01,
    "output": 0.03
  }
}
```

---

### Get Models by Capability

```bash
GET /api/v1/ai/models/by-capability/{capability}
```

**Available Capabilities:**
- `text_generation`
- `code_generation`
- `vision`
- `function_calling`
- `json_mode`
- `streaming`

**Example:**
```bash
GET /api/v1/ai/models/by-capability/vision
```

**Response:**
```json
{
  "capability": "vision",
  "model_count": 6,
  "models": [
    {
      "model_id": "gemini-pro-vision",
      "provider": "gemini",
      "display_name": "Gemini Pro Vision",
      "context_window": 16384,
      "cost_per_1k_input": 0.00025
    },
    {
      "model_id": "gpt-4-vision-preview",
      "provider": "openai",
      "display_name": "GPT-4 Vision",
      "context_window": 128000,
      "cost_per_1k_input": 0.01
    },
    ...
  ]
}
```

---

## Python Usage Examples

### Basic Model Lookup

```python
from app.core.model_registry import get_model_spec

spec = get_model_spec("gemini-pro")
print(f"Context window: {spec.context_window}")
print(f"Max output: {spec.max_output_tokens}")
print(f"Cost per 1K input: ${spec.cost_per_1k_input}")
```

### Token Validation

```python
from app.core.model_registry import validate_token_count

is_valid, message = validate_token_count(
    model_id="gpt-4",
    input_tokens=7000,
    requested_output_tokens=2000
)

if not is_valid:
    print(f"Error: {message}")
    # Switch to larger model
    is_valid, message = validate_token_count(
        model_id="gpt-4-turbo-preview",
        input_tokens=7000,
        requested_output_tokens=2000
    )
```

### Cost Estimation

```python
from app.core.model_registry import estimate_cost, get_models_by_provider

# Compare costs across providers
models = ["gemini-pro", "gpt-3.5-turbo", "claude-3-haiku"]

for model_id in models:
    cost = estimate_cost(model_id, input_tokens=10000, output_tokens=1000)
    print(f"{model_id}: ${cost:.4f}")

# Output:
# gemini-pro: $0.0030
# gpt-3.5-turbo: $0.0065
# claude-3-haiku: $0.0038
```

### Find Cheapest Model for Task

```python
from app.core.model_registry import get_models_by_capability, ModelCapability

# Find cheapest code generation model
code_models = get_models_by_capability(ModelCapability.CODE_GENERATION)
cheapest = min(code_models, key=lambda m: m.cost_per_1k_input)

print(f"Cheapest code model: {cheapest.display_name}")
print(f"Cost: ${cheapest.cost_per_1k_input} per 1K tokens")
```

### Get Provider Summary

```python
from app.core.model_registry import get_model_summary

summary = get_model_summary()

for provider, data in summary.items():
    print(f"\n{provider.upper()}")
    print(f"  Models: {data['model_count']}")
    print(f"  Context range: {data['min_context']:,} - {data['max_context']:,}")
    print(f"  Avg cost/1K: ${data['avg_cost_per_1k_input']:.5f}")
```

---

## Integration with AI Service

The model registry is integrated into the AI service for automatic validation:

```python
# In AIService.process_ai_request()
# Before making API call:

spec = get_model_spec(model_name, provider)
if not spec:
    raise AIServiceError("Unknown model", ErrorType.INVALID_INPUT)

# Validate token counts
is_valid, error_msg = validate_token_count(
    model_name,
    input_token_count,
    config.max_tokens
)

if not is_valid:
    raise AIServiceError(error_msg, ErrorType.INVALID_INPUT)
```

---

## Future Enhancements

### Planned Features

1. **Dynamic Token Counting**
   - Integrate tiktoken for accurate token estimation
   - Pre-validate before API calls

2. **Auto-Fallback Strategy**
   - If model exceeds context, suggest alternatives
   - Automatic model switching on token limits

3. **Cost Tracking**
   - Track actual usage per model
   - Budget alerts and limits
   - Monthly cost reports

4. **Model Performance Metrics**
   - Track response times
   - Error rates by model
   - Success rates

5. **Smart Model Selection**
   - AI-powered model recommendation
   - Based on task type, budget, speed needs
   - Historical performance data

---

## Troubleshooting

### Model Not Found

**Problem:** `get_model_spec()` returns `None`

**Solutions:**
1. Check model ID spelling
2. Use provider-specific lookup: `get_model_spec(model_id, provider="openai")`
3. List available models: `get_models_by_provider("openai")`

### Token Validation Fails

**Problem:** Valid input still fails validation

**Solutions:**
1. Check if using correct model ID
2. Verify input_tokens + output_tokens < context_window
3. Some models have asymmetric limits (check max_output_tokens separately)

### Cost Estimation Shows $0.00

**Problem:** `estimate_cost()` returns zero

**Solutions:**
1. Verify model exists in registry
2. Check if pricing data is loaded for that model
3. Some free tier models may have $0 cost

---

## Adding New Models

### Step 1: Add to Provider Dictionary

```python
OPENAI_MODELS = {
    "gpt-5": ModelSpec(
        model_id="gpt-5",
        provider="openai",
        display_name="GPT-5",
        context_window=1_000_000,
        max_output_tokens=16_384,
        capabilities=[ModelCapability.TEXT_GENERATION, ...],
        cost_per_1k_input=0.05,
        cost_per_1k_output=0.15,
        recommended_for=["Everything"],
        notes="Next generation model"
    ),
}
```

### Step 2: Registry Auto-Updates

The model is automatically included in `MODEL_REGISTRY` via dictionary unpacking.

### Step 3: Update Default if Needed

```python
def get_default_model(provider: str) -> Optional[str]:
    defaults = {
        "openai": "gpt-5",  # Update to new default
        ...
    }
```

That's it! No other code changes needed (OCP principle).

---

## Summary

The Model Registry provides:

✅ **17 models** across 5 providers  
✅ **Token validation** prevents context errors  
✅ **Cost estimation** for budget management  
✅ **Capability filtering** for task matching  
✅ **API endpoints** for frontend integration  
✅ **Easy extensibility** following SOLID principles

**Next Steps:**
1. Integrate token counting library (tiktoken)
2. Add automatic fallback on context limits
3. Implement usage tracking and analytics
