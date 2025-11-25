"""
AI Service
Main orchestrator for AI operations using the adapter pattern.

SOLID Principles Applied:
    - SRP: Only orchestrates AI requests, no direct provider logic
    - OCP: New providers can be added by registering in _adapters dict
    - LSP: All adapters are interchangeable through BaseAIAdapter
    - ISP: Minimal interface, only what's needed
    - DIP: Depends on BaseAIAdapter abstraction, not concrete implementations
"""
from typing import Dict, Type
from fastapi import HTTPException

from app.schemas.ai_schemas import (
    AIRequest,
    AIResponse,
    AIProviderType,
    AIModelConfig,
)
from app.services.ai_adapters import (
    BaseAIAdapter,
    GeminiAdapter,
    OpenAIAdapter,
    ClaudeAdapter,
    DeepSeekAdapter,
    VertexAIAdapter,
)
from app.core.errors import (
    AIServiceError,
    QuotaExceededError,
    InvalidInputError,
    ErrorType
)
from app.core.quota_tracker import QuotaTracker


class AIService:
    """
    AI Service orchestrator implementing factory pattern.
    
    Routes requests to appropriate AI provider adapters.
    
    Attributes:
        _adapters (Dict): Mapping of provider types to adapter classes
    
    SOLID Principles Applied:
        - SRP: Only handles routing to correct adapter
        - OCP: Adding new providers doesn't modify existing logic
        - DIP: Depends on BaseAIAdapter interface
    """
    
    # Factory mapping: provider type -> adapter class
    _adapters: Dict[AIProviderType, Type[BaseAIAdapter]] = {
        AIProviderType.GEMINI: GeminiAdapter,
        AIProviderType.OPENAI: OpenAIAdapter,
        AIProviderType.CLAUDE: ClaudeAdapter,
        AIProviderType.DEEPSEEK: DeepSeekAdapter,
        AIProviderType.VERTEX_AI: VertexAIAdapter,
    }
    
    @classmethod
    def _get_adapter(cls, provider: AIProviderType) -> BaseAIAdapter:
        """
        Factory method to instantiate the appropriate adapter.
        
        Args:
            provider (AIProviderType): The AI provider to use
        
        Returns:
            BaseAIAdapter: Instance of the appropriate adapter
        
        Raises:
            HTTPException: If provider is not supported or initialization fails
        
        Source/Caller:
            - Called by: AIService.process_ai_request
        
        SOLID Principle Applied:
            - OCP: New adapters registered without modifying this method
            - DIP: Returns BaseAIAdapter interface, not concrete type
        """
        adapter_class = cls._adapters.get(provider)
        
        if not adapter_class:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_type": ErrorType.INVALID_PROVIDER.value,
                    "message": f"Unsupported AI provider: {provider}",
                    "provider": provider.value if provider else None
                }
            )
        
        try:
            return adapter_class()
        except AIServiceError as e:
            raise HTTPException(
                status_code=500 if e.error_type not in [ErrorType.INVALID_INPUT, ErrorType.MISSING_API_KEY] else 400,
                detail=e.to_dict()
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_type": ErrorType.ADAPTER_INITIALIZATION_ERROR.value,
                    "message": f"Failed to initialize {provider} adapter: {str(e)}",
                    "provider": provider.value
                }
            )
    
    @classmethod
    async def process_ai_request(cls, request: AIRequest) -> AIResponse:
        """
        Process an AI request using the specified provider.
        
        Args:
            request (AIRequest): The AI request payload
        
        Returns:
            AIResponse: The AI response
        
        Raises:
            HTTPException: If request processing fails
        
        Source/Caller:
            - Called by: API route handlers (app.api.routes.ai_routes)
            - Input Source: Client HTTP request
        
        SOLID Principle Applied:
            - SRP: Only orchestrates the request flow
            - LSP: All adapters handled uniformly
            - DIP: Works with AIRequest/AIResponse abstractions
        """
        quota_tracker = QuotaTracker()
        
        try:
            # Check if provider is blocked before attempting to initialize
            provider_name = request.provider.value
            if quota_tracker.is_provider_blocked(provider_name):
                raise QuotaExceededError(
                    provider=provider_name,
                    message=f"Provider {provider_name} is currently blocked due to quota exceeded. Please try again later.",
                    details={
                        "blocked_providers": quota_tracker.get_blocked_providers()
                    }
                )
            
            # Get the appropriate adapter (Factory Pattern)
            adapter = cls._get_adapter(request.provider)
            
            # Ensure ai_config exists
            ai_config = request.ai_config or AIModelConfig()
            
            # Call the AI provider (Strategy Pattern)
            response = await adapter.call_ai(
                instruction_prompt=request.instruction_prompt,
                input_data=request.input_data,
                model_config=ai_config,
                model_name=request.model_name,
            )
            
            return response
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except QuotaExceededError as e:
            # Quota exceeded - return 429 status
            raise HTTPException(
                status_code=429,
                detail=e.to_dict()
            )
        except InvalidInputError as e:
            # Client input error - return 400 status
            raise HTTPException(
                status_code=400,
                detail=e.to_dict()
            )
        except AIServiceError as e:
            # Determine appropriate status code based on error type
            status_code = 500
            if e.error_type in [ErrorType.INVALID_INPUT, ErrorType.INVALID_CONFIG, ErrorType.INVALID_PROVIDER]:
                status_code = 400
            elif e.error_type == ErrorType.MISSING_API_KEY:
                status_code = 401
            elif e.error_type in [ErrorType.QUOTA_EXCEEDED, ErrorType.RATE_LIMIT_EXCEEDED]:
                status_code = 429
            
            raise HTTPException(
                status_code=status_code,
                detail=e.to_dict()
            )
        except Exception as e:
            # Unexpected error - return 500 status
            raise HTTPException(
                status_code=500,
                detail={
                    "error_type": ErrorType.PROCESSING_ERROR.value,
                    "message": f"Unexpected error during AI processing: {str(e)}",
                    "provider": request.provider.value,
                    "is_retryable": False
                }
            )
    
    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """
        Get list of supported AI providers.
        
        Returns:
            list[str]: List of supported provider names
        
        Source/Caller:
            - Called by: API info/documentation endpoints
        
        SOLID Principle Applied:
            - OCP: Dynamically reads from _adapters registry
        """
        return [provider.value for provider in cls._adapters.keys()]
    
    @classmethod
    def get_provider_status(cls) -> Dict[str, Dict[str, any]]:
        """
        Get status of all providers including blocked status.
        
        Returns:
            Dict with provider statuses
        
        Source/Caller:
            - Called by: Status monitoring endpoints
        
        SOLID Principle Applied:
            - SRP: Only retrieves status information
        """
        quota_tracker = QuotaTracker()
        blocked_providers = quota_tracker.get_blocked_providers()
        
        return {
            "providers": cls.get_supported_providers(),
            "blocked_providers": blocked_providers,
            "available_providers": [
                p for p in cls.get_supported_providers()
                if p not in blocked_providers
            ]
        }
