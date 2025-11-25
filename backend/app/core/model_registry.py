"""
Model Registry
Centralized registry of all AI models with their specifications, context windows, and capabilities.

This module provides:
- Model metadata for all supported AI providers
- Context window limits for token management
- Model capabilities and pricing information
- Helper functions for model selection and validation

Source/Caller:
    - Called by: AI adapters, token management, cost estimation
    - Input Source: Static model specifications from AI providers

SOLID Principle Applied:
    - SRP: Only manages model metadata and specifications
    - OCP: New models can be added without modifying existing code
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ModelCapability(str, Enum):
    """
    Capabilities that AI models can have.
    
    Used to filter and select appropriate models for specific tasks.
    """
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    JSON_MODE = "json_mode"
    STREAMING = "streaming"


@dataclass
class ModelSpec:
    """
    Specification for an AI model.
    
    Attributes:
        model_id (str): Unique model identifier
        provider (str): AI provider name (gemini, openai, claude, etc.)
        display_name (str): Human-readable model name
        context_window (int): Maximum context length in tokens
        max_output_tokens (int): Maximum output tokens per request
        supports_system_message (bool): Whether model supports system messages
        capabilities (List[ModelCapability]): List of model capabilities
        cost_per_1k_input (float): Cost per 1K input tokens in USD
        cost_per_1k_output (float): Cost per 1K output tokens in USD
        recommended_for (List[str]): Use cases this model excels at
        notes (str): Additional notes or limitations
    """
    model_id: str
    provider: str
    display_name: str
    context_window: int
    max_output_tokens: int
    supports_system_message: bool = True
    capabilities: List[ModelCapability] = None
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    recommended_for: List[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = [ModelCapability.TEXT_GENERATION]
        if self.recommended_for is None:
            self.recommended_for = []


# ============================================================================
# GOOGLE GEMINI MODELS
# ============================================================================

GEMINI_MODELS = {
    "gemini-pro": ModelSpec(
        model_id="gemini-pro",
        provider="gemini",
        display_name="Gemini Pro",
        context_window=32_768,
        max_output_tokens=8_192,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.00025,  # $0.25 per 1M tokens
        cost_per_1k_output=0.0005,  # $0.50 per 1M tokens
        recommended_for=[
            "General data analysis",
            "Text summarization",
            "Code generation",
            "Question answering"
        ],
        notes="Free tier available with rate limits. Fast and efficient for most tasks."
    ),
    
    "gemini-pro-vision": ModelSpec(
        model_id="gemini-pro-vision",
        provider="gemini",
        display_name="Gemini Pro Vision",
        context_window=16_384,
        max_output_tokens=8_192,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.0005,
        recommended_for=[
            "Image analysis",
            "Chart interpretation",
            "Visual data extraction"
        ],
        notes="Can process images and text. Limited to 16 images per request."
    ),
    
    "gemini-1.5-pro": ModelSpec(
        model_id="gemini-1.5-pro",
        provider="gemini",
        display_name="Gemini 1.5 Pro",
        context_window=1_048_576,  # 1M tokens!
        max_output_tokens=8_192,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.0035,  # $3.50 per 1M for <128K tokens
        cost_per_1k_output=0.0105,  # $10.50 per 1M
        recommended_for=[
            "Large document analysis",
            "Long conversation context",
            "Complex reasoning tasks",
            "Multi-document synthesis"
        ],
        notes="Extremely large context window. Higher cost but handles massive inputs."
    ),
    
    "gemini-1.5-flash": ModelSpec(
        model_id="gemini-1.5-flash",
        provider="gemini",
        display_name="Gemini 1.5 Flash",
        context_window=1_048_576,
        max_output_tokens=8_192,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.00035,  # $0.35 per 1M
        cost_per_1k_output=0.00053,  # $0.53 per 1M
        recommended_for=[
            "High-volume processing",
            "Cost-sensitive applications",
            "Fast responses needed"
        ],
        notes="Fastest and cheapest with 1M context. Great for production workloads."
    ),
}


# ============================================================================
# OPENAI MODELS
# ============================================================================

OPENAI_MODELS = {
    "gpt-4-turbo-preview": ModelSpec(
        model_id="gpt-4-turbo-preview",
        provider="openai",
        display_name="GPT-4 Turbo Preview",
        context_window=128_000,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.01,  # $10 per 1M tokens
        cost_per_1k_output=0.03,  # $30 per 1M tokens
        recommended_for=[
            "Complex reasoning",
            "Code generation",
            "Long document analysis",
            "Creative writing"
        ],
        notes="Latest GPT-4 with 128K context. Best overall reasoning capabilities."
    ),
    
    "gpt-4": ModelSpec(
        model_id="gpt-4",
        provider="openai",
        display_name="GPT-4",
        context_window=8_192,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.03,  # $30 per 1M tokens
        cost_per_1k_output=0.06,  # $60 per 1M tokens
        recommended_for=[
            "High-quality outputs",
            "Complex problem solving"
        ],
        notes="Original GPT-4. More expensive and smaller context than Turbo."
    ),
    
    "gpt-4-vision-preview": ModelSpec(
        model_id="gpt-4-vision-preview",
        provider="openai",
        display_name="GPT-4 Vision",
        context_window=128_000,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.VISION,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
        recommended_for=[
            "Image analysis",
            "Chart interpretation",
            "Visual reasoning"
        ],
        notes="GPT-4 with vision capabilities. Can analyze images and charts."
    ),
    
    "gpt-3.5-turbo": ModelSpec(
        model_id="gpt-3.5-turbo",
        provider="openai",
        display_name="GPT-3.5 Turbo",
        context_window=16_385,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.0005,  # $0.50 per 1M tokens
        cost_per_1k_output=0.0015,  # $1.50 per 1M tokens
        recommended_for=[
            "Cost-effective processing",
            "Simple queries",
            "High-volume tasks"
        ],
        notes="Much cheaper than GPT-4. Good for simple tasks and high volume."
    ),
}


# ============================================================================
# ANTHROPIC CLAUDE MODELS
# ============================================================================

CLAUDE_MODELS = {
    "claude-3-opus-20240229": ModelSpec(
        model_id="claude-3-opus-20240229",
        provider="claude",
        display_name="Claude 3 Opus",
        context_window=200_000,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.015,  # $15 per 1M tokens
        cost_per_1k_output=0.075,  # $75 per 1M tokens
        recommended_for=[
            "Complex analysis",
            "Research tasks",
            "Long document processing",
            "High-stakes outputs"
        ],
        notes="Most capable Claude model. Excellent for analysis and reasoning."
    ),
    
    "claude-3-sonnet-20240229": ModelSpec(
        model_id="claude-3-sonnet-20240229",
        provider="claude",
        display_name="Claude 3 Sonnet",
        context_window=200_000,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.003,  # $3 per 1M tokens
        cost_per_1k_output=0.015,  # $15 per 1M tokens
        recommended_for=[
            "Balanced performance/cost",
            "General purpose tasks",
            "Data analysis"
        ],
        notes="Good balance of capability and cost. Recommended for most use cases."
    ),
    
    "claude-3-haiku-20240307": ModelSpec(
        model_id="claude-3-haiku-20240307",
        provider="claude",
        display_name="Claude 3 Haiku",
        context_window=200_000,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.00025,  # $0.25 per 1M tokens
        cost_per_1k_output=0.00125,  # $1.25 per 1M tokens
        recommended_for=[
            "Fast responses",
            "High-volume processing",
            "Cost-sensitive applications"
        ],
        notes="Fastest and cheapest Claude. Great for simple tasks at scale."
    ),
}


# ============================================================================
# DEEPSEEK MODELS
# ============================================================================

DEEPSEEK_MODELS = {
    "deepseek-chat": ModelSpec(
        model_id="deepseek-chat",
        provider="deepseek",
        display_name="DeepSeek Chat",
        context_window=32_768,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.00014,  # $0.14 per 1M tokens
        cost_per_1k_output=0.00028,  # $0.28 per 1M tokens
        recommended_for=[
            "Cost-effective processing",
            "General chat",
            "Simple analysis"
        ],
        notes="Very affordable. Good for budget-conscious applications."
    ),
    
    "deepseek-coder": ModelSpec(
        model_id="deepseek-coder",
        provider="deepseek",
        display_name="DeepSeek Coder",
        context_window=32_768,
        max_output_tokens=4_096,
        supports_system_message=True,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.STREAMING
        ],
        cost_per_1k_input=0.00014,
        cost_per_1k_output=0.00028,
        recommended_for=[
            "Code generation",
            "Code review",
            "Technical documentation"
        ],
        notes="Specialized for coding tasks. Better code quality than chat model."
    ),
}


# ============================================================================
# GOOGLE VERTEX AI MODELS (Using Gemini on GCP)
# ============================================================================

VERTEX_AI_MODELS = {
    **{f"vertex-{k}": ModelSpec(
        model_id=f"vertex-{v.model_id}",
        provider="vertex_ai",
        display_name=f"{v.display_name} (Vertex AI)",
        context_window=v.context_window,
        max_output_tokens=v.max_output_tokens,
        supports_system_message=v.supports_system_message,
        capabilities=v.capabilities,
        cost_per_1k_input=v.cost_per_1k_input,
        cost_per_1k_output=v.cost_per_1k_output,
        recommended_for=v.recommended_for + ["Enterprise deployments", "GCP integration"],
        notes=f"Vertex AI version of {v.display_name}. {v.notes}"
    ) for k, v in GEMINI_MODELS.items()}
}


# ============================================================================
# MASTER MODEL REGISTRY
# ============================================================================

MODEL_REGISTRY: Dict[str, ModelSpec] = {
    **GEMINI_MODELS,
    **OPENAI_MODELS,
    **CLAUDE_MODELS,
    **DEEPSEEK_MODELS,
    **VERTEX_AI_MODELS,
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_model_spec(model_id: str, provider: str = None) -> Optional[ModelSpec]:
    """
    Get model specification by ID and optional provider.
    
    Args:
        model_id (str): Model identifier
        provider (str, optional): Provider name to narrow search
    
    Returns:
        Optional[ModelSpec]: Model specification or None if not found
    
    Source/Caller:
        - Called by: AI adapters during initialization
        - Input Source: Model ID from request
    
    SOLID Principle Applied:
        - SRP: Only retrieves model specifications
    """
    if model_id in MODEL_REGISTRY:
        return MODEL_REGISTRY[model_id]
    
    # If provider specified, try with provider prefix
    if provider:
        prefixed_id = f"{provider}-{model_id}"
        if prefixed_id in MODEL_REGISTRY:
            return MODEL_REGISTRY[prefixed_id]
    
    return None


def get_models_by_provider(provider: str) -> List[ModelSpec]:
    """
    Get all models for a specific provider.
    
    Args:
        provider (str): Provider name (gemini, openai, claude, etc.)
    
    Returns:
        List[ModelSpec]: List of model specifications for the provider
    
    Source/Caller:
        - Called by: API endpoints, UI model selectors
        - Input Source: Provider selection
    
    SOLID Principle Applied:
        - SRP: Only filters models by provider
    """
    return [
        spec for spec in MODEL_REGISTRY.values()
        if spec.provider == provider
    ]


def get_models_by_capability(capability: ModelCapability) -> List[ModelSpec]:
    """
    Get all models supporting a specific capability.
    
    Args:
        capability (ModelCapability): Required capability
    
    Returns:
        List[ModelSpec]: List of models with the capability
    
    Source/Caller:
        - Called by: Task-specific model selection
        - Input Source: Task requirements
    
    SOLID Principle Applied:
        - SRP: Only filters models by capability
    """
    return [
        spec for spec in MODEL_REGISTRY.values()
        if capability in spec.capabilities
    ]


def validate_token_count(model_id: str, input_tokens: int, requested_output_tokens: int) -> tuple[bool, str]:
    """
    Validate if token counts are within model limits.
    
    Args:
        model_id (str): Model identifier
        input_tokens (int): Number of input tokens
        requested_output_tokens (int): Requested output tokens
    
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    
    Source/Caller:
        - Called by: AI adapters before making API calls
        - Input Source: Token count from prompt encoding
    
    SOLID Principle Applied:
        - SRP: Only validates token limits
    
    Example:
        >>> is_valid, msg = validate_token_count("gpt-4", 7000, 2000)
        >>> if not is_valid:
        ...     raise ValueError(msg)
    """
    spec = get_model_spec(model_id)
    
    if not spec:
        return False, f"Unknown model: {model_id}"
    
    total_tokens = input_tokens + requested_output_tokens
    
    if input_tokens > spec.context_window:
        return False, (
            f"Input tokens ({input_tokens}) exceeds model context window "
            f"({spec.context_window}) for {spec.display_name}"
        )
    
    if requested_output_tokens > spec.max_output_tokens:
        return False, (
            f"Requested output tokens ({requested_output_tokens}) exceeds model limit "
            f"({spec.max_output_tokens}) for {spec.display_name}"
        )
    
    if total_tokens > spec.context_window:
        return False, (
            f"Total tokens ({total_tokens}) exceeds context window "
            f"({spec.context_window}) for {spec.display_name}. "
            f"Try reducing input or output token limit."
        )
    
    return True, ""


def estimate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimate cost for a model request.
    
    Args:
        model_id (str): Model identifier
        input_tokens (int): Number of input tokens
        output_tokens (int): Number of output tokens
    
    Returns:
        float: Estimated cost in USD
    
    Source/Caller:
        - Called by: Cost tracking, budget management
        - Input Source: Token usage from API responses
    
    SOLID Principle Applied:
        - SRP: Only calculates cost estimates
    
    Example:
        >>> cost = estimate_cost("gpt-4-turbo-preview", 1000, 500)
        >>> print(f"Estimated cost: ${cost:.4f}")
    """
    spec = get_model_spec(model_id)
    
    if not spec:
        return 0.0
    
    input_cost = (input_tokens / 1000) * spec.cost_per_1k_input
    output_cost = (output_tokens / 1000) * spec.cost_per_1k_output
    
    return input_cost + output_cost


def get_default_model(provider: str) -> Optional[str]:
    """
    Get the default/recommended model for a provider.
    
    Args:
        provider (str): Provider name
    
    Returns:
        Optional[str]: Model ID of recommended model
    
    Source/Caller:
        - Called by: AI adapters when no model specified
        - Input Source: Provider selection
    
    SOLID Principle Applied:
        - SRP: Only returns default model mapping
    """
    defaults = {
        "gemini": "gemini-pro",
        "openai": "gpt-4-turbo-preview",
        "claude": "claude-3-sonnet-20240229",
        "deepseek": "deepseek-chat",
        "vertex_ai": "vertex-gemini-pro",
    }
    
    return defaults.get(provider)


def get_model_summary() -> Dict[str, Dict]:
    """
    Get summary statistics for all models.
    
    Returns:
        Dict[str, Dict]: Summary by provider with model counts and capabilities
    
    Source/Caller:
        - Called by: Admin dashboards, documentation generation
        - Input Source: Model registry
    
    SOLID Principle Applied:
        - SRP: Only aggregates model statistics
    """
    summary = {}
    
    for spec in MODEL_REGISTRY.values():
        provider = spec.provider
        
        if provider not in summary:
            summary[provider] = {
                "model_count": 0,
                "models": [],
                "min_context": float('inf'),
                "max_context": 0,
                "avg_cost_per_1k_input": 0,
            }
        
        summary[provider]["model_count"] += 1
        summary[provider]["models"].append(spec.model_id)
        summary[provider]["min_context"] = min(summary[provider]["min_context"], spec.context_window)
        summary[provider]["max_context"] = max(summary[provider]["max_context"], spec.context_window)
        summary[provider]["avg_cost_per_1k_input"] += spec.cost_per_1k_input
    
    # Calculate averages
    for provider_data in summary.values():
        if provider_data["model_count"] > 0:
            provider_data["avg_cost_per_1k_input"] /= provider_data["model_count"]
    
    return summary
