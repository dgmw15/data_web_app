# Error Handling System Documentation

## Overview

The DataCrunch API implements a comprehensive error handling system that follows SOLID principles and provides:
- Structured error responses
- Quota tracking to prevent excessive API calls
- Automatic provider blocking when quota is exceeded
- Retryable vs non-retryable error classification
- Standardized error conversion across all AI providers

## Architecture

### 1. Error Types (`app/core/errors.py`)

All errors inherit from `AIServiceError`, which provides:
- Categorized error types (via `ErrorType` enum)
- Human-readable messages
- Structured details dictionary
- Provider identification
- Timestamp tracking
- Retryability flag

#### Error Categories

**Client Errors (4xx)**
- `INVALID_INPUT` - Invalid request parameters
- `MISSING_API_KEY` - API key not configured
- `INVALID_PROVIDER` - Unsupported AI provider
- `INVALID_CONFIG` - Invalid model configuration

**Server Errors (5xx)**
- `API_CONNECTION_ERROR` - Connection to AI provider failed
- `API_TIMEOUT` - Request timed out
- `ADAPTER_INITIALIZATION_ERROR` - Failed to initialize adapter
- `PROCESSING_ERROR` - General processing error

**Rate Limit Errors (429)**
- `QUOTA_EXCEEDED` - API quota exhausted (blocks provider)
- `RATE_LIMIT_EXCEEDED` - Rate limit hit (retryable)

**Response Errors**
- `INVALID_RESPONSE` - Malformed response from provider
- `EMPTY_RESPONSE` - Empty response received

### 2. Quota Tracker (`app/core/quota_tracker.py`)

Thread-safe singleton that:
- Tracks which providers are blocked
- Automatically unblocks after expiry time
- Prevents API calls to blocked providers
- Provides status information for monitoring

**Key Features:**
- Singleton pattern for global state
- Thread-safe with locks
- Time-based automatic unblocking
- Manual unblock capability for admins

### 3. Error Flow

```
Client Request
    ↓
API Route (HTTP layer)
    ↓
AIService (checks quota tracker)
    ↓
[Blocked?] → Yes → Raise QuotaExceededError (429)
    ↓ No
Adapter (validates input)
    ↓
AI Provider API
    ↓
[Error?] → Yes → Convert to AIServiceError
    ↓            → Block provider if quota error
    ↓
Return AIResponse
```

## Usage Examples

### 1. Handling Errors in Adapters

```python
async def call_ai(self, ...):
    quota_tracker = QuotaTracker()
    
    # Check if provider is blocked
    if quota_tracker.is_provider_blocked(self.PROVIDER_NAME):
        raise AIServiceError(
            error_type=ErrorType.QUOTA_EXCEEDED,
            message="Provider is blocked",
            provider=self.PROVIDER_NAME
        )
    
    try:
        # Validate input
        self._validate_config(model_config)
        
        # Make API call
        response = await api_call()
        
        return AIResponse(...)
        
    except InvalidInputError:
        raise  # Re-raise as-is
    except AIServiceError as e:
        # Block if quota exceeded
        if e.error_type == ErrorType.QUOTA_EXCEEDED:
            quota_tracker.block_provider(self.PROVIDER_NAME)
        raise
    except Exception as e:
        # Convert to standard error
        raise handle_provider_error(e, self.PROVIDER_NAME)
```

### 2. Client Error Responses

**Successful Response (200)**
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

**Input Error (400)**
```json
{
  "error_type": "invalid_input",
  "message": "Temperature must be between 0.0 and 2.0",
  "provider": "gemini",
  "timestamp": "2024-01-15T10:30:00Z",
  "is_retryable": false,
  "details": {}
}
```

**Quota Exceeded (429)**
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

### 3. Monitoring Provider Status

**GET /api/v1/ai/status**
```json
{
  "providers": ["gemini", "openai", "claude", "deepseek", "vertex_ai"],
  "blocked_providers": {
    "gemini": "2024-01-15T11:30:00Z"
  },
  "available_providers": ["openai", "claude", "deepseek", "vertex_ai"]
}
```

**POST /api/v1/ai/unblock/{provider}**
```json
{
  "message": "Provider gemini has been unblocked",
  "provider": "gemini"
}
```

## SOLID Principles Applied

### Single Responsibility Principle (SRP)
- `AIServiceError`: Only represents error state
- `QuotaTracker`: Only tracks quota status
- `handle_provider_error()`: Only converts errors
- Each error class has one specific purpose

### Open/Closed Principle (OCP)
- New error types can be added to `ErrorType` enum without modifying existing code
- Provider-specific error handling via `handle_provider_error()` function
- Quota tracker extensible without core changes

### Liskov Substitution Principle (LSP)
- All error subclasses (`QuotaExceededError`, `RateLimitError`, etc.) fully substitutable for `AIServiceError`
- All return same structured format via `to_dict()`
- Consistent exception hierarchy

### Interface Segregation Principle (ISP)
- Minimal `AIServiceError` interface with only essential fields
- Specialized errors add specific fields without bloating base class
- QuotaTracker has focused, minimal interface

### Dependency Inversion Principle (DIP)
- Adapters depend on `AIServiceError` abstraction, not concrete HTTP exceptions
- Service layer converts to HTTP exceptions at boundary
- Error handling independent of HTTP framework

## Testing

Run error handling tests:
```bash
cd backend
pytest tests/test_error_handling.py -v
```

Test coverage includes:
- Error creation and serialization
- Quota tracking and blocking
- Provider error conversion
- Service-level error handling
- Input validation

## Best Practices

1. **Always use structured errors**: Never raise raw exceptions from adapters
2. **Check quota before API calls**: Prevents wasted requests
3. **Convert provider errors**: Use `handle_provider_error()` for consistency
4. **Set is_retryable correctly**: Helps clients implement retry logic
5. **Include details**: Add context in `details` dict for debugging
6. **Log errors**: Use structured logging with error metadata
7. **Monitor blocked providers**: Set up alerts for quota issues

## Future Enhancements

- Persistent quota tracking (Redis/Database)
- Per-user rate limiting
- Automatic retry with exponential backoff
- Circuit breaker pattern
- Error rate monitoring and alerting
- Detailed usage analytics
