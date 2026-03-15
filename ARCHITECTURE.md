# LLM Evaluation Framework - Architecture

## System Overview

The LLM Evaluation Framework is a production-ready platform for evaluating Large Language Models using automated metrics, LLM-as-judge scoring, human feedback, and Arena-style pairwise comparisons.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │Experiments│  │Arena     │  │Leaderboard│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
┌────────────────────────┴────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Layer (Routers)                                 │   │
│  │  - Auth  - Experiments  - Arena  - Comparison       │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Services Layer                                      │   │
│  │  - ModelRegistry  - MetricRegistry  - JobQueue      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Core Infrastructure                                 │   │
│  │  - Logging  - Caching  - Rate Limiting  - Security  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────┬──────────────┬──────────────┬─────────────────┘
             │              │              │
    ┌────────┴────┐  ┌──────┴──────┐  ┌───┴────┐
    │ PostgreSQL  │  │   Redis     │  │   S3   │
    │  Database   │  │Cache/Queue  │  │Storage │
    └─────────────┘  └─────────────┘  └────────┘
                          │
                    ┌─────┴─────┐
                    │ RQ Workers│
                    │(Scalable) │
                    └───────────┘
```

## Component Details

### 1. Frontend Layer

**Technology**: React 18 + TypeScript + Vite + Tailwind CSS

**Components**:
- Dashboard: Overview with stats and charts
- Experiments: Run and manage experiments
- Arena: Pairwise model comparisons
- Leaderboard: Model rankings

### 2. API Layer

**Technology**: FastAPI + Pydantic

**Routers**:
- `/auth`: JWT authentication
- `/experiments`: Experiment management
- `/evaluation`: Metrics and leaderboard
- `/arena`: Pairwise comparisons with ELO
- `/compare`: Experiment comparison

**Middleware**:
- CorrelationIdMiddleware: Request tracing
- RequestLoggingMiddleware: Structured logging
- PrometheusMiddleware: Metrics collection
- RateLimitMiddleware: 100 req/min per user

### 3. Services Layer

**Model Providers**:
- OpenAIProvider: GPT-4, GPT-3.5
- AnthropicProvider: Claude models
- LocalLlamaProvider: Ollama/vLLM

**Evaluation Metrics**:
- CorrectnessMetric: Error detection
- HallucinationMetric: False claim detection
- ReasoningMetric: Logical structure
- SafetyMetric: Harmful content screening

**Job Queue**:
- RQ (Redis Queue) for async experiment execution
- Horizontally scalable workers
- 1-hour job timeout

### 4. Data Layer

**PostgreSQL Tables**:
- users: Authentication and authorization
- prompts: Test cases
- model_responses: LLM outputs
- evaluations: Metric scores
- experiments: Experiment tracking
- arena_comparisons: Pairwise votes
- arena_elo_ratings: ELO rankings

**Redis**:
- Cache: Model responses (7-day TTL)
- Rate Limiting: Sliding window
- Job Queue: Experiment tasks

**S3 Storage**:
- Dataset uploads
- JSON prompt files

### 5. Observability

**Logging**:
- Structured JSON logs with structlog
- Correlation IDs for distributed tracing
- Log levels: DEBUG, INFO, WARNING, ERROR

**Metrics**:
- Prometheus metrics endpoint
- HTTP request rate and duration
- Model API latency by provider
- Evaluation latency by metric
- Cache hit rate

**Monitoring**:
- Grafana dashboards
- Real-time metrics visualization
- Alerting capabilities

### 6. Security

**Authentication**:
- JWT tokens (HS256)
- Bcrypt password hashing
- 7-day token expiration

**Authorization**:
- User roles (user, superuser)
- Protected endpoints

**Input Validation**:
- SQL injection prevention
- XSS attack prevention
- Input sanitization

**Encryption**:
- API key encryption (Fernet)
- Secure secret management

**Rate Limiting**:
- 100 requests/minute per user
- Redis-based sliding window

## Data Flow

### Experiment Execution Flow

```
1. User creates experiment via API
   ↓
2. API validates input and enqueues job
   ↓
3. RQ Worker picks up job
   ↓
4. Worker fetches prompts from database
   ↓
5. Worker calls ModelRegistry.generate()
   ↓
6. ModelRegistry routes to appropriate provider
   ↓
7. Provider calls LLM API (with retry logic)
   ↓
8. Response cached in Redis
   ↓
9. MetricRegistry evaluates response
   ↓
10. Results stored in database
    ↓
11. Experiment status updated
```

### Arena Evaluation Flow

```
1. User requests matchup
   ↓
2. API selects 2 random responses for same prompt
   ↓
3. User votes for winner (A, B, or Tie)
   ↓
4. ArenaService updates ELO ratings
   ↓
5. Comparison stored in database
   ↓
6. Leaderboard automatically updated
```

## Scalability

### Horizontal Scaling

**Workers**: Deploy multiple RQ workers
```bash
docker-compose up --scale worker=5
```

**Backend**: Run multiple FastAPI instances behind load balancer

### Vertical Scaling

**Database**: Increase PostgreSQL resources
**Redis**: Increase memory allocation
**Workers**: Increase worker concurrency

### Caching Strategy

**Model Responses**: 7-day TTL
- Key: `model_name:prompt_hash:temperature`
- Reduces API costs significantly

**Evaluation Results**: Optional caching
- Key: `metric_name:prompt_hash:response_hash`

## Deployment

### Development

```bash
docker-compose up
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Production Features**:
- Multi-stage Docker builds
- Non-root containers
- Health checks
- Restart policies
- Prometheus + Grafana
- Nginx reverse proxy

### CI/CD

**GitHub Actions**:
- Run tests on push
- Lint code (flake8, black, isort)
- Build Docker images
- Security scanning (Trivy)
- Coverage reporting (Codecov)

## Performance

**Expected Throughput**:
- 100 requests/second per backend instance
- 10 concurrent experiments per worker
- Sub-100ms API response time (cached)
- 1-5 second model API response time

**Optimization Techniques**:
- Response caching
- Database connection pooling
- Async I/O with FastAPI
- Redis for fast lookups
- Indexed database queries

## Extensibility

### Adding New Model Providers

1. Implement `BaseModelProvider`
2. Register in `ModelRegistry`
3. Add configuration in settings

### Adding New Metrics

1. Implement `BaseMetric`
2. Register in `MetricRegistry`
3. Metric automatically available in API

### Adding New Evaluation Methods

1. Create service class
2. Add API endpoint
3. Update frontend

## Security Considerations

**Production Checklist**:
- [ ] Change SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up firewall rules
- [ ] Enable database backups
- [ ] Rotate API keys regularly
- [ ] Monitor security logs
- [ ] Keep dependencies updated
- [ ] Use managed services (RDS, ElastiCache)

## Maintenance

**Regular Tasks**:
- Monitor logs for errors
- Check Prometheus metrics
- Review database performance
- Clear old cache entries
- Backup database
- Update dependencies
- Review security alerts

**Troubleshooting**:
- Check `/health` endpoint
- Review structured logs
- Check Redis connectivity
- Verify database connections
- Monitor worker queue length
