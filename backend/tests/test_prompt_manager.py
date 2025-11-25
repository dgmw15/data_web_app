"""
Prompt Manager Tests
Tests for prompt template management and formatting.

Test Coverage:
- Template retrieval
- Custom prompt handling
- Template listing
- Additional instructions appending
- Template existence validation

Troubleshooting Guide:
- Template not found → Check TEMPLATES dictionary in PromptManager
- Wrong template content → Verify template text matches expected keywords
- Custom prompt issues → Check CUSTOM template handling
"""
import pytest
from app.services.prompt_manager import PromptManager, PromptTemplate


class TestPromptTemplateEnum:
    """
    Test suite for PromptTemplate enum.
    
    What it tests:
    - All template types are defined
    - Template values are correct strings
    - Enum can be used for comparisons
    
    Troubleshooting:
    - Missing template → Add to PromptTemplate enum
    """
    
    def test_all_templates_defined(self):
        """
        Test: All expected template types exist
        Input: Access each template type
        Expected: No AttributeError
        """
        assert PromptTemplate.DATA_ANALYSIS
        assert PromptTemplate.DATA_CLEANING
        assert PromptTemplate.DATA_TRANSFORMATION
        assert PromptTemplate.CATEGORIZATION
        assert PromptTemplate.SENTIMENT_ANALYSIS
        assert PromptTemplate.CUSTOM
    
    def test_template_string_values(self):
        """
        Test: Template enum values are correct strings
        Input: Template enum members
        Expected: String values match expected format
        """
        assert PromptTemplate.DATA_ANALYSIS.value == "data_analysis"
        assert PromptTemplate.DATA_CLEANING.value == "data_cleaning"
        assert PromptTemplate.CUSTOM.value == "custom"


class TestGetPrompt:
    """
    Test suite for PromptManager.get_prompt() method.
    
    What it tests:
    - Retrieving predefined templates
    - Custom prompt handling
    - Adding additional instructions
    - Empty custom instructions
    - Template content validation
    
    Troubleshooting:
    - Empty prompt returned → Check template exists in TEMPLATES dict
    - Wrong template → Verify template name/key
    - Additional instructions not appended → Check string concatenation
    """
    
    def test_get_data_analysis_template(self):
        """
        Test: Retrieve DATA_ANALYSIS template
        Input: PromptTemplate.DATA_ANALYSIS
        Expected: Prompt contains data analyst keywords
        
        Troubleshooting:
        - Empty prompt → Check TEMPLATES[DATA_ANALYSIS] exists
        - Wrong content → Verify template text
        """
        prompt = PromptManager.get_prompt(PromptTemplate.DATA_ANALYSIS)
        
        assert len(prompt) > 0
        assert "data analyst" in prompt.lower()
        assert "analyze" in prompt.lower()
        assert "insights" in prompt.lower()
    
    def test_get_data_cleaning_template(self):
        """
        Test: Retrieve DATA_CLEANING template
        Input: PromptTemplate.DATA_CLEANING
        Expected: Prompt contains data quality keywords
        """
        prompt = PromptManager.get_prompt(PromptTemplate.DATA_CLEANING)
        
        assert len(prompt) > 0
        assert "data quality" in prompt.lower()
        assert "missing" in prompt.lower() or "null" in prompt.lower()
    
    def test_get_data_transformation_template(self):
        """
        Test: Retrieve DATA_TRANSFORMATION template
        Input: PromptTemplate.DATA_TRANSFORMATION
        Expected: Prompt contains transformation keywords
        """
        prompt = PromptManager.get_prompt(PromptTemplate.DATA_TRANSFORMATION)
        
        assert len(prompt) > 0
        assert "transform" in prompt.lower()
        assert "data engineer" in prompt.lower()
    
    def test_get_categorization_template(self):
        """
        Test: Retrieve CATEGORIZATION template
        Input: PromptTemplate.CATEGORIZATION
        Expected: Prompt contains categorization keywords
        """
        prompt = PromptManager.get_prompt(PromptTemplate.CATEGORIZATION)
        
        assert len(prompt) > 0
        assert "categor" in prompt.lower()  # matches categorize, categorization
        assert "classification" in prompt.lower() or "classify" in prompt.lower()
    
    def test_get_sentiment_analysis_template(self):
        """
        Test: Retrieve SENTIMENT_ANALYSIS template
        Input: PromptTemplate.SENTIMENT_ANALYSIS
        Expected: Prompt contains sentiment keywords
        """
        prompt = PromptManager.get_prompt(PromptTemplate.SENTIMENT_ANALYSIS)
        
        assert len(prompt) > 0
        assert "sentiment" in prompt.lower()
        assert "positive" in prompt.lower() or "negative" in prompt.lower()
    
    def test_get_custom_prompt(self):
        """
        Test: Handle CUSTOM template with custom instructions
        Input: PromptTemplate.CUSTOM, "Analyze this carefully"
        Expected: Returns exactly the custom instructions
        
        Troubleshooting:
        - Base template returned → Check CUSTOM handling in get_prompt()
        - Empty result → Verify custom_instructions parameter
        """
        custom_text = "Analyze this data with focus on outliers and trends"
        prompt = PromptManager.get_prompt(PromptTemplate.CUSTOM, custom_text)
        
        assert prompt == custom_text
    
    def test_get_template_with_additional_instructions(self):
        """
        Test: Append additional instructions to template
        Input: Template + custom_instructions
        Expected: Both base template and additions present
        
        Troubleshooting:
        - Only base template → Check string concatenation logic
        - Wrong format → Verify newline separator
        """
        additional = "Focus specifically on anomalies"
        prompt = PromptManager.get_prompt(
            PromptTemplate.DATA_CLEANING,
            additional
        )
        
        assert "data quality" in prompt.lower()
        assert additional in prompt
        assert "Additional Instructions" in prompt
    
    def test_get_template_with_empty_additional_instructions(self):
        """
        Test: Template with empty additional instructions
        Input: Template + ""
        Expected: Just base template, no extra text
        """
        prompt = PromptManager.get_prompt(PromptTemplate.DATA_ANALYSIS, "")
        
        assert "data analyst" in prompt.lower()
        assert "Additional Instructions" not in prompt
    
    def test_template_as_string_key(self):
        """
        Test: Use string value instead of enum
        Input: "data_analysis" as string
        Expected: Same result as enum
        
        Troubleshooting:
        - Different result → Check if get_prompt accepts both str and enum
        """
        prompt1 = PromptManager.get_prompt(PromptTemplate.DATA_ANALYSIS)
        prompt2 = PromptManager.get_prompt("data_analysis")
        
        assert prompt1 == prompt2


class TestListTemplates:
    """
    Test suite for PromptManager.list_templates() method.
    
    What it tests:
    - All templates are listed
    - Descriptions are provided
    - Return format is correct
    
    Troubleshooting:
    - Missing templates → Check list_templates() includes all enums
    - Wrong descriptions → Verify description text
    """
    
    def test_list_all_templates(self):
        """
        Test: List all available templates
        Input: None
        Expected: Dict with all template names and descriptions
        
        Troubleshooting:
        - Missing template → Add to list_templates() return dict
        - Wrong count → Verify all PromptTemplate enum members included
        """
        templates = PromptManager.list_templates()
        
        assert isinstance(templates, dict)
        assert len(templates) >= 6  # At least 6 templates
        
        # Check all expected templates are present
        assert PromptTemplate.DATA_ANALYSIS in templates
        assert PromptTemplate.DATA_CLEANING in templates
        assert PromptTemplate.DATA_TRANSFORMATION in templates
        assert PromptTemplate.CATEGORIZATION in templates
        assert PromptTemplate.SENTIMENT_ANALYSIS in templates
        assert PromptTemplate.CUSTOM in templates
    
    def test_template_descriptions_are_strings(self):
        """
        Test: All template descriptions are non-empty strings
        Input: None
        Expected: Each value is a string with content
        """
        templates = PromptManager.list_templates()
        
        for template_name, description in templates.items():
            assert isinstance(description, str)
            assert len(description) > 0
    
    def test_specific_template_descriptions(self):
        """
        Test: Verify specific template descriptions
        Input: None
        Expected: Descriptions match template purposes
        
        Troubleshooting:
        - Wrong description → Update list_templates() description text
        """
        templates = PromptManager.list_templates()
        
        assert "analyze" in templates[PromptTemplate.DATA_ANALYSIS].lower()
        assert "clean" in templates[PromptTemplate.DATA_CLEANING].lower() or \
               "quality" in templates[PromptTemplate.DATA_CLEANING].lower()
        assert "transform" in templates[PromptTemplate.DATA_TRANSFORMATION].lower()
        assert "categor" in templates[PromptTemplate.CATEGORIZATION].lower()
        assert "sentiment" in templates[PromptTemplate.SENTIMENT_ANALYSIS].lower()
        assert "custom" in templates[PromptTemplate.CUSTOM].lower()


class TestTemplateContent:
    """
    Test suite for template content quality.
    
    What it tests:
    - Templates are substantial (not too short)
    - Templates contain instructions
    - Templates are well-formatted
    
    Troubleshooting:
    - Template too short → Add more detailed instructions
    - Poor formatting → Check whitespace and structure
    """
    
    def test_templates_have_sufficient_length(self):
        """
        Test: Templates are substantial (>50 characters)
        Input: Each template
        Expected: All templates have meaningful content
        
        Troubleshooting:
        - Short template → Expand template with more details
        """
        for template in [
            PromptTemplate.DATA_ANALYSIS,
            PromptTemplate.DATA_CLEANING,
            PromptTemplate.DATA_TRANSFORMATION,
            PromptTemplate.CATEGORIZATION,
            PromptTemplate.SENTIMENT_ANALYSIS
        ]:
            prompt = PromptManager.get_prompt(template)
            assert len(prompt) > 50, f"{template} template is too short"
    
    def test_templates_contain_numbered_lists(self):
        """
        Test: Templates use numbered lists for structure
        Input: Each template
        Expected: Contains numbered items (1., 2., etc.)
        """
        for template in [
            PromptTemplate.DATA_ANALYSIS,
            PromptTemplate.DATA_CLEANING,
            PromptTemplate.CATEGORIZATION
        ]:
            prompt = PromptManager.get_prompt(template)
            # Should have numbered lists
            assert "1." in prompt or "1)" in prompt
    
    def test_templates_are_role_based(self):
        """
        Test: Templates start with role definition
        Input: Each template
        Expected: Contains "You are a..." pattern
        """
        templates_to_check = [
            PromptTemplate.DATA_ANALYSIS,
            PromptTemplate.DATA_CLEANING,
            PromptTemplate.DATA_TRANSFORMATION
        ]
        
        for template in templates_to_check:
            prompt = PromptManager.get_prompt(template)
            assert "you are" in prompt.lower(), \
                f"{template} should define AI role"


class TestPromptManagerClassMethods:
    """
    Test suite for PromptManager class structure.
    
    What it tests:
    - Methods are class methods
    - No instance required
    - TEMPLATES is class attribute
    
    Troubleshooting:
    - Method call fails → Check @classmethod decorator
    """
    
    def test_get_prompt_is_classmethod(self):
        """
        Test: get_prompt can be called without instance
        Input: Call on class directly
        Expected: Works without instantiation
        """
        # Should work without creating instance
        prompt = PromptManager.get_prompt(PromptTemplate.DATA_ANALYSIS)
        assert len(prompt) > 0
    
    def test_list_templates_is_classmethod(self):
        """
        Test: list_templates can be called without instance
        Input: Call on class directly
        Expected: Works without instantiation
        """
        # Should work without creating instance
        templates = PromptManager.list_templates()
        assert len(templates) > 0
    
    def test_templates_dict_exists(self):
        """
        Test: TEMPLATES class attribute exists
        Input: Access PromptManager.TEMPLATES
        Expected: Dict with template mappings
        """
        assert hasattr(PromptManager, 'TEMPLATES')
        assert isinstance(PromptManager.TEMPLATES, dict)
        assert len(PromptManager.TEMPLATES) > 0


class TestEdgeCases:
    """
    Test suite for edge cases and error scenarios.
    
    What it tests:
    - Invalid template names
    - None values
    - Empty strings
    - Special characters
    
    Troubleshooting:
    - Unexpected behavior → Add validation in get_prompt()
    """
    
    def test_invalid_template_name(self):
        """
        Test: Handle invalid template name gracefully
        Input: Non-existent template name
        Expected: Returns empty string or handles gracefully
        
        Troubleshooting:
        - Crashes → Add error handling in get_prompt()
        """
        prompt = PromptManager.get_prompt("invalid_template_name")
        # Should return empty string or handle gracefully
        assert isinstance(prompt, str)
    
    def test_custom_prompt_with_special_characters(self):
        """
        Test: Custom prompt with special characters
        Input: CUSTOM template with special chars
        Expected: Returns exactly what was provided
        """
        custom = "Analyze {data} with $pecial ch@rs & symbols!"
        prompt = PromptManager.get_prompt(PromptTemplate.CUSTOM, custom)
        
        assert prompt == custom
    
    def test_very_long_custom_prompt(self):
        """
        Test: Very long custom prompt
        Input: CUSTOM with 1000+ character string
        Expected: Handles without truncation
        """
        custom = "Analyze this data. " * 100  # Long string
        prompt = PromptManager.get_prompt(PromptTemplate.CUSTOM, custom)
        
        assert len(prompt) == len(custom)
        assert prompt == custom


# Run tests with: pytest tests/test_prompt_manager.py -v --tb=short
