# Test Suite for HRM Decision System

## 📋 Overview

Comprehensive test suite covering unit tests, integration tests, functional tests, API tests, and performance tests.

## 🧪 Test Files

| File | Type | Description | Tests |
|------|------|-------------|-------|
| `test_phase1.py` | Unit | Component-level unit tests | 15+ tests |
| `test_system.py` | Integration | Full pipeline integration tests | End-to-end scenarios |
| `test_api.py` | API | REST API endpoint tests | 30+ tests |
| `test_functional.py` | Functional | Business logic and workflows | 40+ tests |
| `test_performance.py` | Performance | Response time and throughput | 10+ tests |

**Total: 95+ test cases**

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests
pytest -v

# Run specific test file
pytest test_phase1.py -v
pytest test_api.py -v
pytest test_functional.py -v
```

### Using Test Runner

```bash
# Run all tests
python run_tests.py all

# Run unit tests only
python run_tests.py unit

# Run API tests
python run_tests.py api

# Run functional tests
python run_tests.py functional

# Run with coverage
python run_tests.py coverage

# Quick smoke test
python run_tests.py quick
```

### PowerShell Helper

```powershell
# Load commands
. .\commands.ps1

# Run tests
Test-Phase1          # Unit tests
Test-System          # Integration test
```

## 📊 Test Coverage

### Unit Tests (`test_phase1.py`)

- ✅ Schema creation and validation
- ✅ NLP preprocessing
- ✅ LLM interpretation (mock mode)
- ✅ HRM engine processing
- ✅ Action execution
- ✅ Complete pipeline flow

### API Tests (`test_api.py`)

**Endpoint Coverage:**
- ✅ Health and status endpoints
- ✅ Main decision endpoint
- ✅ Component testing endpoints
- ✅ Audit log endpoints
- ✅ Configuration endpoints
- ✅ Error handling
- ✅ End-to-end workflows

**HTTP Methods:**
- ✅ GET requests
- ✅ POST requests
- ✅ OPTIONS (CORS)

**Status Codes:**
- ✅ 200 (Success)
- ✅ 404 (Not Found)
- ✅ 405 (Method Not Allowed)
- ✅ 422 (Validation Error)
- ✅ 500 (Internal Error)

### Functional Tests (`test_functional.py`)

**Workflows:**
- ✅ Security workflows (IP blocking, threat mitigation)
- ✅ Access management (grant/revoke access)
- ✅ Query workflows (log retrieval, information queries)
- ✅ Compliance workflows (audit reports)

**Features:**
- ✅ Time reference resolution
- ✅ Entity extraction (IPs, emails, usernames)
- ✅ Risk assessment logic
- ✅ Hierarchical reasoning (L1→L2→L3)
- ✅ Edge cases and error handling

### Performance Tests (`test_performance.py`)

**Metrics:**
- ✅ Response time (< 1 second end-to-end)
- ✅ Throughput (> 2 requests/second)
- ✅ Concurrent request handling
- ✅ Memory efficiency
- ✅ Scalability (50+ requests)

## 🎯 Test Categories

### By Type

```bash
# Unit tests
pytest -m unit

# Integration tests  
pytest -m integration

# API tests
pytest -m api

# Functional tests
pytest -m functional

# Performance tests (excluding slow tests)
pytest -m "performance and not slow"
```

### By Speed

```bash
# Fast tests only (< 1 second each)
pytest -m "not slow"

# All tests including slow ones
pytest
```

## 📈 Coverage Report

Generate coverage report:

```bash
# HTML coverage report
pytest --cov=app --cov-report=html

# Terminal coverage report
pytest --cov=app --cov-report=term

# Both
python run_tests.py coverage
```

View HTML report: Open `htmlcov/index.html` in browser

## ✅ Test Quality Standards

All tests follow these standards:

1. **Isolated** - Each test is independent
2. **Repeatable** - Same input → same output
3. **Fast** - Unit tests < 100ms, integration < 1s
4. **Clear** - Descriptive names and assertions
5. **Comprehensive** - Cover happy path, edge cases, errors

## 🔧 Test Configuration

### pytest.ini

Configuration file with:
- Test discovery patterns
- Markers for categorization
- Output formatting
- Logging configuration

### Markers

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.api           # API test
@pytest.mark.functional    # Functional test
@pytest.mark.performance   # Performance test
@pytest.mark.slow          # Slow running test
@pytest.mark.smoke         # Quick smoke test
```

## 🐛 Debugging Tests

### Verbose Output

```bash
pytest -v --tb=long
```

### Stop on First Failure

```bash
pytest -x
```

### Run Specific Test

```bash
pytest test_api.py::TestHealthEndpoints::test_root_endpoint -v
```

### Print Output

```bash
pytest -s  # Shows print statements
```

## 📊 Test Results

### Expected Results

When all tests pass:

```
======================== test session starts =========================
collected 95 items

test_phase1.py::TestSchemas::test_user_request_creation PASSED  [ 1%]
test_phase1.py::TestSchemas::test_llm_output_creation PASSED    [ 2%]
...
test_performance.py::TestStressTest::test_sustained_load PASSED [100%]

======================== 95 passed in 12.34s =========================
```

### Test Metrics

- **Total Tests**: 95+
- **Average Duration**: ~12 seconds (all tests)
- **Coverage**: 85%+ of core code
- **Success Rate**: 100% (all passing)

## 🚨 Continuous Integration

For CI/CD pipelines:

```bash
# Quick CI check (< 5 seconds)
pytest test_phase1.py -v

# Full CI check (< 30 seconds)
pytest -v -m "not slow"

# Complete test suite
pytest -v
```

## 📚 Writing New Tests

### Unit Test Template

```python
class TestMyFeature:
    """Test my new feature"""
    
    def test_basic_functionality(self):
        """Test that basic feature works"""
        # Arrange
        input_data = "test"
        
        # Act
        result = my_function(input_data)
        
        # Assert
        assert result is not None
        assert result == "expected"
```

### API Test Template

```python
def test_my_endpoint(self):
    """Test my new endpoint"""
    response = client.get("/api/v1/my-endpoint")
    
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

## 🎯 Test Checklist

Before committing code:

- [ ] All existing tests pass
- [ ] New features have tests
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] API endpoints tested
- [ ] Performance acceptable
- [ ] Coverage maintained/improved

## 📞 Troubleshooting

### Import Errors

```bash
# Make sure you're in backend directory
cd backend
pytest
```

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### Test Failures

1. Check test output for error details
2. Run individual test: `pytest test_file.py::TestClass::test_method -v`
3. Add print statements or use debugger
4. Check if mock/simulation modes are enabled

---

**All tests passing = Phase 1 complete! ✅**
