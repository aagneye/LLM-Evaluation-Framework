# Developer Guide

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### Local Development Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd llm-eval-framework

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup
cd ../frontend
npm install

# 4. Start infrastructure
docker-compose up postgres redis -d

# 5. Run migrations
cd ../backend
alembic upgrade head

# 6. Start backend
uvicorn app.main:app --reload

# 7. Start frontend (in new terminal)
cd frontend
npm run dev

# 8. Start worker (in new terminal)
cd backend
rq worker experiments --url redis://localhost:6379/0
```

## Project Structure

```
llm-eval-framework/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core infrastructure
│   │   ├── evaluation/       # Evaluation metrics
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── workers/          # Background jobs
│   ├── tests/                # Test suite
│   └── alembic/              # Database migrations
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   └── api/              # API client
│   └── public/               # Static assets
├── monitoring/               # Grafana & Prometheus
└── docs/                     # Documentation
```

## Code Style

### Python

We use:
- **black** for formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black app tests
isort app tests

# Lint
flake8 app tests

# Type check
mypy app
```

### TypeScript

We use:
- **Prettier** for formatting
- **ESLint** for linting

```bash
# Format
npm run format

# Lint
npm run lint
```

## Adding New Features

### Adding a New Model Provider

1. Create provider class:

```python
# backend/app/services/models/my_provider.py
from app.services.models.base import BaseModelProvider, ModelResponse

class MyProvider(BaseModelProvider):
    def __init__(self):
        super().__init__("my_provider")
    
    def is_available(self) -> bool:
        return True
    
    def list_models(self) -> list[str]:
        return ["model-1", "model-2"]
    
    def generate(self, prompt: str, model_name: str, **kwargs) -> ModelResponse:
        # Implementation
        pass
```

2. Register in registry:

```python
# backend/app/services/models/registry.py
from app.services.models.my_provider import MyProvider

class ModelRegistry:
    def _initialize_providers(self):
        self._providers = {
            # ... existing providers
            "my_provider": MyProvider(),
        }
```

### Adding a New Evaluation Metric

1. Create metric class:

```python
# backend/app/evaluation/metrics/my_metric.py
from app.evaluation.metrics.base import BaseMetric, MetricResult, MetricCategory

class MyMetric(BaseMetric):
    def __init__(self):
        super().__init__(
            name="my_metric",
            category=MetricCategory.CUSTOM,
            description="My custom metric"
        )
    
    def evaluate(self, prompt: str, response: str, **kwargs) -> MetricResult:
        # Calculate score
        score = 8.0
        
        return MetricResult(
            metric_name=self.name,
            score=score,
            category=self.category,
            passed=score >= 6.0
        )
```

2. Register in registry:

```python
# backend/app/evaluation/metrics/registry.py
from app.evaluation.metrics.my_metric import MyMetric

class MetricRegistry:
    def _initialize_default_metrics(self):
        default_metrics = [
            # ... existing metrics
            MyMetric(),
        ]
```

### Adding a New API Endpoint

1. Create router:

```python
# backend/app/api/my_endpoint.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/my-endpoint", tags=["My Feature"])

@router.get("/")
def list_items(db: Session = Depends(get_db)):
    return {"items": []}

@router.post("/")
def create_item(data: dict, db: Session = Depends(get_db)):
    return {"id": 1}
```

2. Include router in main app:

```python
# backend/app/main.py
from app.api import my_endpoint

app.include_router(my_endpoint.router)
```

## Database Migrations

### Creating a Migration

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add new table"

# Create empty migration
alembic revision -m "Custom migration"
```

### Applying Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current
```

### Migration Example

```python
# alembic/versions/xxx_add_new_table.py
def upgrade():
    op.create_table(
        'my_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('my_table')
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with verbose output
pytest -v

# Run only fast tests
pytest -m "not slow"
```

### Writing Tests

```python
# tests/test_my_feature.py
import pytest

def test_my_function():
    result = my_function(input_data)
    assert result == expected_output

def test_with_fixture(client, auth_headers):
    response = client.get("/endpoint", headers=auth_headers)
    assert response.status_code == 200

@pytest.mark.slow
def test_slow_operation():
    # Long-running test
    pass
```

### Test Fixtures

```python
# tests/conftest.py
@pytest.fixture
def my_fixture(db_session):
    # Setup
    obj = MyModel(name="test")
    db_session.add(obj)
    db_session.commit()
    
    yield obj
    
    # Teardown
    db_session.delete(obj)
    db_session.commit()
```

## Debugging

### Backend Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()

# VSCode launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload"
            ],
            "jinja": true
        }
    ]
}
```

### Frontend Debugging

```typescript
// Add debugger statement
debugger;

// Console logging
console.log('Debug:', data);

// React DevTools
// Install browser extension
```

### Logging

```python
# Backend
import structlog
logger = structlog.get_logger(__name__)

logger.debug("Debug message", key="value")
logger.info("Info message", user_id=123)
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

## Performance Optimization

### Database Queries

```python
# Use eager loading
from sqlalchemy.orm import joinedload

query = db.query(ModelResponse).options(
    joinedload(ModelResponse.prompt),
    joinedload(ModelResponse.evaluations)
)

# Use select_in loading for collections
from sqlalchemy.orm import selectinload

query = db.query(Experiment).options(
    selectinload(Experiment.responses)
)

# Add indexes
from sqlalchemy import Index

Index('idx_model_name', ModelResponse.model_name)
```

### Caching

```python
# Cache expensive operations
from app.core.cache import get_cache_manager

cache = get_cache_manager()

# Check cache first
cached = cache.get("expensive_operation")
if cached:
    return cached

# Compute and cache
result = expensive_operation()
cache.set("expensive_operation", result, ttl=3600)
return result
```

### Async Operations

```python
# Use async for I/O operations
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Run multiple operations concurrently
import asyncio

results = await asyncio.gather(
    fetch_data_1(),
    fetch_data_2(),
    fetch_data_3()
)
```

## Common Tasks

### Adding Dependencies

```bash
# Backend
pip install package-name
pip freeze > requirements.txt

# Frontend
npm install package-name
```

### Updating Dependencies

```bash
# Backend
pip install --upgrade package-name
pip freeze > requirements.txt

# Frontend
npm update package-name
```

### Running Linters

```bash
# Backend
black app tests
isort app tests
flake8 app tests
mypy app

# Frontend
npm run lint
npm run format
```

### Building for Production

```bash
# Backend
docker build -t llm-eval-backend:latest -f backend/Dockerfile.prod backend/

# Frontend
cd frontend
npm run build
```

## Troubleshooting

### Common Issues

**Import errors**:
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database connection errors**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL
```

**Redis connection errors**:
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
```

**Port already in use**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

## Best Practices

### Code Organization

- Keep functions small and focused
- Use type hints everywhere
- Write docstrings for public functions
- Follow SOLID principles
- Use dependency injection

### Error Handling

```python
# Use custom exceptions
from app.core.exceptions import ResourceNotFoundError

if not user:
    raise ResourceNotFoundError("User", user_id)

# Log errors with context
logger.error(
    "operation_failed",
    user_id=user_id,
    error=str(e),
    exc_info=True
)
```

### Security

- Never commit secrets
- Use environment variables
- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Add authentication to sensitive endpoints

### Performance

- Use database indexes
- Implement caching
- Use async for I/O
- Batch database operations
- Monitor query performance

## Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Run linters
5. Create pull request
6. Wait for review

See CONTRIBUTING.md for details.
