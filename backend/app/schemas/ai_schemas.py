"""
AI Service Schemas
Defines request and response models for AI operations.

SOLID Principles Applied:
    - SRP: Each schema has one clear responsibility
    - OCP: New fields can be added without breaking existing code (Pydantic handles this)
    - ISP: Minimal, focused schemas - no bloated interfaces
    - DIP: Schemas are abstractions that other layers depend on
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class AIProviderType(str, Enum):
    """
    Supported AI provider types.
    
    Attributes:
        GEMINI: Google Gemini AI
        OPENAI: OpenAI GPT models
        CLAUDE: Anthropic Claude models
        DEEPSEEK: DeepSeek models
        VERTEX_AI: Google Vertex AI (GCP)
    
    SOLID Principle Applied:
        - OCP: New providers can be added without modifying existing code
    """
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    VERTEX_AI = "vertex_ai"


class AIModelConfig(BaseModel):
    """
    Configuration for AI model parameters.
    
    Attributes:
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        top_p: Nucleus sampling parameter
        frequency_penalty: Reduce repetition (OpenAI/DeepSeek)
        presence_penalty: Encourage new topics (OpenAI/DeepSeek)
    
    SOLID Principle Applied:
        - SRP: Only defines model configuration parameters
        - ISP: Only includes relevant configuration fields
    """
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1000, ge=1)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)


class AIRequest(BaseModel):
    """
    AI service request payload.
    
    Attributes:
        provider: AI provider to use
        instruction_prompt: System/instruction prompt for AI
        input_data: JSON-formatted input data
        ai_config: Optional model configuration overrides (renamed from model_config to avoid Pydantic conflict)
        model_name: Optional specific model name override
    
    SOLID Principle Applied:
        - SRP: Only defines request structure, no processing logic
        - DIP: Other layers depend on this abstraction
    """
    provider: AIProviderType
    instruction_prompt: str = Field(..., min_length=1)
    input_data: Dict[str, Any]
    ai_config: Optional[AIModelConfig] = Field(default_factory=AIModelConfig)
    model_name: Optional[str] = None


class AIResponse(BaseModel):
    """
    AI service response payload.
    
    Attributes:
        provider: AI provider used
        content: Generated response content
        usage: Token usage statistics
        model: Model name that was used
        raw_response: Optional raw API response for debugging
    
    SOLID Principle Applied:
        - SRP: Only defines response structure
        - LSP: All adapters return this same format for substitutability
    """
    provider: AIProviderType
    content: str
    usage: Dict[str, int]
    model: str
    raw_response: Optional[Dict[str, Any]] = None


class AIError(BaseModel):
    """
    AI service error response.
    
    Attributes:
        provider: AI provider that failed
        error_type: Type of error
        message: Human-readable error message
        details: Additional error details
    
    SOLID Principle Applied:
        - SRP: Only defines error structure
        - ISP: Minimal error information needed
    """
    provider: AIProviderType
    error_type: str
    message: str
    details: Optional[Dict[str, Any]] = None
