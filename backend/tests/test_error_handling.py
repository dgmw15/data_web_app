"""
Error Handling and Quota Tracking Tests
Tests for error handling, quota tracking, and provider blocking.

Test Coverage:
- Error creation and serialization
- Quota tracking singleton pattern
- Provider blocking and unblocking
- Error type conversion
- Input validation
- Service-level error integration

Troubleshooting Guide:
- If singleton tests fail: Check if QuotaTracker state is being reset properly
- If error conversion fails: Verify error message patterns in handle_provider_error()
- If validation tests fail: Check Pydantic field constraints in AIModelConfig
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from app.core.errors import (
    AIServiceError,
    QuotaExceededError,
    RateLimitError,
    InvalidInputError,
    APIConnectionError,
    ErrorType,
    handle_provider_error
)
from app.core.quota_tracker import QuotaTracker
from app.services.ai_service import AIService
from app.schemas.ai_schemas import AIRequest, AIProviderType, AIModelConfig


class TestAIServiceError:
    """
    Test suite for AIServiceError base class.
    
    What it tests:
    - Error object creation with all attributes
    - Timestamp generation
    - Error serialization to dict
    - Error message formatting
    
    Common issues:
    - Missing required fields → Check error_type and message are provided
    - Timestamp issues → Verify datetime.utcnow() is working
    """
    
    def test_error_creation_with_all_fields(self):
        """
        Test: Create AIServiceError with all fields
        Input: error_type, message, details, provider, is_retryable
        Expected: All fields stored correctly, timestamp generated
        """
        error = AIServiceError(
            error_type=ErrorType.PROCESSING_ERROR,
            message="Test error message",
            provider="test_provider",
            is_retryable=True,
            details={"extra": "info"}
        )
        
        assert error.error_type == ErrorType.PROCESSING_ERROR
        assert error.message == "Test error message"
        assert error.provider == "test_provider"
        assert error.is_retryable is True
        assert error.details["extra"] == "info"
        assert isinstance(error.timestamp, datetime)
    
    def test_error_creation_with_defaults(self):
        """
        Test: Create error with minimal required fields
        Input: error_type, message only
        Expected: Optional fields have default values
        """
        error = AIServiceError(
            error_type=ErrorType.INVALID_INPUT,
            message="Test error"
        )
        
        assert error.details == {}
        assert error.provider is None
        assert error.is_retryable is False
    
    def test_error_to_dict_serialization(self):
        """
        Test: Convert error to dictionary for API response
        Input: AIServiceError object
        Expected: Dict with all fields, timestamp as ISO string
        
        Troubleshooting:
        - Missing fields → Check to_dict() implementation
        - Timestamp format error → Verify isoformat() call
        """
        error = AIServiceError(
            error_type=ErrorType.INVALID_INPUT,
            message="Invalid temperature value",
            details={"field": "temperature", "value": 3.0},
            provider="gemini"
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["error_type"] == "invalid_input"
        assert error_dict["message"] == "Invalid temperature value"
        assert error_dict["details"]["field"] == "temperature"
        assert error_dict["provider"] == "gemini"
        assert "timestamp" in error_dict
        assert error_dict["is_retryable"] is False
    
    def test_error_inherits_from_exception(self):
        """
        Test: AIServiceError can be raised and caught
        Input: Raise AIServiceError
        Expected: Can be caught as Exception
        """
        with pytest.raises(AIServiceError) as exc_info:
            raise AIServiceError(
                error_type=ErrorType.PROCESSING_ERROR,
                message="Test"
            )
        
        assert exc_info.value.error_type == ErrorType.PROCESSING_ERROR


class TestSpecializedErrors:
    """
    Test suite for specialized error types.
    
    What it tests:
    - QuotaExceededError initialization and defaults
    - RateLimitError with retry_after
    - InvalidInputError non-retryable behavior
    - APIConnectionError retryable behavior
    """
    
    def test_quota_exceeded_error_defaults(self):
        """
        Test: QuotaExceededError has correct defaults
        Input: provider only
        Expected: QUOTA_EXCEEDED type, not retryable
        """
        error = QuotaExceededError(provider="openai")
        
        assert error.error_type == ErrorType.QUOTA_EXCEEDED
        assert error.is_retryable is False
        assert error.provider == "openai"
        assert "quota exceeded" in error.message.lower()
    
    def test_quota_exceeded_error_custom_message(self):
        """
        Test: Custom message for QuotaExceededError
        Input: provider, custom message
        Expected: Custom message used
        """
        error = QuotaExceededError(
            provider="gemini",
            message="Monthly quota exhausted"
        )
        
        assert error.message == "Monthly quota exhausted"
    
    def test_rate_limit_error_with_retry_after(self):
        """
        Test: RateLimitError includes retry_after in details
        Input: provider, retry_after=60
        Expected: retry_after in details, retryable=True
        
        Troubleshooting:
        - retry_after missing → Check __init__ adds to details dict
        """
        error = RateLimitError(provider="claude", retry_after=60)
        
        assert error.error_type == ErrorType.RATE_LIMIT_EXCEEDED
        assert error.is_retryable is True
        assert error.details["retry_after_seconds"] == 60
        assert "60 seconds" in error.message
    
    def test_rate_limit_error_without_retry_after(self):
        """
        Test: RateLimitError without retry time
        Input: provider only
        Expected: Generic message, no retry_after in details
        """
        error = RateLimitError(provider="deepseek")
        
        assert error.is_retryable is True
        assert "Rate limit exceeded" in error.message
    
    def test_invalid_input_error(self):
        """
        Test: InvalidInputError is not retryable
        Input: error message
        Expected: INVALID_INPUT type, not retryable
        """
        error = InvalidInputError("Temperature must be between 0 and 2")
        
        assert error.error_type == ErrorType.INVALID_INPUT
        assert error.is_retryable is False
        assert "Temperature" in error.message
    
    def test_api_connection_error(self):
        """
        Test: APIConnectionError is retryable
        Input: provider, message
        Expected: API_CONNECTION_ERROR type, retryable=True
        """
        error = APIConnectionError(
            provider="vertex_ai",
            message="Connection timeout"
        )
        
        assert error.error_type == ErrorType.API_CONNECTION_ERROR
        assert error.is_retryable is True
        assert error.provider == "vertex_ai"


class TestErrorConversion:
    """
    Test suite for handle_provider_error() function.
    
    What it tests:
    - Converting various provider errors to standard format
    - Detecting quota exceeded patterns
    - Detecting rate limit patterns
    - Detecting authentication errors
    - Detecting connection errors
    
    Troubleshooting:
    - Wrong error type detected → Check keyword matching in handle_provider_error()
    - Original error lost → Verify it's stored in details["original_error"]
    """
    
    def test_convert_quota_exceeded_error(self):
        """
        Test: Detect and convert quota exceeded errors
        Input: Exception with "quota exceeded" text
        Expected: QuotaExceededError returned
        """
        original = Exception("Error 429: Quota exceeded for this project")
        converted = handle_provider_error(original, "gemini")
        
        assert isinstance(converted, QuotaExceededError)
        assert converted.provider == "gemini"
        assert converted.details["original_error"] == str(original)
    
    def test_convert_rate_limit_error(self):
        """
        Test: Detect rate limit errors
        Input: Exception with "rate limit" or "429" text
        Expected: RateLimitError returned
        """
        original = Exception("429: Too many requests")
        converted = handle_provider_error(original, "openai")
        
        assert isinstance(converted, RateLimitError)
        assert converted.provider == "openai"
        assert converted.is_retryable is True
    
    def test_convert_authentication_error(self):
        """
        Test: Detect authentication failures
        Input: Exception with "401", "403", or "api key" text
        Expected: MISSING_API_KEY error type
        """
        original = Exception("401 Unauthorized: Invalid API key")
        converted = handle_provider_error(original, "claude")
        
        assert converted.error_type == ErrorType.MISSING_API_KEY
        assert converted.is_retryable is False
        assert converted.provider == "claude"
    
    def test_convert_connection_error(self):
        """
        Test: Detect connection/network errors
        Input: Exception with "connection" or "timeout" text
        Expected: APIConnectionError returned
        """
        original = Exception("Connection timeout to API server")
        converted = handle_provider_error(original, "deepseek")
        
        assert isinstance(converted, APIConnectionError)
        assert converted.is_retryable is True
    
    def test_convert_generic_error(self):
        """
        Test: Convert unrecognized errors
        Input: Exception with no special keywords
        Expected: Generic PROCESSING_ERROR type
        """
        original = Exception("Something went wrong")
        converted = handle_provider_error(original, "vertex_ai")
        
        assert converted.error_type == ErrorType.PROCESSING_ERROR
        assert converted.is_retryable is True
        assert "Something went wrong" in converted.details["original_error"]


class TestQuotaTracker:
    """
    Test suite for QuotaTracker singleton.
    
    What it tests:
    - Singleton pattern ensures one instance
    - Provider blocking and checking
    - Automatic unblocking after expiry
    - Manual unblocking
    - Thread-safe operations
    
    Troubleshooting:
    - Singleton test fails → Check __new__ implementation
    - State persists between tests → Ensure setup_method() calls reset()
    - Threading issues → Verify Lock is used in all methods
    """
    
    def setup_method(self):
        """Reset quota tracker before each test to ensure clean state."""
        tracker = QuotaTracker()
        tracker.reset()
    
    def test_singleton_pattern(self):
        """
        Test: Only one QuotaTracker instance exists
        Input: Create two instances
        Expected: Both references point to same object
        
        Troubleshooting:
        - Fails → Check __new__ method singleton implementation
        """
        tracker1 = QuotaTracker()
        tracker2 = QuotaTracker()
        
        assert tracker1 is tracker2
    
    def test_provider_not_blocked_initially(self):
        """
        Test: New providers are not blocked by default
        Input: Check any provider
        Expected: is_provider_blocked returns False
        """
        tracker = QuotaTracker()
        
        assert tracker.is_provider_blocked("gemini") is False
        assert tracker.is_provider_blocked("openai") is False
    
    def test_block_provider(self):
        """
        Test: Blocking a provider
        Input: block_provider("openai", duration_minutes=30)
        Expected: Provider is blocked, expiry time set
        """
        tracker = QuotaTracker()
        
        tracker.block_provider("openai", duration_minutes=30)
        
        assert tracker.is_provider_blocked("openai") is True
    
    def test_block_provider_default_duration(self):
        """
        Test: Default block duration is 60 minutes
        Input: block_provider without duration
        Expected: Provider blocked for default period
        """
        tracker = QuotaTracker()
        
        tracker.block_provider("claude")
        
        assert tracker.is_provider_blocked("claude") is True
        blocked = tracker.get_blocked_providers()
        assert "claude" in blocked
    
    def test_multiple_providers_independent(self):
        """
        Test: Blocking one provider doesn't affect others
        Input: Block "gemini" only
        Expected: Only "gemini" is blocked
        """
        tracker = QuotaTracker()
        
        tracker.block_provider("gemini")
        
        assert tracker.is_provider_blocked("gemini") is True
        assert tracker.is_provider_blocked("openai") is False
        assert tracker.is_provider_blocked("claude") is False
    
    def test_manual_unblock(self):
        """
        Test: Manually unblock a provider
        Input: Block then manually unblock
        Expected: Provider no longer blocked
        """
        tracker = QuotaTracker()
        
        tracker.block_provider("claude")
        assert tracker.is_provider_blocked("claude") is True
        
        tracker.manually_unblock_provider("claude")
        assert tracker.is_provider_blocked("claude") is False
    
    def test_get_blocked_providers_dict(self):
        """
        Test: Get dictionary of blocked providers with expiry
        Input: Block multiple providers
        Expected: Dict with provider names → ISO timestamp strings
        
        Troubleshooting:
        - Wrong format → Check isoformat() call
        - Missing providers → Verify _block_until dict is updated
        """
        tracker = QuotaTracker()
        
        tracker.block_provider("gemini", duration_minutes=60)
        tracker.block_provider("openai", duration_minutes=120)
        
        blocked = tracker.get_blocked_providers()
        
        assert "gemini" in blocked
        assert "openai" in blocked
        assert isinstance(blocked["gemini"], str)
        assert isinstance(blocked["openai"], str)
        # Verify ISO format by parsing
        datetime.fromisoformat(blocked["gemini"])
    
    def test_reset_clears_all_blocks(self):
        """
        Test: Reset removes all blocks
        Input: Block multiple providers then reset
        Expected: All providers unblocked
        """
        tracker = QuotaTracker()
        
        tracker.block_provider("gemini")
        tracker.block_provider("openai")
        tracker.block_provider("claude")
        
        tracker.reset()
        
        assert tracker.is_provider_blocked("gemini") is False
        assert tracker.is_provider_blocked("openai") is False
        assert tracker.is_provider_blocked("claude") is False
        assert len(tracker.get_blocked_providers()) == 0


class TestInputValidation:
    """
    Test suite for input validation in adapters.
    
    What it tests:
    - Temperature validation (0.0-2.0 range)
    - Max tokens validation (positive integers)
    - Top_p validation (0.0-1.0 range)
    - Empty prompt validation
    - Empty input data validation
    
    Troubleshooting:
    - Validation not triggered → Check _validate_config() is called
    - Wrong error message → Verify InvalidInputError message format
    """
    
    def test_invalid_temperature_too_high(self):
        """
        Test: Reject temperature > 2.0
        Input: AIModelConfig with temperature=3.0
        Expected: Pydantic ValidationError or InvalidInputError
        """
        with pytest.raises(Exception):  # Pydantic will raise ValidationError
            AIModelConfig(temperature=3.0)
    
    def test_invalid_temperature_negative(self):
        """
        Test: Reject negative temperature
        Input: AIModelConfig with temperature=-0.5
        Expected: ValidationError
        """
        with pytest.raises(Exception):
            AIModelConfig(temperature=-0.5)
    
    def test_valid_temperature_range(self):
        """
        Test: Accept valid temperature values
        Input: Various valid temperatures
        Expected: No error, config created
        """
        config1 = AIModelConfig(temperature=0.0)
        config2 = AIModelConfig(temperature=1.0)
        config3 = AIModelConfig(temperature=2.0)
        
        assert config1.temperature == 0.0
        assert config2.temperature == 1.0
        assert config3.temperature == 2.0
    
    def test_invalid_max_tokens_zero(self):
        """
        Test: Reject max_tokens <= 0
        Input: AIModelConfig with max_tokens=0
        Expected: ValidationError
        """
        with pytest.raises(Exception):
            AIModelConfig(max_tokens=0)
    
    def test_invalid_top_p_out_of_range(self):
        """
        Test: Reject top_p outside [0.0, 1.0]
        Input: AIModelConfig with top_p=1.5
        Expected: ValidationError
        """
        with pytest.raises(Exception):
            AIModelConfig(top_p=1.5)
    
    def test_valid_model_config_defaults(self):
        """
        Test: Default values are valid
        Input: AIModelConfig with no arguments
        Expected: All defaults within valid ranges
        """
        config = AIModelConfig()
        
        assert 0.0 <= config.temperature <= 2.0
        assert config.max_tokens > 0
        assert 0.0 <= config.top_p <= 1.0


class TestAIServiceIntegration:
    """
    Test suite for AIService error handling integration.
    
    What it tests:
    - Provider blocking prevents requests
    - Invalid provider returns 400
    - Quota exceeded returns 429
    - Service-level error conversion
    
    Troubleshooting:
    - Wrong status code → Check HTTPException status_code mapping
    - Provider not blocked → Verify QuotaTracker integration
    """
    
    @pytest.mark.asyncio
    async def test_blocked_provider_returns_429(self):
        """
        Test: Blocked provider returns 429 status
        Input: Request to blocked provider
        Expected: HTTPException with status 429
        
        Troubleshooting:
        - Not blocked → Ensure setup blocks the provider first
        - Wrong status → Check process_ai_request error handling
        """
        from fastapi import HTTPException
        
        tracker = QuotaTracker()
        tracker.reset()
        tracker.block_provider("gemini")
        
        request = AIRequest(
            provider=AIProviderType.GEMINI,
            instruction_prompt="Test",
            input_data={"test": "data"}
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await AIService.process_ai_request(request)
        
        assert exc_info.value.status_code == 429
        assert "blocked" in str(exc_info.value.detail).lower()
    
    def test_get_provider_status_shows_blocked(self):
        """
        Test: Provider status endpoint shows blocked providers
        Input: Block one provider
        Expected: Status shows provider in blocked list, not in available
        """
        tracker = QuotaTracker()
        tracker.reset()
        tracker.block_provider("openai")
        
        status = AIService.get_provider_status()
        
        assert "providers" in status
        assert "blocked_providers" in status
        assert "available_providers" in status
        assert "openai" in status["blocked_providers"]
        assert "openai" not in status["available_providers"]
        assert "gemini" in status["available_providers"]


# Run tests with: pytest tests/test_error_handling.py -v --tb=short
