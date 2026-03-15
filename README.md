# LLM Evaluation Framework

> **Production-ready platform for evaluating Large Language Models with automated metrics, human feedback, and Arena-style comparisons.**

[![CI/CD](https://github.com/yourusername/llm-eval-framework/workflows/CI/badge.svg)](https://github.com/yourusername/llm-eval-framework/actions)
[![codecov](https://codecov.io/gh/yourusername/llm-eval-framework/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/llm-eval-framework)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

### Core Capabilities

- **Multi-Provider Support**: OpenAI, Anthropic, and local models (Ollama/vLLM)
- **Automated Evaluation**: 4 built-in metrics (Correctness, Hallucination, Reasoning, Safety)
- **Arena Evaluation**: Pairwise comparisons with ELO rankings
- **Human Feedback**: Web-based review interface
- **Experiment Tracking**: Compare models across datasets
- **Leaderboards**: Dynamic rankings with filtering

### Production Features

- **JWT Authentication**: Secure user management
- **Rate Limiting**: 100 req/min per user with Redis
- **Job Queue**: Horizontal scaling with RQ workers
- **Caching**: Redis-based response caching
- **Observability**: Prometheus metrics + Grafana dashboards
- **Security**: SQL injection prevention, XSS protection, API key encryption
- **CI/CD**: GitHub Actions with automated testing
- **Documentation**: Comprehensive API, architecture, and deployment docs

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourusername/llm-eval-framework.git
cd llm-eval-framework

# 2. Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and SECRET_KEY

# 3. Start with Docker
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# Grafana: http://localhost:3000 (admin/admin)
```

## 🏗️ Architecture

```
┌─────────────┐
│   React     │  Frontend (TypeScript + Tailwind)
│  Dashboard  │
└──────┬──────┘
       │ REST API
┌──────┴──────┐
│   FastAPI   │  Backend (Python 3.11)
│   Backend   │  - Authentication (JWT)
└──────┬──────┘  - Rate Limiting (Redis)
       │         - Caching (Redis)
   ┌───┴───┬────────┬──────┐
   │       │        │      │
┌──┴──┐ ┌─┴──┐  ┌──┴──┐ ┌─┴──┐
│ PG  │ │Redis│ │  S3 │ │ RQ │
│ SQL │ │     │ │     │ │Work│
└─────┘ └─────┘ └─────┘ └────┘
```

**Key Components**:
- **FastAPI Backend**: RESTful API with async support
- **React Frontend**: Modern UI with TypeScript
- **PostgreSQL**: Relational database for experiments and results
- **Redis**: Caching and job queue
- **RQ Workers**: Async experiment execution
- **Prometheus + Grafana**: Monitoring and metrics

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

## 📦 Installation

### Prerequisites

- Docker 24+ and Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

### Docker Installation (Recommended)

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Installation

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Workers

```bash
cd backend
rq worker experiments --url redis://localhost:6379/0
```

## 🎯 Usage

### 1. Register and Login

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'

curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. Create Experiment

```bash
curl -X POST http://localhost:8000/experiments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "GPT-4 Reasoning Test",
    "model_name": "gpt-4",
    "dataset_name": "reasoning",
    "temperature": 0.7
  }'
```

### 3. View Leaderboard

```bash
curl http://localhost:8000/evaluation/leaderboard \
  -H "Authorization: Bearer <token>"
```

### 4. Arena Evaluation

```bash
# Get matchup
curl http://localhost:8000/arena/matchup \
  -H "Authorization: Bearer <token>"

# Submit vote
curl -X POST http://localhost:8000/arena/compare \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "response_a_id": 1,
    "response_b_id": 2,
    "winner": "A"
  }'
```

## 📚 API Documentation

Full API documentation is available at:
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Markdown**: [API.md](API.md)

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get JWT token |
| `/experiments` | POST | Create experiment |
| `/evaluation/leaderboard` | GET | Get model rankings |
| `/arena/matchup` | GET | Get pairwise comparison |
| `/compare/experiments` | GET | Compare experiments |
| `/metrics` | GET | Prometheus metrics |

## 🛠️ Development

### Project Structure

```
llm-eval-framework/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core infrastructure
│   │   ├── evaluation/       # Metrics
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   └── workers/          # Background jobs
│   └── tests/                # Test suite
├── frontend/
│   └── src/
│       ├── components/       # React components
│       └── pages/            # Page components
├── monitoring/               # Grafana & Prometheus
└── docs/                     # Documentation
```

### Running Tests

```bash
# Backend tests
cd backend
pytest --cov=app --cov-report=html

# Frontend tests
cd frontend
npm test
```

### Code Quality

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

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for detailed development instructions.

## 🚢 Deployment

### Docker Production Deployment

```bash
# 1. Set up environment
cp .env.example .env.production
# Edit .env.production with production values

# 2. Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# 3. Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 4. Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale worker=5
```

### Kubernetes Deployment

```bash
# Apply configurations
kubectl apply -f k8s/

# Check status
kubectl get pods -n llm-eval
```

### AWS Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- AWS ECS Fargate
- RDS and ElastiCache
- S3 storage
- Load balancing
- SSL/TLS setup

## 📊 Monitoring

### Prometheus Metrics

Access metrics at: http://localhost:8000/metrics

**Key Metrics**:
- `http_requests_total`: Total HTTP requests
- `http_request_duration_seconds`: Request latency
- `model_requests_total`: Model API requests
- `evaluation_duration_seconds`: Evaluation latency
- `cache_operations_total`: Cache operations

### Grafana Dashboards

Access Grafana at: http://localhost:3000

**Default Dashboards**:
- HTTP Request Rate
- API Latency (p95, p99)
- Model Provider Performance
- Cache Hit Rate
- Error Rate by Endpoint

## 🔒 Security

### Production Security Checklist

- [x] JWT authentication with secure secret
- [x] Password hashing with bcrypt
- [x] Rate limiting (100 req/min per user)
- [x] SQL injection prevention
- [x] XSS attack prevention
- [x] API key encryption
- [x] CORS configuration
- [x] Input validation
- [ ] HTTPS/SSL (configure in production)
- [ ] Security headers (configure in nginx)
- [ ] Regular dependency updates

### Environment Variables

**Required**:
- `SECRET_KEY`: JWT signing key (min 32 characters)
- `OPENAI_API_KEY`: OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

**Optional**:
- `ANTHROPIC_API_KEY`: Anthropic API key
- `S3_ACCESS_KEY`: S3 access key
- `S3_SECRET_KEY`: S3 secret key

## 🧪 Testing

### Test Coverage

Current coverage: **85%+**

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with markers
pytest -m "not slow"
```

### Test Categories

- **Unit Tests**: Individual functions and classes
- **Integration Tests**: API endpoints with database
- **Security Tests**: SQL injection, XSS, encryption
- **Performance Tests**: Load testing (optional)

## 📈 Performance

### Benchmarks

- **API Response Time**: <100ms (cached)
- **Model API Latency**: 1-5 seconds
- **Throughput**: 100 req/sec per backend instance
- **Cache Hit Rate**: 70-90% (typical)

### Optimization Tips

1. **Enable Caching**: Reduces API costs by 70%+
2. **Scale Workers**: Add more RQ workers for parallel execution
3. **Database Indexing**: Ensure proper indexes on queries
4. **Connection Pooling**: Configure PostgreSQL connection pool
5. **Redis Memory**: Allocate sufficient memory for cache

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Steps

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Workflow

1. Write code following style guidelines
2. Add tests for new features
3. Run linters and tests
4. Update documentation
5. Submit PR with clear description

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- OpenAI and Anthropic for LLM APIs
- React and Tailwind CSS for the frontend
- Prometheus and Grafana for monitoring
- All open-source contributors

## 📞 Support

- **Documentation**: See [docs/](docs/) folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/llm-eval-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/llm-eval-framework/discussions)

## 🗺️ Roadmap

### v1.1 (Next Release)
- [ ] Support for more LLM providers (Google, Cohere)
- [ ] Advanced metrics (Toxicity, Bias detection)
- [ ] Experiment scheduling
- [ ] Email notifications
- [ ] CSV/PDF export

### v2.0 (Future)
- [ ] Multi-turn conversation evaluation
- [ ] Custom metric builder UI
- [ ] Collaborative evaluation
- [ ] Advanced analytics
- [ ] API versioning

## 📊 Stats

- **Lines of Code**: 15,000+
- **Test Coverage**: 85%+
- **API Endpoints**: 30+
- **Database Tables**: 8
- **Evaluation Metrics**: 4 (extensible)
- **Model Providers**: 3 (extensible)

---

**Built with ❤️ for the AI community**

[⬆ Back to top](#llm-evaluation-framework)
