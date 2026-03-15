# API Documentation

Base URL: `http://localhost:8000`

All endpoints return JSON responses.

## Authentication

### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-03-15T10:00:00Z"
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Get Current User

```http
GET /auth/me
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-03-15T10:00:00Z"
}
```

## Experiments

### Create Experiment

```http
POST /experiments
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "GPT-4 Reasoning Test",
  "model_name": "gpt-4",
  "dataset_name": "reasoning",
  "temperature": 0.7
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "GPT-4 Reasoning Test",
  "model_name": "gpt-4",
  "dataset_name": "reasoning",
  "status": "pending",
  "job_id": "abc123",
  "created_at": "2024-03-15T10:00:00Z"
}
```

### List Experiments

```http
GET /experiments?limit=10&offset=0
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "experiments": [
    {
      "id": 1,
      "name": "GPT-4 Reasoning Test",
      "model_name": "gpt-4",
      "dataset_name": "reasoning",
      "status": "completed",
      "created_at": "2024-03-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

### Get Experiment Details

```http
GET /experiments/1
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "GPT-4 Reasoning Test",
  "model_name": "gpt-4",
  "dataset_name": "reasoning",
  "status": "completed",
  "total_responses": 10,
  "average_score": 8.5,
  "average_latency": 1.2,
  "created_at": "2024-03-15T10:00:00Z",
  "completed_at": "2024-03-15T10:05:00Z"
}
```

## Evaluation

### Get Leaderboard

```http
GET /evaluation/leaderboard?dataset=reasoning&limit=10
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "entries": [
    {
      "model_name": "gpt-4",
      "average_score": 8.5,
      "total_evaluations": 100,
      "correctness_score": 9.0,
      "hallucination_score": 8.5,
      "reasoning_score": 8.8,
      "safety_score": 9.2,
      "average_latency": 1.2,
      "rank": 1
    }
  ],
  "total_models": 3,
  "dataset_filter": "reasoning",
  "metric_filter": null
}
```

### Get Model Metrics

```http
GET /evaluation/metrics/gpt-4?dataset=reasoning
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "model_name": "gpt-4",
  "total_evaluations": 100,
  "average_score": 8.5,
  "metric_scores": {
    "correctness": 9.0,
    "hallucination": 8.5,
    "reasoning": 8.8,
    "safety": 9.2
  },
  "latency_stats": {
    "average": 1.2,
    "min": 0.8,
    "max": 2.5
  },
  "evaluation_distribution": {
    "excellent (9-10)": 45,
    "good (7-9)": 40,
    "moderate (5-7)": 10,
    "poor (0-5)": 5
  }
}
```

## Arena Evaluation

### Get Random Matchup

```http
GET /arena/matchup
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "prompt_text": "Explain quantum computing",
  "response_a": "Quantum computing uses quantum bits...",
  "response_a_id": 1,
  "response_a_model": "gpt-4",
  "response_b": "Quantum computers leverage quantum mechanics...",
  "response_b_id": 2,
  "response_b_model": "claude-3-opus"
}
```

### Submit Comparison

```http
POST /arena/compare
Authorization: Bearer <token>
Content-Type: application/json

{
  "response_a_id": 1,
  "response_b_id": 2,
  "winner": "A"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "prompt_id": 5,
  "response_a_id": 1,
  "response_b_id": 2,
  "winner": "A",
  "user_id": 1,
  "created_at": "2024-03-15T10:00:00Z"
}
```

### Get Arena Leaderboard

```http
GET /arena/leaderboard?limit=10
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "rankings": [
    {
      "model_name": "gpt-4",
      "elo_rating": 1650.5,
      "total_comparisons": 50,
      "wins": 30,
      "losses": 15,
      "ties": 5,
      "win_rate": 0.650,
      "updated_at": "2024-03-15T10:00:00Z"
    }
  ],
  "total_models": 3,
  "total_comparisons": 150
}
```

## Comparison

### Compare Experiments

```http
GET /compare/experiments?experiment_ids=1&experiment_ids=2
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "experiments": [
    {
      "experiment_id": 1,
      "experiment_name": "GPT-4 Test",
      "model_name": "gpt-4",
      "dataset_name": "reasoning",
      "total_responses": 10,
      "average_score": 8.5,
      "average_latency": 1.2,
      "metric_scores": {
        "correctness": 9.0,
        "hallucination": 8.5
      }
    }
  ],
  "metric_comparisons": [
    {
      "metric_name": "correctness",
      "experiment_scores": {
        "1": 9.0,
        "2": 8.2
      },
      "best_experiment_id": 1,
      "worst_experiment_id": 2,
      "score_range": 0.8
    }
  ],
  "best_overall_experiment_id": 1,
  "summary": {
    "total_experiments": 2,
    "total_responses": 20,
    "average_score_range": 0.5,
    "fastest_experiment": {
      "id": 2,
      "name": "GPT-3.5 Test",
      "latency": 0.8
    }
  }
}
```

### Compare Models

```http
GET /compare/models?model_names=gpt-4&model_names=claude-3-opus&dataset=reasoning
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "models": {
    "gpt-4": {
      "total_responses": 100,
      "average_score": 8.5,
      "average_latency": 1.2
    },
    "claude-3-opus": {
      "total_responses": 95,
      "average_score": 8.3,
      "average_latency": 1.5
    }
  },
  "dataset_filter": "reasoning"
}
```

## Prompts

### Create Prompt

```http
POST /prompts
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt_text": "What is 2+2?",
  "category": "math",
  "dataset_name": "arithmetic"
}
```

### List Prompts

```http
GET /prompts?dataset=reasoning&limit=10
Authorization: Bearer <token>
```

### Get Prompt

```http
GET /prompts/1
Authorization: Bearer <token>
```

## Responses

### List Responses

```http
GET /responses?experiment_id=1&limit=10
Authorization: Bearer <token>
```

### Get Response

```http
GET /responses/1
Authorization: Bearer <token>
```

## Human Feedback

### Submit Feedback

```http
POST /human-feedback
Authorization: Bearer <token>
Content-Type: application/json

{
  "response_id": 1,
  "score": 8,
  "notes": "Good response but could be more detailed",
  "reviewer_name": "John Doe"
}
```

### List Feedback

```http
GET /human-feedback?response_id=1
Authorization: Bearer <token>
```

## Health & Metrics

### Health Check

```http
GET /health
```

**Response** (200 OK):
```json
{
  "status": "healthy"
}
```

### Prometheus Metrics

```http
GET /metrics
```

**Response** (200 OK):
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status_code="200"} 42.0
...
```

## Error Responses

### 400 Bad Request

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "path": "/experiments"
  }
}
```

### 401 Unauthorized

```json
{
  "error": {
    "code": "AUTH_ERROR",
    "message": "Authentication failed",
    "path": "/experiments"
  }
}
```

### 403 Forbidden

```json
{
  "error": {
    "code": "AUTHZ_ERROR",
    "message": "Insufficient permissions",
    "path": "/admin"
  }
}
```

### 404 Not Found

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Experiment with id 999 not found",
    "path": "/experiments/999"
  }
}
```

### 429 Too Many Requests

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "path": "/experiments"
  }
}
```

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1710504000
Retry-After: 60
```

### 500 Internal Server Error

```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "path": "/experiments"
  }
}
```

## Rate Limiting

All authenticated endpoints are rate-limited to **100 requests per minute** per user.

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Pagination

List endpoints support pagination:
- `limit`: Number of items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

Example:
```http
GET /experiments?limit=20&offset=40
```

## Filtering

Many endpoints support filtering:
- `dataset`: Filter by dataset name
- `model_name`: Filter by model name
- `status`: Filter by status

Example:
```http
GET /experiments?dataset=reasoning&status=completed
```

## Sorting

Some endpoints support sorting:
- `sort_by`: Field to sort by
- `order`: `asc` or `desc`

Example:
```http
GET /experiments?sort_by=created_at&order=desc
```

## Correlation IDs

All requests receive a correlation ID for tracing:

**Request Header**:
```
X-Correlation-ID: abc-123-def-456
```

**Response Header**:
```
X-Correlation-ID: abc-123-def-456
```

Use this ID when reporting issues or debugging.
