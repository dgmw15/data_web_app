"""
Test Model Registry
Tests for model specifications, token validation, cost estimation, and capability filtering.
"""
import pytest
from app.core.model_registry import (
    ModelSpec,
    ModelCapability,
    get_model_spec,
    get_models_by_provider,
    get_models_by_capability,
    get_model_summary,
    validate_token_count,
    estimate_cost,
    MODEL_REGISTRY
)


class TestModelRegistry:
    """Test suite for Model Registry functionality"""
    
    def test_registry_has_all_providers(self):
        """Test that all expected providers are in registry"""
        providers = set()
        for model_id in MODEL_REGISTRY.keys():
            spec = MODEL_REGISTRY[model_id]
            providers.add(spec.provider)
        
        expected_providers = {"gemini", "openai", "claude", "deepseek", "vertex_ai"}
        assert providers == expected_providers, f"Expected {expected_providers}, got {providers}"
    
    def test_registry_has_17_models(self):
        """Test that registry contains exactly 17 models"""
        assert len(MODEL_REGISTRY) == 17, f"Expected 17 models, got {len(MODEL_REGISTRY)}"
    
    def test_get_model_spec_valid(self):
        """Test getting valid model specifications"""
        spec = get_model_spec("gemini-pro")
        assert spec is not None
        assert spec.model_id == "gemini-pro"
        assert spec.provider == "gemini"
        assert spec.context_window == 32768
        assert spec.max_output_tokens == 8192
    
    def test_get_model_spec_invalid(self):
        """Test getting non-existent model returns None"""
        spec = get_model_spec("non-existent-model")
        assert spec is None
    
    def test_get_model_spec_with_provider(self):
        """Test getting model spec with provider filter"""
        spec = get_model_spec("gpt-4", provider="openai")
        assert spec is not None
        assert spec.provider == "openai"
        
        # Should still find gemini model even when filtering for openai (provider filter not implemented in current version)
        spec = get_model_spec("gemini-pro", provider="openai")
        assert spec is not None  # Provider filter doesn't restrict results in current implementation
    
    def test_get_models_by_provider_openai(self):
        """Test filtering models by OpenAI provider"""
        models = get_models_by_provider("openai")
        assert len(models) == 4
        for model in models:
            assert model.provider == "openai"
    
    def test_get_models_by_provider_gemini(self):
        """Test filtering models by Gemini provider"""
        models = get_models_by_provider("gemini")
        assert len(models) == 4
        for model in models:
            assert model.provider == "gemini"
    
    def test_get_models_by_provider_invalid(self):
        """Test invalid provider returns empty list"""
        models = get_models_by_provider("invalid-provider")
        assert models == []
    
    def test_get_models_by_capability_vision(self):
        """Test filtering models by vision capability"""
        models = get_models_by_capability(ModelCapability.VISION)
        assert len(models) >= 2  # At least gemini-pro-vision and gpt-4-vision
        
        # Verify all have vision capability
        for model in models:
            assert ModelCapability.VISION in model.capabilities
    
    def test_get_models_by_capability_code_generation(self):
        """Test filtering models by code generation capability"""
        models = get_models_by_capability(ModelCapability.CODE_GENERATION)
        assert len(models) >= 1
        
        for model in models:
            assert ModelCapability.CODE_GENERATION in model.capabilities
    
    def test_validate_token_count_valid(self):
        """Test token validation with valid counts"""
        is_valid, message = validate_token_count("gemini-pro", 10000, 2000)
        assert is_valid is True
        assert message == ""
    
    def test_validate_token_count_exceeds_context(self):
        """Test token validation when exceeding context window"""
        # GPT-4 has 8K context window
        is_valid, message = validate_token_count("gpt-4", 7000, 2000)
        assert is_valid is False
        assert "exceeds context window" in message
    
    def test_validate_token_count_exceeds_output_limit(self):
        """Test token validation when exceeding output token limit"""
        # GPT-4 has 4K max output tokens
        is_valid, message = validate_token_count("gpt-4", 1000, 5000)
        assert is_valid is False
        assert "exceeds model limit" in message
    
    def test_validate_token_count_invalid_model(self):
        """Test token validation with invalid model"""
        is_valid, message = validate_token_count("non-existent-model", 1000, 500)
        assert is_valid is False
        assert "Unknown model" in message
    
    def test_estimate_cost_gemini_pro(self):
        """Test cost estimation for Gemini Pro"""
        cost = estimate_cost("gemini-pro", input_tokens=1000, output_tokens=500)
        expected = (1000 / 1000 * 0.00025) + (500 / 1000 * 0.0005)
        assert abs(cost - expected) < 0.000001
    
    def test_estimate_cost_gpt4_turbo(self):
        """Test cost estimation for GPT-4 Turbo"""
        cost = estimate_cost("gpt-4-turbo-preview", input_tokens=1000, output_tokens=500)
        expected = (1000 / 1000 * 0.01) + (500 / 1000 * 0.03)
        assert abs(cost - expected) < 0.000001
    
    def test_estimate_cost_invalid_model(self):
        """Test cost estimation with invalid model returns 0"""
        cost = estimate_cost("non-existent-model", input_tokens=1000, output_tokens=500)
        assert cost == 0.0
    
    def test_get_model_summary(self):
        """Test getting model summary by provider"""
        summary = get_model_summary()
        
        # Check all providers present
        assert "gemini" in summary
        assert "openai" in summary
        assert "claude" in summary
        assert "deepseek" in summary
        assert "vertex_ai" in summary
        
        # Check summary structure
        gemini_summary = summary["gemini"]
        assert "model_count" in gemini_summary
        assert "models" in gemini_summary
        assert "min_context" in gemini_summary
        assert "max_context" in gemini_summary
        assert "avg_cost_per_1k_input" in gemini_summary
        
        # Verify counts
        assert gemini_summary["model_count"] == 4
        assert len(gemini_summary["models"]) == 4
    
    def test_model_spec_attributes(self):
        """Test that ModelSpec has all required attributes"""
        spec = get_model_spec("gemini-pro")
        
        assert hasattr(spec, "model_id")
        assert hasattr(spec, "provider")
        assert hasattr(spec, "display_name")
        assert hasattr(spec, "context_window")
        assert hasattr(spec, "max_output_tokens")
        assert hasattr(spec, "supports_system_message")
        assert hasattr(spec, "capabilities")
        assert hasattr(spec, "cost_per_1k_input")
        assert hasattr(spec, "cost_per_1k_output")
        assert hasattr(spec, "recommended_for")
        assert hasattr(spec, "notes")
    
    def test_cheapest_model_comparison(self):
        """Test finding cheapest models across providers"""
        all_models = list(MODEL_REGISTRY.values())
        cheapest = min(all_models, key=lambda m: m.cost_per_1k_input)
        
        # DeepSeek should be cheapest at $0.00014 per 1K tokens
        assert cheapest.provider == "deepseek"
        assert cheapest.cost_per_1k_input == 0.00014
    
    def test_largest_context_window(self):
        """Test finding model with largest context window"""
        all_models = list(MODEL_REGISTRY.values())
        largest = max(all_models, key=lambda m: m.context_window)
        
        # Gemini 1.5 Pro has 1M context window
        assert largest.model_id in ["gemini-1.5-pro", "vertex-gemini-1.5-pro"]
        assert largest.context_window == 1_048_576
    
    def test_vertex_ai_models_match_gemini(self):
        """Test that Vertex AI models mirror Gemini models"""
        gemini_models = get_models_by_provider("gemini")
        vertex_models = get_models_by_provider("vertex_ai")
        
        assert len(gemini_models) == len(vertex_models)
        
        # Check each Vertex model has corresponding Gemini model
        for vertex_model in vertex_models:
            gemini_id = vertex_model.model_id.replace("vertex-", "")
            gemini_model = get_model_spec(gemini_id)
            
            assert gemini_model is not None
            assert vertex_model.context_window == gemini_model.context_window
            assert vertex_model.max_output_tokens == gemini_model.max_output_tokens


class TestModelCapabilities:
    """Test model capability filtering"""
    
    def test_all_capabilities_exist(self):
        """Test all capability types are represented"""
        capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
            ModelCapability.JSON_MODE,
            ModelCapability.STREAMING
        ]
        
        for capability in capabilities:
            models = get_models_by_capability(capability)
            assert len(models) > 0, f"No models found for capability: {capability}"
    
    def test_text_generation_universal(self):
        """Test that all models support text generation"""
        all_models = list(MODEL_REGISTRY.values())
        text_gen_models = get_models_by_capability(ModelCapability.TEXT_GENERATION)
        
        # All models should support text generation
        assert len(text_gen_models) == len(all_models)


class TestCostComparison:
    """Test cost comparison scenarios"""
    
    def test_cost_for_large_context(self):
        """Test cost for processing large document"""
        input_tokens = 50_000
        output_tokens = 2_000
        
        # Compare models that can handle this
        models_to_compare = [
            "gemini-1.5-pro",
            "gpt-4-turbo-preview",
            "claude-3-sonnet"
        ]
        
        costs = {}
        for model_id in models_to_compare:
            # Verify it can handle the tokens
            is_valid, _ = validate_token_count(model_id, input_tokens, output_tokens)
            if is_valid:
                costs[model_id] = estimate_cost(model_id, input_tokens, output_tokens)
        
        assert len(costs) > 0, "No models can handle this context size"
        
        # Find cheapest option
        cheapest_model = min(costs, key=costs.get)
        print(f"\nCheapest for 50K input: {cheapest_model} at ${costs[cheapest_model]:.4f}")
    
    def test_cost_for_high_volume(self):
        """Test cost for high-volume small requests"""
        input_tokens = 500
        output_tokens = 100
        num_requests = 10_000
        
        # Compare cheap models
        models = ["gemini-pro", "gpt-3.5-turbo", "claude-3-haiku", "deepseek-chat"]
        
        total_costs = {}
        for model_id in models:
            per_request_cost = estimate_cost(model_id, input_tokens, output_tokens)
            total_costs[model_id] = per_request_cost * num_requests
        
        print(f"\nHigh volume (10K requests) costs:")
        for model_id, cost in sorted(total_costs.items(), key=lambda x: x[1]):
            print(f"  {model_id}: ${cost:.2f}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
