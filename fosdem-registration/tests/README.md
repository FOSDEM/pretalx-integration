# fosdem_registration Testing Guide

This directory contains comprehensive pytest-django tests for the fosdem_registration plugin.

## Setup

### 1. Install Test Dependencies

```bash
pip install pytest pytest-django pytest-cov factory-boy
```

### 2. Export Data from Your Running Django Instance

First, export real data from your Django instance to use as test fixtures:

```bash
# From your pretalx instance directory
python manage.py shell < /path/to/fosdem-registration/export_test_data.py
```

This will create JSON fixtures in `tests/fixtures/` based on your real data.

### 3. Configure Test Settings

Ensure your Django test settings are properly configured. The tests use:
- `DJANGO_SETTINGS_MODULE=pretalx.common.settings.test_settings`
- SQLite in-memory database for speed
- Email backend for testing

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Model tests only
pytest -m models

# View tests only  
pytest -m views

# Form tests only
pytest -m forms

# Integration tests only
pytest -m integration

# Unit tests only (excludes integration and slow tests)
pytest -m "unit and not slow"

# Skip slow tests
pytest -m "not slow"
```

### Run with Coverage
```bash
pytest --cov=fosdem_registration --cov-report=html
```

### Verbose Output
```bash
pytest -v
```

## Test Structure

### Files
- `conftest.py` - Test configuration and fixtures
- `test_models.py` - Model unit tests
- `test_views.py` - View tests
- `test_forms.py` - Form tests  
- `test_integration.py` - End-to-end integration tests

### Test Categories

#### Unit Tests (`@pytest.mark.unit`)
- Fast, isolated tests
- Test individual components
- Mock external dependencies

#### Integration Tests (`@pytest.mark.integration`)
- Test multiple components working together
- Real database transactions
- Email sending
- Complete user workflows

#### Slow Tests (`@pytest.mark.slow`)
- Performance tests
- Bulk data operations
- Tests that take > 1 second

### Fixtures

The `conftest.py` file provides many reusable fixtures:

- `event` - Test FOSDEM event
- `user` - Test user account
- `team` - Test team with permissions
- `track` - Test track for sessions
- `submission` - Test session/workshop
- `registration_track` - Track configured for registrations
- `guardian` - Test guardian/parent
- `registration` - Test child registration
- `multiple_registrations` - Multiple test registrations
- `authenticated_client` - Client logged in with permissions

## Test Data

### Using Real Data
The `export_test_data.py` script exports anonymized data from your production instance:

- Events, tracks, submissions
- Questions and answers
- Teams and users (anonymized)
- Existing registrations (anonymized)

### Fixture Data
Tests use Django fixtures that create predictable test data:

```python
@pytest.fixture
def sample_form_data():
    return {
        "name": "Jane Doe",
        "email": "jane.doe@example.com", 
        "contact_number": "+32470987654",
        "form-TOTAL_FORMS": "2",
        # ... child registration data
    }
```

## Key Test Scenarios

### Model Tests
- Field validation (age limits, email format)
- Capacity limits and validation
- Model relationships and cascading deletes
- Custom model methods and properties

### View Tests  
- Permission requirements
- Proper context data
- Form handling (GET/POST)
- Error handling and edge cases
- Email notifications

### Form Tests
- Field validation
- Formset handling
- Required/optional fields
- Data cleaning and saving

### Integration Tests
- Complete registration workflows
- Capacity management
- Multi-event isolation
- Email notifications
- Performance with bulk data

## Debugging Tests

### Failed Test Debugging
```bash
# Run with detailed traceback
pytest --tb=long

# Run single test with output
pytest -s test_models.py::TestFosdemRegistration::test_capacity_validation_failure

# Drop into debugger on failure
pytest --pdb
```

### Database Inspection
```bash
# Keep test database for inspection
pytest --reuse-db

# Create test data in shell
python manage.py shell --settings=pretalx.common.settings.test_settings
```

## Writing New Tests

### Test Organization
- Group related tests in classes
- Use descriptive test method names
- Add appropriate markers (`@pytest.mark.models`, etc.)
- Include docstrings explaining what is being tested

### Using Fixtures
```python
def test_my_feature(self, submission, guardian, registration_track):
    # Test code using provided fixtures
    pass
```

### Testing Forms
```python
def test_form_validation(self):
    form_data = {"field": "value"}
    form = MyForm(data=form_data)
    assert form.is_valid()
    assert form.cleaned_data["field"] == "value"
```

### Testing Views
```python  
def test_view_response(self, client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert "expected_content" in response.content.decode()
```

### Testing Models
```python
def test_model_validation(self, submission, guardian):
    registration = FosdemRegistration(
        session=submission,
        registering_person=guardian,
        age=-1  # Invalid age
    )
    with pytest.raises(ValidationError):
        registration.full_clean()
```

## Performance Testing

The integration tests include performance benchmarks:

```python
def test_bulk_operations(self):
    start_time = time.time()
    # ... perform operations
    duration = time.time() - start_time
    assert duration < 2.0  # Should complete in < 2 seconds
```

## Continuous Integration

For CI/CD pipelines, run tests with:

```bash
# Fast test suite (skip slow tests)
pytest -m "not slow" --cov=fosdem_registration --cov-fail-under=80

# Full test suite  
pytest --cov=fosdem_registration --cov-fail-under=90 --cov-report=xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` includes pretalx source
2. **Database Errors**: Check test database permissions
3. **Missing Fixtures**: Run `export_test_data.py` to create fixtures
4. **Permission Errors**: Verify test user has required permissions

### Getting Help

- Check test output for specific error details
- Review fixture dependencies in `conftest.py`
- Ensure all required packages are installed
- Verify Django settings for test environment