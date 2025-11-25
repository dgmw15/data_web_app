"""
AI Service Tests
Unit tests for AI service, adapters, and prompt manager.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.schemas.ai_schemas import (
    AIRequest,
    AIResponse,
    AIProviderType,
    AIModelConfig,
)
from app.services.ai_service import AIService
from app.services.prompt_manager import PromptManager, PromptTemplate


class TestPromptManager:
    """Test suite for PromptManager."""
    
    def test_get_predefined_template(self):
        """Test retrieving a predefined template."""
        prompt = PromptManager.get_prompt(PromptTemplate.DATA_ANALYSIS)
        assert "data analyst" in prompt.lower()
        assert len(prompt) > 0
    
    def test_get_custom_prompt(self):
        """Test custom prompt handling."""
        custom = "Analyze this data carefully"
        prompt = PromptManager.get_prompt(PromptTemplate.CUSTOM, custom)
        assert prompt == custom
    
    def test_get_template_with_additional_instructions(self):
        """Test template with additional instructions."""
        additional = "Focus on outliers"
        prompt = PromptManager.get_prompt(
            PromptTemplate.DATA_CLEANING,
            additional
        )
        assert "data quality" in prompt.lower()
        assert additional in prompt
    
    def test_list_templates(self):
        """Test listing all templates."""
        templates = PromptManager.list_templates()
        assert len(templates) > 0
        assert PromptTemplate.DATA_ANALYSIS in templates


class TestAIService:
    """Test suite for AIService."""
    
    def test_get_supported_providers(self):
        """Test getting list of supported providers."""
        providers = AIService.get_supported_providers()
        assert AIProviderType.GEMINI.value in providers
        assert AIProviderType.OPENAI.value in providers
        assert AIProviderType.CLAUDE.value in providers
        assert AIProviderType.DEEPSEEK.value in providers
        assert AIProviderType.VERTEX_AI.value in providers
    
    def test_get_adapter_valid_provider(self):
        """Test adapter factory with valid provider."""
        from app.services.ai_adapters import GeminiAdapter
        adapter = AIService._get_adapter(AIProviderType.GEMINI)
        assert isinstance(adapter, GeminiAdapter)
    
    def test_get_adapter_invalid_provider(self):
        """Test adapter factory with invalid provider."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            # Create a mock invalid provider
            AIService._get_adapter("invalid_provider")
    
    def test_get_adapter_vertex_ai(self):
        """Test adapter factory with Vertex AI provider."""
        from app.services.ai_adapters import VertexAIAdapter
        adapter = AIService._get_adapter(AIProviderType.VERTEX_AI)
        assert isinstance(adapter, VertexAIAdapter)
    
    @pytest.mark.asyncio
    async def test_process_ai_request_structure(self):
        """Test AI request processing structure (mocked)."""
        request = AIRequest(
            provider=AIProviderType.GEMINI,
            instruction_prompt="Test prompt",
            input_data={"test": "data"},
            ai_config=AIModelConfig()  # Updated to ai_config
        )
        
        # Mock the adapter
        mock_response = AIResponse(
            provider=AIProviderType.GEMINI,
            content="Test response",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            model="gemini-pro"
        )
        
        with patch.object(AIService, '_get_adapter') as mock_get_adapter:
            mock_adapter = Mock()
            mock_adapter.call_ai = AsyncMock(return_value=mock_response)
            mock_get_adapter.return_value = mock_adapter
            
            response = await AIService.process_ai_request(request)
            
            assert response.provider == AIProviderType.GEMINI
            assert response.content == "Test response"
            assert response.usage["total_tokens"] == 30


class TestAISchemas:
    """Test suite for AI schemas."""
    
    def test_ai_request_validation(self):
        """Test AIRequest validation."""
        request = AIRequest(
            provider=AIProviderType.OPENAI,
            instruction_prompt="Analyze this data",
            input_data={"numbers": [1, 2, 3, 4, 5]}
        )
        assert request.provider == AIProviderType.OPENAI
        assert request.input_data["numbers"] == [1, 2, 3, 4, 5]
    
    def test_model_config_defaults(self):
        """Test AIModelConfig default values."""
        config = AIModelConfig()
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.top_p == 1.0
    
    def test_model_config_validation(self):
        """Test AIModelConfig validation bounds."""
        # Valid config
        config = AIModelConfig(temperature=0.5, max_tokens=2000)
        assert config.temperature == 0.5
        
        # Temperature should be validated by Pydantic
        with pytest.raises(Exception):
            AIModelConfig(temperature=3.0)  # Out of range
