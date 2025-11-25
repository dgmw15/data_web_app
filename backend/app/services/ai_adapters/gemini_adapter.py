"""
Google Gemini AI Adapter
Implements the Gemini AI provider.

SOLID Principles Applied:
    - SRP: Only handles Gemini API communication
    - OCP: Extends BaseAIAdapter without modifying it
    - LSP: Fully substitutable for BaseAIAdapter
    - ISP: Implements only required call_ai method
    - DIP: Depends on BaseAIAdapter abstraction
"""
import google.generativeai as genai
from typing import Dict, Any

from app.core.config import settings
from app.schemas.ai_schemas import AIModelConfig, AIResponse, AIProviderType
from app.services.ai_adapters.base_adapter import BaseAIAdapter
from app.core.errors import (
    AIServiceError,
    ErrorType,
    handle_provider_error,
    InvalidInputError
)
from app.core.quota_tracker import QuotaTracker


class GeminiAdapter(BaseAIAdapter):
    """
    Adapter for Google Gemini AI.
    
    Attributes:
        DEFAULT_MODEL (str): Default Gemini model name
        PROVIDER_NAME (str): Provider identifier
    
    SOLID Principle Applied:
        - SRP: Only responsible for Gemini API integration
    """
    
    DEFAULT_MODEL = "gemini-pro"
    PROVIDER_NAME = "gemini"
    
    def __init__(self):
        """
        Initialize Gemini adapter with API key.
        
        Raises:
            AIServiceError: If API key is not configured
        
        SOLID Principle Applied:
            - SRP: Only handles initialization, no business logic
        """
        if not settings.gemini_api_key:
            raise AIServiceError(
                error_type=ErrorType.MISSING_API_KEY,
                message="Gemini API key not configured",
                provider=self.PROVIDER_NAME
            )
        genai.configure(api_key=settings.gemini_api_key)
    
    async def call_ai(
        self,
        instruction_prompt: str,
        input_data: Dict[str, Any],
        model_config: AIModelConfig,
        model_name: str | None = None
    ) -> AIResponse:
        """
        Call Google Gemini AI with given parameters.
        
        Args:
            instruction_prompt (str): System/instruction prompt
            input_data (Dict[str, Any]): JSON-formatted input data
            model_config (AIModelConfig): Model configuration parameters
            model_name (str | None): Optional specific model name
        
        Returns:
            AIResponse: Standardized AI response
        
        Raises:
            AIServiceError: If API call fails
        
        Source/Caller:
            - Called by: AIService.process_ai_request
            - Input Source: API route handler
        
        SOLID Principle Applied:
            - LSP: Returns AIResponse like all other adapters
            - DIP: Depends on AIModelConfig abstraction
        """
        quota_tracker = QuotaTracker()
        
        # Check if provider is blocked due to quota
        if quota_tracker.is_provider_blocked(self.PROVIDER_NAME):
            raise AIServiceError(
                error_type=ErrorType.QUOTA_EXCEEDED,
                message=f"{self.PROVIDER_NAME} is currently blocked due to quota exceeded",
                provider=self.PROVIDER_NAME,
                is_retryable=False
            )
        
        try:
            # Validate configuration
            self._validate_config(model_config)
            
            # Validate input
            if not instruction_prompt or not instruction_prompt.strip():
                raise InvalidInputError("Instruction prompt cannot be empty")
            
            if not input_data:
                raise InvalidInputError("Input data cannot be empty")
            
            model = genai.GenerativeModel(model_name or self.DEFAULT_MODEL)
            
            generation_config = genai.types.GenerationConfig(
                temperature=model_config.temperature,
                max_output_tokens=model_config.max_tokens,
                top_p=model_config.top_p,
            )
            
            message = self._format_input_message(instruction_prompt, input_data)
            
            response = await model.generate_content_async(
                message,
                generation_config=generation_config
            )
            
            # Validate response
            if not response or not response.text:
                raise AIServiceError(
                    error_type=ErrorType.EMPTY_RESPONSE,
                    message="Received empty response from Gemini",
                    provider=self.PROVIDER_NAME,
                    is_retryable=True
                )
            
            # Extract usage information
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }
            
            return AIResponse(
                provider=AIProviderType.GEMINI,
                content=response.text,
                usage=usage,
                model=model_name or self.DEFAULT_MODEL,
                raw_response=None
            )
            
        except InvalidInputError:
            # Re-raise input validation errors as-is
            raise
        except AIServiceError as e:
            # Check if it's a quota error and block the provider
            if e.error_type == ErrorType.QUOTA_EXCEEDED:
                quota_tracker.block_provider(self.PROVIDER_NAME)
            raise
        except Exception as e:
            # Convert provider-specific errors to standardized errors
            standardized_error = handle_provider_error(e, self.PROVIDER_NAME)
            
            # Block provider if quota exceeded
            if standardized_error.error_type == ErrorType.QUOTA_EXCEEDED:
                quota_tracker.block_provider(self.PROVIDER_NAME)
            
            raise standardized_error
