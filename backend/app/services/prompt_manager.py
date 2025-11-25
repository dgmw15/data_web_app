"""
Prompt Manager
Manages instruction prompt templates for AI operations.

SOLID Principles Applied:
    - SRP: Only manages prompt templates, no other responsibilities
    - OCP: New templates can be added without modifying existing code
    - ISP: Minimal interface with focused methods
    - DIP: Works with generic types (Dict, str), not concrete implementations
"""
from typing import Dict, Any
from enum import Enum


class PromptTemplate(str, Enum):
    """
    Pre-defined prompt templates for common AI tasks.
    
    Attributes:
        DATA_ANALYSIS: Analyze and summarize data
        DATA_CLEANING: Identify data quality issues
        DATA_TRANSFORMATION: Transform data format/structure
        CATEGORIZATION: Categorize items into groups
        SENTIMENT_ANALYSIS: Analyze sentiment from text
        CUSTOM: User-defined custom prompt
    
    SOLID Principle Applied:
        - OCP: New templates can be added without breaking existing code
    """
    DATA_ANALYSIS = "data_analysis"
    DATA_CLEANING = "data_cleaning"
    DATA_TRANSFORMATION = "data_transformation"
    CATEGORIZATION = "categorization"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CUSTOM = "custom"


class PromptManager:
    """
    Manages and formats instruction prompts for AI operations.
    
    Provides pre-built templates and custom prompt support.
    
    SOLID Principles Applied:
        - SRP: Only handles prompt management and formatting
        - OCP: Template dictionary allows extension without modification
        - ISP: Provides only necessary methods
    """
    
    # Prompt Templates Dictionary
    TEMPLATES: Dict[str, str] = {
        PromptTemplate.DATA_ANALYSIS: """
You are a data analyst. Analyze the provided dataset and provide:
1. Key statistics and patterns
2. Notable trends or anomalies
3. Actionable insights
4. Data quality observations

Format your response in a clear, structured manner.
""",
        
        PromptTemplate.DATA_CLEANING: """
You are a data quality expert. Review the provided dataset and identify:
1. Missing or null values
2. Data type inconsistencies
3. Outliers or anomalies
4. Duplicate records
5. Formatting issues

Provide specific recommendations for cleaning each issue.
""",
        
        PromptTemplate.DATA_TRANSFORMATION: """
You are a data engineer. Transform the provided data according to the requirements:
1. Apply the specified transformations
2. Ensure data integrity is maintained
3. Validate the output format
4. Provide transformation summary

Return the transformed data in the requested format.
""",
        
        PromptTemplate.CATEGORIZATION: """
You are a classification expert. Categorize the provided items:
1. Analyze each item's characteristics
2. Assign appropriate categories
3. Provide confidence scores if applicable
4. Explain the categorization logic

Return results in a structured format with categories clearly labeled.
""",
        
        PromptTemplate.SENTIMENT_ANALYSIS: """
You are a sentiment analysis expert. Analyze the provided text data:
1. Determine overall sentiment (positive/negative/neutral)
2. Identify key emotional indicators
3. Provide sentiment scores
4. Highlight significant phrases

Return results in a structured format with clear sentiment labels.
""",
    }
    
    @classmethod
    def get_prompt(cls, template: PromptTemplate | str, custom_instructions: str = "") -> str:
        """
        Get a prompt template by name or return custom prompt.
        
        Args:
            template (PromptTemplate | str): Template name or custom prompt
            custom_instructions (str): Additional instructions to append
        
        Returns:
            str: Formatted instruction prompt
        
        Source/Caller:
            - Called by: AIService.process_ai_request
            - Input Source: API route handler
        
        SOLID Principle Applied:
            - SRP: Only retrieves and formats prompts
            - OCP: New templates added via TEMPLATES dict
        """
        if template == PromptTemplate.CUSTOM:
            return custom_instructions
        
        base_prompt = cls.TEMPLATES.get(template, "")
        
        if custom_instructions:
            return f"{base_prompt}\n\nAdditional Instructions:\n{custom_instructions}"
        
        return base_prompt
    
    @classmethod
    def list_templates(cls) -> Dict[str, str]:
        """
        Get all available prompt templates.
        
        Returns:
            Dict[str, str]: Dictionary of template names and descriptions
        
        Source/Caller:
            - Called by: API documentation endpoints
        
        SOLID Principle Applied:
            - SRP: Only provides template information
            - OCP: Dynamically reads from enum
        """
        return {
            PromptTemplate.DATA_ANALYSIS: "Analyze and summarize datasets",
            PromptTemplate.DATA_CLEANING: "Identify data quality issues",
            PromptTemplate.DATA_TRANSFORMATION: "Transform data structure",
            PromptTemplate.CATEGORIZATION: "Categorize items into groups",
            PromptTemplate.SENTIMENT_ANALYSIS: "Analyze text sentiment",
            PromptTemplate.CUSTOM: "Use custom instructions",
        }
