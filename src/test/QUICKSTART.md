# Quick Start: Running Tests

## Prerequisites

Make sure you have pytest and dependencies installed:

```bash
# Install all development dependencies
pip install pytest pytest-cov httpx pytest-asyncio

# Or using the project's pyproject.toml
pip install -e ".[dev]"
```

## Running Tests

### Run All Tests
```bash
pytest src/test/ -v
```

### Run with Coverage Report
```bash
pytest src/test/ -v --cov=src --cov-report=term-missing --cov-report=html
```

This generates:
- Terminal report with missing line numbers
- HTML coverage report in `htmlcov/index.html`

### Run Specific Test File
```bash
pytest src/test/test_user.py -v
pytest src/test/test_product.py -v
```

### Run Specific Test Class
```bash
pytest src/test/test_user.py::TestUserCreate -v
pytest src/test/test_product.py::TestCreateProduct -v
```

### Run Single Test
```bash
pytest src/test/test_user.py::TestUserCreate::test_create_user_success -v
```

### Run with Less Verbose Output
```bash
pytest src/test/ -q
```

### Run with Short Traceback
```bash
pytest src/test/ --tb=short
```

## Test Structure

```
src/test/
├── __init__.py              # Test package
├── conftest.py              # Shared fixtures and configuration
├── test_app.py              # Application-level tests
├── test_user.py             # User endpoint tests
├── test_product.py          # Product endpoint tests
└── README.md                # Test documentation
```

## Fixtures Available

All fixtures are defined in `conftest.py`:

- `db` - Fresh SQLite in-memory database for each test
- `client` - FastAPI test client
- `test_user` - Regular authenticated user
- `admin_user` - Administrator user
- `test_product` - Sample product
- `user_token` - JWT token for test_user
- `admin_token` - JWT token for admin_user

## Example Usage

```python
def test_something(client, user_token, test_product):
    """Example test using fixtures."""
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get(f"/api/v0/products/{test_product.Product_ID}", headers=headers)
    assert response.status_code == 200
```

## CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Run tests
  run: pytest src/test/ -v --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Notes

- Tests use an in-memory SQLite database (no real database needed)
- Session is isolated per test for clean state
- All tests complete in ~11 seconds
- 100% of tests pass with current implementation
