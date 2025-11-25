"""
AI Schemas Tests
Tests for Pydantic models used in AI operations.

Test Coverage:
- AIProviderType enum
- AIModelConfig validation and defaults
- AIRequest creation and validation
- AIResponse structure
- AIError structure
- Field constraints and validation

Troubleshooting Guide:
- ValidationError → Check field constraints (ge, le, min_length)
- Missing field → Verify required vs optional fields
- Type error → Check field type annotations
- Default values → Verify Field(default=...) declarations
"""
import pytest
from pydantic import ValidationError
from app.schemas.ai_schemas import (
    AIProviderType,
    AIModelConfig,
    AIRequest,
    AIResponse,
    AIError
)


class TestAIProviderType:
    """
    Test suite for AIProviderType enum.
    
    What it tests:
    - All providers are defined
    - String values are correct
    - Can be used in comparisons
    
    Troubleshooting:
    - Missing provider → Add to AIProviderType enum
    - Wrong value → Check enum string assignment
    """
    
    def test_all_providers_exist(self):
        """
        Test: All expected AI providers are defined
        Input: Access each provider type
        Expected: No AttributeError
        """
        assert AIProviderType.GEMINI
        assert AIProviderType.OPENAI
        assert AIProviderType.CLAUDE
        assert AIProviderType.DEEPSEEK
        assert AIProviderType.VERTEX_AI
    
    def test_provider_string_values(self):
        """
        Test: Provider enum values are lowercase strings
        Input: Provider enum members
        Expected: Correct string values
        """
        assert AIProviderType.GEMINI.value == "gemini"
        assert AIProviderType.OPENAI.value == "openai"
        assert AIProviderType.CLAUDE.value == "claude"
        assert AIProviderType.DEEPSEEK.value == "deepseek"
        assert AIProviderType.VERTEX_AI.value == "vertex_ai"
    
    def test_provider_comparison(self):
        """
        Test: Can compare provider types
        Input: Two provider instances
        Expected: Equality works correctly
        """
        provider1 = AIProviderType.GEMINI
        provider2 = AIProviderType.GEMINI
        provider3 = AIProviderType.OPENAI
        
        assert provider1 == provider2
        assert provider1 != provider3


class TestAIModelConfig:
    """
    Test suite for AIModelConfig Pydantic model.
    
    What it tests:
    - Default values
    - Field validation (temperature, max_tokens, top_p, etc.)
    - Constraint violations
    - Optional fields
    
    Troubleshooting:
    - ValidationError → Check Field constraints (ge, le)
    - Wrong default → Verify Field(default=...) value
    - Type mismatch → Check field type annotation
    """
    
    def test_default_values(self):
        """
        Test: AIModelConfig has correct defaults
        Input: AIModelConfig()
        Expected: All defaults match specification
        
        Troubleshooting:
        - Wrong default → Check Field(default=...) in schema
        """
        config = AIModelConfig()
        
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0
    
    def test_valid_custom_values(self):
        """
        Test: Can set valid custom values
        Input: AIModelConfig with custom parameters
        Expected: Values stored correctly
        """
        config = AIModelConfig(
            temperature=0.5,
            max_tokens=2000,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.3
        )
        
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.5
        assert config.presence_penalty == 0.3
    
    def test_temperature_min_boundary(self):
        """
        Test: Temperature minimum boundary (0.0)
        Input: temperature=0.0
        Expected: Valid
        """
        config = AIModelConfig(temperature=0.0)
        assert config.temperature == 0.0
    
    def test_temperature_max_boundary(self):
        """
        Test: Temperature maximum boundary (2.0)
        Input: temperature=2.0
        Expected: Valid
        """
        config = AIModelConfig(temperature=2.0)
        assert config.temperature == 2.0
    
    def test_temperature_below_min(self):
        """
        Test: Temperature below minimum fails
        Input: temperature=-0.1
        Expected: ValidationError
        
        Troubleshooting:
        - No error raised → Check Field(ge=0.0) constraint
        """
        with pytest.raises(ValidationError) as exc_info:
            AIModelConfig(temperature=-0.1)
        
        assert "temperature" in str(exc_info.value).lower()
    
    def test_temperature_above_max(self):
        """
        Test: Temperature above maximum fails
        Input: temperature=2.1
        Expected: ValidationError
        """
        with pytest.raises(ValidationError) as exc_info:
            AIModelConfig(temperature=2.1)
        
        assert "temperature" in str(exc_info.value).lower()
    
    def test_max_tokens_positive(self):
        """
        Test: max_tokens must be positive
        Input: max_tokens=1
        Expected: Valid (minimum value)
        """
        config = AIModelConfig(max_tokens=1)
        assert config.max_tokens == 1
    
    def test_max_tokens_zero_invalid(self):
        """
        Test: max_tokens cannot be zero
        Input: max_tokens=0
        Expected: ValidationError
        """
        with pytest.raises(ValidationError):
            AIModelConfig(max_tokens=0)
    
    def test_max_tokens_negative_invalid(self):
        """
        Test: max_tokens cannot be negative
        Input: max_tokens=-1
        Expected: ValidationError
        """
        with pytest.raises(ValidationError):
            AIModelConfig(max_tokens=-1)
    
    def test_top_p_boundaries(self):
        """
        Test: top_p valid range [0.0, 1.0]
        Input: top_p=0.0, 0.5, 1.0
        Expected: All valid
        """
        config1 = AIModelConfig(top_p=0.0)
        config2 = AIModelConfig(top_p=0.5)
        config3 = AIModelConfig(top_p=1.0)
        
        assert config1.top_p == 0.0
        assert config2.top_p == 0.5
        assert config3.top_p == 1.0
    
    def test_top_p_out_of_range(self):
        """
        Test: top_p outside [0.0, 1.0] fails
        Input: top_p=1.5
        Expected: ValidationError
        """
        with pytest.raises(ValidationError):
            AIModelConfig(top_p=1.5)
    
    def test_frequency_penalty_boundaries(self):
        """
        Test: frequency_penalty range [-2.0, 2.0]
        Input: Various values in range
        Expected: All valid
        """
        config1 = AIModelConfig(frequency_penalty=-2.0)
        config2 = AIModelConfig(frequency_penalty=0.0)
        config3 = AIModelConfig(frequency_penalty=2.0)
        
        assert config1.frequency_penalty == -2.0
        assert config2.frequency_penalty == 0.0
        assert config3.frequency_penalty == 2.0
    
    def test_presence_penalty_boundaries(self):
        """
        Test: presence_penalty range [-2.0, 2.0]
        Input: Various values in range
        Expected: All valid
        """
        config1 = AIModelConfig(presence_penalty=-2.0)
        config2 = AIModelConfig(presence_penalty=0.0)
        config3 = AIModelConfig(presence_penalty=2.0)
        
        assert config1.presence_penalty == -2.0
        assert config2.presence_penalty == 0.0
        assert config3.presence_penalty == 2.0


class TestAIRequest:
    """
    Test suite for AIRequest Pydantic model.
    
    What it tests:
    - Required fields validation
    - Optional fields behavior
    - Field type validation
    - Default ai_config creation
    - instruction_prompt min_length constraint
    
    Troubleshooting:
    - ValidationError on required field → Check all required fields provided
    - Wrong type → Verify field type annotations
    - Missing ai_config → Check Field(default_factory=AIModelConfig)
    """
    
    def test_create_minimal_request(self):
        """
        Test: Create request with minimal required fields
        Input: provider, instruction_prompt, input_data only
        Expected: Request created with default ai_config
        
        Troubleshooting:
        - Missing field error → Check which fields are required
        """
        request = AIRequest(
            provider=AIProviderType.GEMINI,
            instruction_prompt="Analyze this data",
            input_data={"values": [1, 2, 3]}
        )
        
        assert request.provider == AIProviderType.GEMINI
        assert request.instruction_prompt == "Analyze this data"
        assert request.input_data == {"values": [1, 2, 3]}
        assert isinstance(request.ai_config, AIModelConfig)
        assert request.model_name is None
    
    def test_create_full_request(self):
        """
        Test: Create request with all fields
        Input: All fields including optional ones
        Expected: All fields stored correctly
        """
        config = AIModelConfig(temperature=0.8)
        
        request = AIRequest(
            provider=AIProviderType.OPENAI,
            instruction_prompt="Custom analysis",
            input_data={"data": "test"},
            ai_config=config,
            model_name="gpt-4"
        )
        
        assert request.provider == AIProviderType.OPENAI
        assert request.ai_config.temperature == 0.8
        assert request.model_name == "gpt-4"
    
    def test_empty_instruction_prompt_fails(self):
        """
        Test: Empty instruction_prompt fails validation
        Input: instruction_prompt=""
        Expected: ValidationError
        
        Troubleshooting:
        - No error → Check Field(min_length=1) constraint
        """
        with pytest.raises(ValidationError) as exc_info:
            AIRequest(
                provider=AIProviderType.GEMINI,
                instruction_prompt="",
                input_data={"test": "data"}
            )
        
        assert "instruction_prompt" in str(exc_info.value).lower()
    
    def test_missing_required_provider(self):
        """
        Test: Missing provider field fails
        Input: No provider specified
        Expected: ValidationError
        """
        with pytest.raises(ValidationError):
            AIRequest(
                instruction_prompt="Test",
                input_data={"test": "data"}
            )
    
    def test_missing_required_instruction_prompt(self):
        """
        Test: Missing instruction_prompt fails
        Input: No instruction_prompt specified
        Expected: ValidationError
        """
        with pytest.raises(ValidationError):
            AIRequest(
                provider=AIProviderType.GEMINI,
                input_data={"test": "data"}
            )
    
    def test_missing_required_input_data(self):
        """
        Test: Missing input_data fails
        Input: No input_data specified
        Expected: ValidationError
        """
        with pytest.raises(ValidationError):
            AIRequest(
                provider=AIProviderType.GEMINI,
                instruction_prompt="Test"
            )
    
    def test_input_data_can_be_complex(self):
        """
        Test: input_data accepts complex structures
        Input: Nested dict with lists and various types
        Expected: Stored correctly
        """
        complex_data = {
            "numbers": [1, 2, 3, 4, 5],
            "text": "sample",
            "nested": {
                "key": "value",
                "list": ["a", "b", "c"]
            },
            "boolean": True
        }
        
        request = AIRequest(
            provider=AIProviderType.CLAUDE,
            instruction_prompt="Analyze",
            input_data=complex_data
        )
        
        assert request.input_data == complex_data
        assert request.input_data["nested"]["key"] == "value"


class TestAIResponse:
    """
    Test suite for AIResponse Pydantic model.
    
    What it tests:
    - Required fields
    - Optional raw_response field
    - Usage dict structure
    - Field types
    
    Troubleshooting:
    - Missing field → Check all required fields are provided
    - Type error → Verify field type annotations
    """
    
    def test_create_minimal_response(self):
        """
        Test: Create response with required fields
        Input: provider, content, usage, model
        Expected: Response created, raw_response is None
        """
        response = AIResponse(
            provider=AIProviderType.GEMINI,
            content="Analysis result",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            model="gemini-pro"
        )
        
        assert response.provider == AIProviderType.GEMINI
        assert response.content == "Analysis result"
        assert response.usage["total_tokens"] == 30
        assert response.model == "gemini-pro"
        assert response.raw_response is None
    
    def test_create_response_with_raw(self):
        """
        Test: Create response with raw_response
        Input: All fields including raw_response
        Expected: raw_response stored
        """
        raw_data = {"api_version": "1.0", "request_id": "123"}
        
        response = AIResponse(
            provider=AIProviderType.OPENAI,
            content="Result",
            usage={"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
            model="gpt-4",
            raw_response=raw_data
        )
        
        assert response.raw_response == raw_data
        assert response.raw_response["request_id"] == "123"
    
    def test_usage_dict_structure(self):
        """
        Test: Usage dict can contain various metrics
        Input: Usage with custom keys
        Expected: All keys preserved
        """
        usage = {
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "total_tokens": 300,
            "custom_metric": 42
        }
        
        response = AIResponse(
            provider=AIProviderType.CLAUDE,
            content="Response",
            usage=usage,
            model="claude-3"
        )
        
        assert response.usage["custom_metric"] == 42


class TestAIError:
    """
    Test suite for AIError Pydantic model.
    
    What it tests:
    - Required fields
    - Optional details field
    - Field types
    
    Troubleshooting:
    - Missing field → Check required vs optional fields
    """
    
    def test_create_minimal_error(self):
        """
        Test: Create error with required fields
        Input: provider, error_type, message
        Expected: Error created, details is None
        """
        error = AIError(
            provider=AIProviderType.GEMINI,
            error_type="quota_exceeded",
            message="API quota exceeded"
        )
        
        assert error.provider == AIProviderType.GEMINI
        assert error.error_type == "quota_exceeded"
        assert error.message == "API quota exceeded"
        assert error.details is None
    
    def test_create_error_with_details(self):
        """
        Test: Create error with details dict
        Input: All fields including details
        Expected: Details stored correctly
        """
        details = {
            "retry_after": 60,
            "original_error": "429 Too Many Requests"
        }
        
        error = AIError(
            provider=AIProviderType.OPENAI,
            error_type="rate_limit_exceeded",
            message="Rate limit hit",
            details=details
        )
        
        assert error.details == details
        assert error.details["retry_after"] == 60


class TestSchemaSerializationDeserialization:
    """
    Test suite for JSON serialization/deserialization.
    
    What it tests:
    - model_dump() output
    - model_dump_json() output
    - Parsing from dict/JSON
    
    Troubleshooting:
    - Serialization error → Check all fields are JSON-serializable
    - Parsing error → Verify field names and types match
    """
    
    def test_request_to_dict(self):
        """
        Test: Serialize AIRequest to dict
        Input: AIRequest instance
        Expected: Dict with all fields
        """
        request = AIRequest(
            provider=AIProviderType.GEMINI,
            instruction_prompt="Test",
            input_data={"key": "value"}
        )
        
        data = request.model_dump()
        
        assert data["provider"] == "gemini"
        assert data["instruction_prompt"] == "Test"
        assert data["input_data"]["key"] == "value"
        assert "ai_config" in data
    
    def test_response_to_dict(self):
        """
        Test: Serialize AIResponse to dict
        Input: AIResponse instance
        Expected: Dict with all fields
        """
        response = AIResponse(
            provider=AIProviderType.OPENAI,
            content="Result",
            usage={"total_tokens": 100},
            model="gpt-4"
        )
        
        data = response.model_dump()
        
        assert data["provider"] == "openai"
        assert data["content"] == "Result"
        assert data["model"] == "gpt-4"
    
    def test_parse_request_from_dict(self):
        """
        Test: Parse AIRequest from dict
        Input: Dict with request data
        Expected: Valid AIRequest instance
        """
        data = {
            "provider": "claude",
            "instruction_prompt": "Analyze this",
            "input_data": {"numbers": [1, 2, 3]},
            "ai_config": {"temperature": 0.5}
        }
        
        request = AIRequest(**data)
        
        assert request.provider == AIProviderType.CLAUDE
        assert request.ai_config.temperature == 0.5


# Run tests with: pytest tests/test_schemas.py -v --tb=short
