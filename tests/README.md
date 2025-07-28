# Tests

This directory contains all test files for the Tiny Backspace project.

## Test Files

- **test_simple.py** - Basic API functionality tests
- **test_file_editing.py** - Comprehensive file editing tests with various scenarios
- **test_observability.py** - Observability and logging system tests
- **test_small_repo.py** - Tests for small repository handling

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python tests/test_simple.py

# Run with verbose output
python -m pytest tests/ -v
```

## Test Categories

### Unit Tests

- Individual component testing
- Service layer validation
- API endpoint testing

### Integration Tests

- End-to-end workflow testing
- AI provider integration
- GitHub API integration

### Observability Tests

- Logging system validation
- Performance monitoring
- Error tracking
