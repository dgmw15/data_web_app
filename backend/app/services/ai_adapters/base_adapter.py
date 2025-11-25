"""
AI Provider Adapters
Implements adapter pattern for different AI providers.

SOLID Principles Applied:
    - SRP: Each adapter only handles communication with one AI provider
    - OCP: New adapters can be added without modifying existing code
    - LSP: All adapters are substitutable through BaseAIAdapter interface
    - ISP: Minimal interface with only required methods
    - DIP: Depends on abstractions (AIModelConfig, AIResponse)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import json

from app.schemas.ai_schemas import AIModelConfig, AIResponse
from app.core.errors import InvalidInputError


class BaseAIAdapter(ABC):
    """
    Abstract base class for AI provider adapters.
    
    All provider adapters must implement the `call_ai` method.
    Provides common functionality for message formatting and validation.
    
    SOLID Principles Applied:
        - SRP: Only defines interface and common utilities
        - OCP: Open for extension (subclasses), closed for modification
        - LSP: Defines contract that all subclasses must honor
        - ISP: Minimal interface with only essential method
        - DIP: Depends on abstractions (schemas), not concrete implementations
    """
    
    @abstractmethod
    async def call_ai(
        self,
        instruction_prompt: str,
        input_data: Dict[str, Any],
        model_config: AIModelConfig,
        model_name: str | None = None
    ) -> AIResponse:
        """
        Call the AI provider with given parameters.
        
        Args:
            instruction_prompt (str): System/instruction prompt
            input_data (Dict[str, Any]): JSON-formatted input data
            model_config (AIModelConfig): Model configuration parameters
            model_name (str | None): Optional specific model name
        
        Returns:
            AIResponse: Standardized AI response
        
        Raises:
            AIServiceError: If API call fails (ensures LSP compliance)
        
        Source/Caller:
            - Called by: AIService orchestrator
        
        SOLID Principle Applied:
            - LSP: All implementations must return AIResponse or raise AIServiceError
            - DIP: Depends on AIModelConfig and AIResponse abstractions
        """
        pass
    
    def _format_input_message(self, instruction_prompt: str, input_data: Dict[str, Any]) -> str:
        """
        Format instruction and input data into a single message.
        
        Args:
            instruction_prompt (str): The instruction prompt
            input_data (Dict[str, Any]): The input data
        
        Returns:
            str: Formatted message combining instruction and data
        
        Source/Caller:
            - Called by: Individual adapter implementations
        
        SOLID Principle Applied:
            - SRP: Only handles message formatting, nothing else
            - DIP: Works with generic Dict, not specific data structures
        """
        formatted_data = json.dumps(input_data, indent=2)
        return f"{instruction_prompt}\n\nInput Data:\n{formatted_data}"
    
    def _validate_config(self, model_config: AIModelConfig) -> None:
        """
        Validate model configuration parameters.
        
        Args:
            model_config (AIModelConfig): Configuration to validate
        
        Raises:
            InvalidInputError: If configuration is invalid
        
        Source/Caller:
            - Called by: Adapter implementations before API calls
        
        SOLID Principle Applied:
            - SRP: Only validates configuration, no other responsibilities
            - LSP: All adapters can use this for consistent validation
        """
        if model_config.temperature < 0 or model_config.temperature > 2:
            raise InvalidInputError(
                f"Invalid temperature: {model_config.temperature}. Must be between 0.0 and 2.0"
            )
        
        if model_config.max_tokens and model_config.max_tokens < 1:
            raise InvalidInputError(
                f"Invalid max_tokens: {model_config.max_tokens}. Must be at least 1"
            )
        
        if model_config.top_p and (model_config.top_p < 0 or model_config.top_p > 1):
            raise InvalidInputError(
                f"Invalid top_p: {model_config.top_p}. Must be between 0.0 and 1.0"
            )
