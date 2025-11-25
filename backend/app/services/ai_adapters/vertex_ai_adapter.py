"""
Google Vertex AI Adapter
Implements the Vertex AI provider for Google Cloud Platform.

SOLID Principles Applied:
    - SRP: Only handles Vertex AI API communication
    - OCP: Extends BaseAIAdapter without modifying it
    - LSP: Fully substitutable for BaseAIAdapter
    - ISP: Implements only required call_ai method
    - DIP: Depends on BaseAIAdapter abstraction
"""
import os
from typing import Dict, Any
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
import vertexai

from app.core.config import settings
from app.schemas.ai_schemas import AIModelConfig, AIResponse, AIProviderType
from app.services.ai_adapters.base_adapter import BaseAIAdapter, AIAdapterError


class VertexAIAdapter(BaseAIAdapter):
    """
    Adapter for Google Vertex AI (GCP).
    
    Supports Gemini and other foundation models through Vertex AI.
    Requires Google Cloud project setup and authentication.
    
    Attributes:
        DEFAULT_MODEL (str): Default Vertex AI model name
        _initialized (bool): Track if Vertex AI SDK has been initialized
    
    SOLID Principle Applied:
        - SRP: Only responsible for Vertex AI integration
    """
    
    DEFAULT_MODEL = "gemini-pro"
    _initialized = False
    
    def __init__(self):
        """
        Initialize Vertex AI adapter with GCP credentials.
        
        Raises:
            AIAdapterError: If configuration is invalid
        
        Source/Caller:
            - Called by: AIService._get_adapter factory method
        
        SOLID Principle Applied:
            - SRP: Only handles initialization
        """
        if not VertexAIAdapter._initialized:
            self._initialize_vertex_ai()
    
    def _initialize_vertex_ai(self):
        """
        Initialize Vertex AI SDK with project and location.
        
        Sets up authentication using service account credentials if provided,
        otherwise falls back to Application Default Credentials (ADC).
        
        Raises:
            AIAdapterError: If project ID is not configured
        
        Source/Caller:
            - Called by: __init__
        
        SOLID Principle Applied:
            - SRP: Only handles SDK initialization
        """
        if not settings.vertex_ai_project_id:
            raise AIAdapterError("Vertex AI project ID not configured")
        
        # Set credentials path if provided
        if settings.vertex_ai_credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.vertex_ai_credentials_path
        
        try:
            # Initialize Vertex AI
            vertexai.init(
                project=settings.vertex_ai_project_id,
                location=settings.vertex_ai_location
            )
            VertexAIAdapter._initialized = True
        except Exception as e:
            raise AIAdapterError(f"Failed to initialize Vertex AI: {str(e)}")
    
    async def call_ai(
        self,
        instruction_prompt: str,
        input_data: Dict[str, Any],
        model_config: AIModelConfig,
        model_name: str | None = None
    ) -> AIResponse:
        """
        Call Google Vertex AI with given parameters.
        
        Args:
            instruction_prompt (str): System/instruction prompt
            input_data (Dict[str, Any]): JSON-formatted input data
            model_config (AIModelConfig): Model configuration parameters
            model_name (str | None): Optional specific model name
        
        Returns:
            AIResponse: Standardized AI response
        
        Raises:
            AIAdapterError: If API call fails or credentials are invalid
        
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
            
            model = GenerativeModel(model_name or self.DEFAULT_MODEL)
            
            generation_config = GenerationConfig(
                temperature=model_config.temperature,
                max_output_tokens=model_config.max_tokens,
                top_p=model_config.top_p,
            )
            
            message = self._format_input_message(instruction_prompt, input_data)
            
            # Vertex AI generate_content is synchronous, but we wrap it for consistency
            response = model.generate_content(
                message,
                generation_config=generation_config
            )
            
            # Extract usage information
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }
            
            return AIResponse(
                provider=AIProviderType.VERTEX_AI,
                content=response.text,
                usage=usage,
                model=model_name or self.DEFAULT_MODEL,
                raw_response=None
            )
        except AIAdapterError:
            raise
        except Exception as e:
            raise AIAdapterError(f"Vertex AI API call failed: {str(e)}")
