"""
Anthropic Claude Adapter
Implements the Claude AI provider.

SOLID Principles Applied:
    - SRP: Only handles Claude API communication
    - OCP: Extends BaseAIAdapter without modifying it
    - LSP: Fully substitutable for BaseAIAdapter
    - ISP: Implements only required call_ai method
    - DIP: Depends on BaseAIAdapter abstraction
"""
from anthropic import AsyncAnthropic
from typing import Dict, Any

from app.core.config import settings
from app.schemas.ai_schemas import AIModelConfig, AIResponse, AIProviderType
from app.services.ai_adapters.base_adapter import BaseAIAdapter, AIAdapterError


class ClaudeAdapter(BaseAIAdapter):
    """
    Adapter for Anthropic Claude models.
    
    Attributes:
        DEFAULT_MODEL (str): Default Claude model name
        client (AsyncAnthropic): Anthropic async client instance
    
    SOLID Principle Applied:
        - SRP: Only responsible for Claude API integration
    """
    
    DEFAULT_MODEL = "claude-3-opus-20240229"
    
    def __init__(self):
        """
        Initialize Claude adapter with API key.
        
        Raises:
            AIAdapterError: If API key is not configured
        
        SOLID Principle Applied:
            - SRP: Only handles initialization and client setup
        """
        if not settings.anthropic_api_key:
            raise AIAdapterError("Anthropic API key not configured")
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    async def call_ai(
        self,
        instruction_prompt: str,
        input_data: Dict[str, Any],
        model_config: AIModelConfig,
        model_name: str | None = None
    ) -> AIResponse:
        """
        Call Anthropic Claude with given parameters.
        
        Args:
            instruction_prompt (str): System/instruction prompt
            input_data (Dict[str, Any]): JSON-formatted input data
            model_config (AIModelConfig): Model configuration parameters
            model_name (str | None): Optional specific model name
        
        Returns:
            AIResponse: Standardized AI response
        
        Raises:
            AIAdapterError: If API call fails
        
        Source/Caller:
            - Called by: AIService.process_ai_request
            - Input Source: API route handler
        
        SOLID Principle Applied:
            - LSP: Returns AIResponse like all other adapters
            - DIP: Depends on AIModelConfig abstraction
        """
        try:
            # Validate configuration
            self._validate_config(model_config)
            
            response = await self.client.messages.create(
                model=model_name or self.DEFAULT_MODEL,
                max_tokens=model_config.max_tokens or 1024,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                system=instruction_prompt,
                messages=[
                    {"role": "user", "content": str(input_data)}
                ]
            )
            
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }
            
            return AIResponse(
                provider=AIProviderType.CLAUDE,
                content=response.content[0].text,
                usage=usage,
                model=response.model,
                raw_response=None
            )
        except AIAdapterError:
            raise
        except Exception as e:
            raise AIAdapterError(f"Claude API call failed: {str(e)}")
