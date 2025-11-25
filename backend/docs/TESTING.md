# Testing Documentation

## Overview

This document provides comprehensive testing information for the DataCrunch API backend. All tests follow SOLID principles and include detailed troubleshooting guidance.

## Running Tests

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Run Specific Test Files
```bash
# Error handling tests
pytest tests/test_error_handling.py -v

# Schema tests
pytest tests/test_schemas.py -v

# Prompt manager tests
pytest tests/test_prompt_manager.py -v

# AI service tests
pytest tests/test_ai_service.py -v
```

### Run with Coverage
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Run Specific Test Class or Method
```bash
# Run specific class
pytest tests/test_error_handling.py::TestQuotaTracker -v

# Run specific test
pytest tests/test_schemas.py::TestAIModelConfig::test_temperature_validation -v
```

## Test Structure

### Test File Organization
```
tests/
├── test_error_handling.py     # Error system and quota tracking
├── test_schemas.py             # Pydantic model validation
├── test_prompt_manager.py      # Template management
└── test_ai_service.py          # Service orchestration
```

### Test Naming Convention
- **Test Files**: `test_<module_name>.py`
- **Test Classes**: `Test<ComponentName>`
- **Test Methods**: `test_<what_is_being_tested>`

Example:
```python
class TestAIServiceError:
    def test_error_creation_with_all_fields(self):
        """
        Test: <Brief description>
        Input: <What goes in>
        Expected: <What should happen>
        
        Troubleshooting:
        - <Common issue> → <Solution>
        """
```

## Test Coverage by Module

### 1. Error Handling (`test_error_handling.py`)

**What it tests:**
- ✅ AIServiceError creation and serialization (5 tests)
- ✅ Specialized error types (6 tests)
- ✅ Error conversion from provider errors (5 tests)
- ✅ QuotaTracker singleton and operations (8 tests)
- ✅ Input validation (6 tests)
- ✅ AIService error integration (2 tests)

**Total: 32 tests**

**Key Test Cases:**
1. **Error Creation**: Validates all error attributes are stored correctly
2. **Error Serialization**: Tests `to_dict()` for API responses
3. **Quota Tracking**: Ensures provider blocking/unblocking works
4. **Error Conversion**: Tests `handle_provider_error()` pattern matching
5. **Validation**: Tests field constraints (temperature, max_tokens, etc.)

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Singleton test fails | State persists between tests | Call `tracker.reset()` in `setup_method()` |
| Wrong error type detected | Keyword matching in conversion | Check `handle_provider_error()` patterns |
| Validation not triggered | Field constraints missing | Verify Pydantic `Field(ge=..., le=...)` |
| Provider not blocked | QuotaTracker not integrated | Check adapter calls `QuotaTracker()` |

### 2. Schemas (`test_schemas.py`)

**What it tests:**
- ✅ AIProviderType enum (3 tests)
- ✅ AIModelConfig validation (15 tests)
- ✅ AIRequest creation (8 tests)
- ✅ AIResponse structure (3 tests)
- ✅ AIError structure (2 tests)
- ✅ Serialization/Deserialization (3 tests)

**Total: 34 tests**

**Key Test Cases:**
1. **Default Values**: Validates all Pydantic defaults
2. **Boundary Testing**: Tests min/max constraints
3. **Required Fields**: Tests missing field validation
4. **Complex Data**: Tests nested structures in input_data
5. **Serialization**: Tests `model_dump()` and parsing

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| ValidationError on valid data | Constraint too strict | Adjust `Field(ge=..., le=...)` values |
| Missing field not caught | Field marked optional | Remove `Optional[]` or provide default |
| Temperature out of range | Input > 2.0 or < 0.0 | Check `Field(ge=0.0, le=2.0)` |
| Serialization fails | Non-JSON type in field | Convert to JSON-compatible type |

### 3. Prompt Manager (`test_prompt_manager.py`)

**What it tests:**
- ✅ PromptTemplate enum (2 tests)
- ✅ Template retrieval (9 tests)
- ✅ Template listing (3 tests)
- ✅ Template content quality (3 tests)
- ✅ Class method structure (3 tests)
- ✅ Edge cases (3 tests)

**Total: 23 tests**

**Key Test Cases:**
1. **Template Retrieval**: Gets predefined templates by enum
2. **Custom Prompts**: Handles CUSTOM template type
3. **Additional Instructions**: Appends extra instructions to templates
4. **Content Validation**: Verifies templates contain expected keywords
5. **Edge Cases**: Invalid names, special characters, long prompts

**Common Issues & Solutions:**

| Issue | Cause | Solution |
|-------|-------|----------|
| Empty prompt returned | Template not in TEMPLATES dict | Add template to `PromptManager.TEMPLATES` |
| Wrong template content | Template key mismatch | Verify enum value matches dict key |
| Additional instructions not appended | String concatenation missing | Check newline separator logic |
| Template too short | Insufficient detail | Expand template with more instructions |

### 4. AI Service (`test_ai_service.py`)

**What it tests:**
- ✅ Prompt manager integration (4 tests)
- ✅ Provider support (1 test)
- ✅ Adapter factory pattern (3 tests)
- ✅ Request processing (1 test, mocked)
- ✅ Schema validation (3 tests)

**Total: 12 tests**

**Key Test Cases:**
1. **Provider List**: All providers are registered
2. **Adapter Factory**: Correct adapter returned for each provider
3. **Request Flow**: End-to-end processing (mocked)
4. **Error Handling**: Invalid provider raises HTTPException

## Troubleshooting Guide

### Test Failures by Category

#### 1. Import Errors
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Cause**: AI provider SDK not installed  
**Solution**: 
```bash
pip install -r requirements.txt
```

#### 2. ValidationError in Tests
```
pydantic.ValidationError: 1 validation error for AIModelConfig
temperature: Input should be less than or equal to 2.0
```
**Cause**: Test providing invalid data  
**Solution**: Check field constraints match test inputs

#### 3. Assertion Failures
```
AssertionError: assert False is True
assert tracker.is_provider_blocked("gemini") is True
```
**Cause**: QuotaTracker state not set up correctly  
**Solution**: Call `tracker.block_provider()` before assertion

#### 4. Async Test Issues
```
RuntimeError: Task attached to a different loop
```
**Cause**: Async test not marked properly  
**Solution**: Add `@pytest.mark.asyncio` decorator

#### 5. Mock Not Called
```
AssertionError: Expected call not found
```
**Cause**: Mock not set up correctly  
**Solution**: Verify mock path matches actual import

### Environment-Specific Issues

#### macOS
- **Issue**: Tests fail with SSL errors
- **Solution**: Install certificates: `pip install certifi`

#### Windows
- **Issue**: Path separator issues in file tests
- **Solution**: Use `pathlib.Path` or `os.path.join()`

#### Linux
- **Issue**: Permission errors with test database
- **Solution**: Ensure test directory is writable

## Test Data Guidelines

### Valid Test Data Examples

**AIModelConfig:**
```python
# Valid
AIModelConfig(temperature=0.7, max_tokens=1000, top_p=0.9)

# Invalid
AIModelConfig(temperature=3.0)  # Out of range
AIModelConfig(max_tokens=0)     # Must be positive
```

**AIRequest:**
```python
# Valid
AIRequest(
    provider=AIProviderType.GEMINI,
    instruction_prompt="Analyze this data",
    input_data={"numbers": [1, 2, 3]}
)

# Invalid
AIRequest(
    provider=AIProviderType.GEMINI,
    instruction_prompt="",  # Min length is 1
    input_data={}
)
```

### Mock Response Examples

```python
mock_response = AIResponse(
    provider=AIProviderType.GEMINI,
    content="Test response",
    usage={
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    },
    model="gemini-pro"
)
```

## Input/Output Documentation

### test_error_handling.py

| Test | Input | Expected Output | Failure Indicates |
|------|-------|-----------------|-------------------|
| `test_error_creation_with_all_fields` | ErrorType, message, details | AIServiceError with all fields | Constructor not storing values |
| `test_quota_exceeded_error_defaults` | provider="openai" | QuotaExceededError, not retryable | Error type or flag wrong |
| `test_block_provider` | provider="gemini", duration=30 | is_blocked=True | Blocking mechanism broken |
| `test_convert_quota_exceeded_error` | Exception("Quota exceeded") | QuotaExceededError | Pattern matching failed |

### test_schemas.py

| Test | Input | Expected Output | Failure Indicates |
|------|-------|-----------------|-------------------|
| `test_default_values` | AIModelConfig() | temperature=0.7, max_tokens=1000 | Wrong defaults set |
| `test_temperature_below_min` | temperature=-0.1 | ValidationError | Constraint not enforced |
| `test_create_minimal_request` | provider, prompt, data | Valid AIRequest | Required fields wrong |
| `test_empty_instruction_prompt_fails` | instruction_prompt="" | ValidationError | min_length not enforced |

### test_prompt_manager.py

| Test | Input | Expected Output | Failure Indicates |
|------|-------|-----------------|-------------------|
| `test_get_data_analysis_template` | DATA_ANALYSIS | Prompt with "data analyst" | Template missing/wrong |
| `test_get_custom_prompt` | CUSTOM + "text" | Returns "text" exactly | Custom handling broken |
| `test_list_all_templates` | None | Dict with 6+ templates | Templates not registered |

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/ -v --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Setup/Teardown**: Use `setup_method()` and `teardown_method()`
3. **Mocking**: Mock external dependencies (API calls, databases)
4. **Assertions**: One logical assertion per test
5. **Documentation**: Every test has docstring with Input/Output/Troubleshooting
6. **Naming**: Descriptive names that explain what's being tested
7. **Coverage**: Aim for >80% code coverage

## Debugging Tests

### Enable Verbose Output
```bash
pytest tests/ -vv  # Extra verbose
pytest tests/ -s   # Show print statements
```

### Run Failed Tests Only
```bash
pytest tests/ --lf  # Last failed
pytest tests/ --ff  # Failed first
```

### Debug with PDB
```python
def test_something(self):
    import pdb; pdb.set_trace()  # Breakpoint
    assert something
```

### View Test Coverage
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## Summary

- **Total Tests**: 101 tests across 4 files
- **Coverage**: Error handling, schemas, services, utilities
- **Documentation**: Every test documents Input → Output → Troubleshooting
- **SOLID Compliant**: Tests follow same principles as code
- **Easy Debugging**: Clear failure messages and troubleshooting steps

## Quick Reference

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific file
pytest tests/test_error_handling.py -v

# Run specific test
pytest tests/test_schemas.py::TestAIModelConfig::test_default_values -v

# Debug mode
pytest tests/ -s --pdb

# Fast fail (stop on first failure)
pytest tests/ -x
```
