"""
Error Handling Module
Centralized error handling for AI operations.

SOLID Principles Applied:
    - SRP: Only handles error definitions and formatting
    - OCP: New error types can be added without modifying existing code
    - ISP: Minimal, focused error classes
"""
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorType(str, Enum):
    """
    Categorized error types for AI operations.
    
    SOLID Principle Applied:
        - OCP: New error types can be added without breaking existing code
    """
    # Client Errors (4xx)
    INVALID_INPUT = "invalid_input"
    MISSING_API_KEY = "missing_api_key"
    INVALID_PROVIDER = "invalid_provider"
    INVALID_CONFIG = "invalid_config"
    
    # Server Errors (5xx)
    API_CONNECTION_ERROR = "api_connection_error"
    API_TIMEOUT = "api_timeout"
    ADAPTER_INITIALIZATION_ERROR = "adapter_initialization_error"
    PROCESSING_ERROR = "processing_error"
    
    # Rate Limit Errors
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # Response Errors
    INVALID_RESPONSE = "invalid_response"
    EMPTY_RESPONSE = "empty_response"


class AIServiceError(Exception):
    """
    Base exception for all AI service errors.
    
    Provides structured error information for logging and client responses.
    
    Attributes:
        error_type (ErrorType): Categorized error type
        message (str): Human-readable error message
        details (Dict): Additional error context
        provider (str): AI provider that caused the error
        timestamp (datetime): When the error occurred
        is_retryable (bool): Whether the operation can be retried
    
    SOLID Principle Applied:
        - SRP: Only represents error state and metadata
        - LSP: Can be used anywhere Exception is expected
    """
    
    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        is_retryable: bool = False
    ):
        """
        Initialize AI service error.
        
        Args:
            error_type: Categorized error type
            message: Human-readable error message
            details: Additional error context
            provider: AI provider that caused the error
            is_retryable: Whether the operation can be retried
        
        SOLID Principle Applied:
            - SRP: Only initializes error state
        """
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.provider = provider
        self.timestamp = datetime.utcnow()
        self.is_retryable = is_retryable
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary for API responses.
        
        Returns:
            Dict containing error information
        
        SOLID Principle Applied:
            - SRP: Only formats error data
        """
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "details": self.details,
            "provider": self.provider,
            "timestamp": self.timestamp.isoformat(),
            "is_retryable": self.is_retryable
        }


class QuotaExceededError(AIServiceError):
    """
    Raised when API quota is exceeded.
    
    This is a non-retryable error that should stop all pending requests.
    
    SOLID Principle Applied:
        - LSP: Fully substitutable for AIServiceError
        - SRP: Only represents quota exceeded state
    """
    
    def __init__(self, provider: str, message: str = "API quota exceeded", **kwargs):
        super().__init__(
            error_type=ErrorType.QUOTA_EXCEEDED,
            message=message,
            provider=provider,
            is_retryable=False,
            **kwargs
        )


class RateLimitError(AIServiceError):
    """
    Raised when rate limit is hit.
    
    This is a retryable error after waiting.
    
    SOLID Principle Applied:
        - LSP: Fully substitutable for AIServiceError
        - SRP: Only represents rate limit state
    """
    
    def __init__(self, provider: str, retry_after: Optional[int] = None, **kwargs):
        details = kwargs.get("details", {})
        details["retry_after_seconds"] = retry_after
        
        super().__init__(
            error_type=ErrorType.RATE_LIMIT_EXCEEDED,
            message=f"Rate limit exceeded. Retry after {retry_after} seconds" if retry_after else "Rate limit exceeded",
            provider=provider,
            is_retryable=True,
            details=details,
            **kwargs
        )


class InvalidInputError(AIServiceError):
    """
    Raised when input validation fails.
    
    This is a non-retryable error that requires client correction.
    
    SOLID Principle Applied:
        - LSP: Fully substitutable for AIServiceError
        - SRP: Only represents invalid input state
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            error_type=ErrorType.INVALID_INPUT,
            message=message,
            is_retryable=False,
            **kwargs
        )


class APIConnectionError(AIServiceError):
    """
    Raised when API connection fails.
    
    This is a retryable error.
    
    SOLID Principle Applied:
        - LSP: Fully substitutable for AIServiceError
        - SRP: Only represents connection error state
    """
    
    def __init__(self, provider: str, message: str, **kwargs):
        super().__init__(
            error_type=ErrorType.API_CONNECTION_ERROR,
            message=message,
            provider=provider,
            is_retryable=True,
            **kwargs
        )


def handle_provider_error(e: Exception, provider: str) -> AIServiceError:
    """
    Convert provider-specific exceptions to AIServiceError.
    
    Args:
        e: The original exception from the provider
        provider: Name of the AI provider
    
    Returns:
        AIServiceError: Standardized error
    
    Source/Caller:
        - Called by: Adapter implementations in exception handlers
    
    SOLID Principle Applied:
        - SRP: Only handles error conversion
        - OCP: New provider errors can be added without modifying existing logic
    """
    error_str = str(e).lower()
    
    # Check for quota exceeded
    if any(keyword in error_str for keyword in ["quota", "exceeded", "limit exceeded", "insufficient_quota"]):
        return QuotaExceededError(
            provider=provider,
            details={"original_error": str(e)}
        )
    
    # Check for rate limit
    if any(keyword in error_str for keyword in ["rate limit", "too many requests", "429"]):
        return RateLimitError(
            provider=provider,
            details={"original_error": str(e)}
        )
    
    # Check for authentication errors
    if any(keyword in error_str for keyword in ["authentication", "unauthorized", "api key", "401", "403"]):
        return AIServiceError(
            error_type=ErrorType.MISSING_API_KEY,
            message=f"Authentication failed for {provider}",
            provider=provider,
            is_retryable=False,
            details={"original_error": str(e)}
        )
    
    # Check for connection errors
    if any(keyword in error_str for keyword in ["connection", "timeout", "unreachable", "network"]):
        return APIConnectionError(
            provider=provider,
            message=f"Connection error with {provider}",
            details={"original_error": str(e)}
        )
    
    # Generic processing error
    return AIServiceError(
        error_type=ErrorType.PROCESSING_ERROR,
        message=f"Error processing request with {provider}: {str(e)}",
        provider=provider,
        is_retryable=True,
        details={"original_error": str(e)}
    )
