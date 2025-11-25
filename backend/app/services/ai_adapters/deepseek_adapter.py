"""
DeepSeek Adapter
Implements the DeepSeek AI provider using OpenAI-compatible API.

SOLID Principles Applied:
    - SRP: Only handles DeepSeek API communication
    - OCP: Extends BaseAIAdapter without modifying it
    - LSP: Fully substitutable for BaseAIAdapter
    - ISP: Implements only required call_ai method
    - DIP: Depends on BaseAIAdapter abstraction
"""
from openai import AsyncOpenAI
from typing import Dict, Any

from app.core.config import settings
from app.schemas.ai_schemas import AIModelConfig, AIResponse, AIProviderType
from app.services.ai_adapters.base_adapter import BaseAIAdapter, AIAdapterError


class DeepSeekAdapter(BaseAIAdapter):
    """
    Adapter for DeepSeek models (OpenAI-compatible API).
    
    Attributes:
        DEFAULT_MODEL (str): Default DeepSeek model name
        client (AsyncOpenAI): OpenAI async client configured for DeepSeek
    
    SOLID Principle Applied:
        - SRP: Only responsible for DeepSeek API integration
    """
    
    DEFAULT_MODEL = "deepseek-chat"
    
    def __init__(self):
        """
        Initialize DeepSeek adapter with API key and base URL.
        
        Raises:
            AIAdapterError: If API key is not configured
        
        SOLID Principle Applied:
            - SRP: Only handles initialization and client setup
        """
        if not settings.deepseek_api_key:
            raise AIAdapterError("DeepSeek API key not configured")
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url
        )
    
    async def call_ai(
        self,
        instruction_prompt: str,
        input_data: Dict[str, Any],
        model_config: AIModelConfig,
        model_name: str | None = None
    ) -> AIResponse:
        """
        Call DeepSeek AI with given parameters.
        
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
            
            response = await self.client.chat.completions.create(
                model=model_name or self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": instruction_prompt},
                    {"role": "user", "content": str(input_data)}
                ],
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
                top_p=model_config.top_p,
                frequency_penalty=model_config.frequency_penalty or 0.0,
                presence_penalty=model_config.presence_penalty or 0.0,
            )
            
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            
            return AIResponse(
                provider=AIProviderType.DEEPSEEK,
                content=response.choices[0].message.content,
                usage=usage,
                model=response.model,
                raw_response=None
            )
        except AIAdapterError:
            raise
        except Exception as e:
            raise AIAdapterError(f"DeepSeek API call failed: {str(e)}")
