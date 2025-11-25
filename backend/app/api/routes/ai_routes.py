"""
AI Routes
API endpoints for AI operations.

SOLID Principles Applied:
    - SRP: Only handles HTTP request/response, no business logic
    - OCP: New endpoints can be added without modifying existing ones
    - DIP: Depends on AIService abstraction, not concrete implementations
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, List, Optional

from app.schemas.ai_schemas import AIRequest, AIResponse
from app.services.ai_service import AIService
from app.services.prompt_manager import PromptManager
from app.core.quota_tracker import QuotaTracker
from app.core.model_registry import (
    get_model_spec,
    get_models_by_provider,
    get_models_by_capability,
    get_model_summary,
    validate_token_count,
    estimate_cost,
    ModelCapability
)

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


@router.get("/models")
async def get_all_models() -> Dict[str, any]:
    """
    Get all available AI models with their specifications.
    
    Returns:
        Dict containing model summary by provider
    
    Source/Caller:
        - Called by: Frontend for model selection UI
        - Called by: Documentation generation
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
        - DIP: Depends on model registry interface
    """
    return get_model_summary()


@router.get("/models/{provider}")
async def get_provider_models(provider: str) -> Dict[str, List]:
    """
    Get all models for a specific provider.
    
    Args:
        provider: Provider name (gemini, openai, claude, deepseek, vertex_ai)
    
    Returns:
        Dict with list of model specifications
    
    Raises:
        HTTPException: 404 if provider not found
    
    Source/Caller:
        - Called by: Frontend for provider-specific model selection
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
    """
    models = get_models_by_provider(provider)
    
    if not models:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' not found or has no models"
        )
    
    return {
        "provider": provider,
        "models": [
            {
                "model_id": m.model_id,
                "display_name": m.display_name,
                "context_window": m.context_window,
                "max_output_tokens": m.max_output_tokens,
                "capabilities": [c.value for c in m.capabilities],
                "cost_per_1k_input": m.cost_per_1k_input,
                "cost_per_1k_output": m.cost_per_1k_output,
                "recommended_for": m.recommended_for,
                "notes": m.notes
            }
            for m in models
        ]
    }


@router.get("/models/spec/{model_id}")
async def get_model_specification(model_id: str) -> Dict[str, any]:
    """
    Get detailed specification for a specific model.
    
    Args:
        model_id: Model identifier
    
    Returns:
        Dict with complete model specification
    
    Raises:
        HTTPException: 404 if model not found
    
    Source/Caller:
        - Called by: Frontend for model detail view
        - Called by: Token validation before requests
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
    """
    spec = get_model_spec(model_id)
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found"
        )
    
    return {
        "model_id": spec.model_id,
        "provider": spec.provider,
        "display_name": spec.display_name,
        "context_window": spec.context_window,
        "max_output_tokens": spec.max_output_tokens,
        "supports_system_message": spec.supports_system_message,
        "capabilities": [c.value for c in spec.capabilities],
        "cost_per_1k_input": spec.cost_per_1k_input,
        "cost_per_1k_output": spec.cost_per_1k_output,
        "recommended_for": spec.recommended_for,
        "notes": spec.notes
    }


@router.post("/models/validate-tokens")
async def validate_tokens(
    model_id: str,
    input_tokens: int,
    requested_output_tokens: int
) -> Dict[str, any]:
    """
    Validate if token counts are within model limits.
    
    Args:
        model_id: Model identifier
        input_tokens: Number of input tokens
        requested_output_tokens: Requested output tokens
    
    Returns:
        Dict with validation result and message
    
    Source/Caller:
        - Called by: Frontend before submitting large requests
        - Called by: Batch processing validation
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
    """
    is_valid, error_message = validate_token_count(
        model_id, 
        input_tokens, 
        requested_output_tokens
    )
    
    return {
        "is_valid": is_valid,
        "message": error_message if not is_valid else "Token counts are valid",
        "model_id": model_id,
        "input_tokens": input_tokens,
        "requested_output_tokens": requested_output_tokens,
        "total_tokens": input_tokens + requested_output_tokens
    }


@router.post("/models/estimate-cost")
async def estimate_request_cost(
    model_id: str,
    input_tokens: int,
    output_tokens: int
) -> Dict[str, any]:
    """
    Estimate cost for a model request.
    
    Args:
        model_id: Model identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        Dict with cost estimate and breakdown
    
    Source/Caller:
        - Called by: Frontend for cost preview
        - Called by: Budget tracking systems
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
    """
    spec = get_model_spec(model_id)
    
    if not spec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found"
        )
    
    total_cost = estimate_cost(model_id, input_tokens, output_tokens)
    input_cost = (input_tokens / 1000) * spec.cost_per_1k_input
    output_cost = (output_tokens / 1000) * spec.cost_per_1k_output
    
    return {
        "model_id": model_id,
        "model_name": spec.display_name,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_breakdown": {
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6)
        },
        "rate_per_1k": {
            "input": spec.cost_per_1k_input,
            "output": spec.cost_per_1k_output
        }
    }


@router.get("/models/by-capability/{capability}")
async def get_models_by_capability_endpoint(capability: str) -> Dict[str, List]:
    """
    Get all models supporting a specific capability.
    
    Args:
        capability: Capability name (text_generation, vision, code_generation, etc.)
    
    Returns:
        Dict with list of models supporting the capability
    
    Raises:
        HTTPException: 400 if capability is invalid
    
    Source/Caller:
        - Called by: Frontend for capability-based filtering
    
    SOLID Principle Applied:
        - SRP: Only handles HTTP layer
    """
    try:
        capability_enum = ModelCapability(capability)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid capability: {capability}. Valid options: {[c.value for c in ModelCapability]}"
        )
    
    models = get_models_by_capability(capability_enum)
    
    return {
        "capability": capability,
        "model_count": len(models),
        "models": [
            {
                "model_id": m.model_id,
                "provider": m.provider,
                "display_name": m.display_name,
                "context_window": m.context_window,
                "cost_per_1k_input": m.cost_per_1k_input
            }
            for m in models
        ]
    }
