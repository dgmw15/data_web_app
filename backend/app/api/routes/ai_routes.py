"""
AI Routes
API endpoints for AI operations.

SOLID Principles Applied:
    - SRP: Only handles HTTP request/response, no business logic
    - OCP: New endpoints can be added without modifying existing ones
    - DIP: Depends on AIService abstraction, not concrete implementations
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict

from app.schemas.ai_schemas import AIRequest, AIResponse
from app.services.ai_service import AIService
from app.services.prompt_manager import PromptManager
from app.core.quota_tracker import QuotaTracker

router = APIRouter()


@router.post("/process", response_model=AIResponse)
async def process_ai_request(request: AIRequest) -> AIResponse:
    """
    Process an AI request with specified provider and parameters.
    
    Args:
        request (AIRequest): AI request payload containing:
            - provider: AI provider to use (gemini/openai/claude/deepseek/vertex_ai)
            - instruction_prompt: Instructions for the AI
            - input_data: JSON data to process
            - model_config: Optional model parameters
            - model_name: Optional specific model override
    
    Returns:
        AIResponse: AI response with content and usage stats
    
    Raises:
        HTTPException: 
            - 400: Invalid input or configuration
            - 401: Missing or invalid API key
            - 429: Rate limit or quota exceeded
            - 500: Server/processing error
    
    Source/Caller:
        - Called by: Frontend client applications
        - Input Source: HTTP POST request body
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer, delegates to AIService
        - DIP: Depends on AIService interface
    """
    return await AIService.process_ai_request(request)


@router.get("/providers")
async def get_providers() -> Dict[str, list[str]]:
    """
    Get list of supported AI providers.
    
    Returns:
        Dict[str, list[str]]: Dictionary with supported providers list
    
    Source/Caller:
        - Called by: Frontend for provider selection UI
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
        - DIP: Depends on AIService interface
    """
    return {
        "providers": AIService.get_supported_providers()
    }


@router.get("/status")
async def get_provider_status() -> Dict[str, any]:
    """
    Get status of all AI providers including blocked status.
    
    Returns:
        Dict containing:
            - providers: List of all supported providers
            - blocked_providers: Dict of blocked providers with expiry times
            - available_providers: List of currently available providers
    
    Source/Caller:
        - Called by: Frontend for status monitoring
        - Called by: Monitoring systems
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
        - DIP: Depends on AIService interface
    """
    return AIService.get_provider_status()


@router.post("/unblock/{provider}")
async def unblock_provider(provider: str) -> Dict[str, str]:
    """
    Manually unblock a provider (admin operation).
    
    Args:
        provider: Provider name to unblock
    
    Returns:
        Dict with success message
    
    Source/Caller:
        - Called by: Admin tools or manual intervention
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
    """
    quota_tracker = QuotaTracker()
    quota_tracker.manually_unblock_provider(provider)
    
    return {
        "message": f"Provider {provider} has been unblocked",
        "provider": provider
    }


@router.get("/prompt-templates")
async def get_prompt_templates() -> Dict[str, Dict[str, str]]:
    """
    Get available prompt templates.
    
    Returns:
        Dict[str, Dict[str, str]]: Dictionary of template names and descriptions
    
    Source/Caller:
        - Called by: Frontend for template selection UI
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
        - DIP: Depends on PromptManager interface
    """
    return {
        "templates": PromptManager.list_templates()
    }
