# LLM Evaluation Framework

A production-ready open-source platform for evaluating Large Language Model (LLM) responses using benchmark prompts, automated grading, LLM-as-a-judge evaluation, and human feedback.

## Overview

This framework provides a comprehensive solution for evaluating LLM performance across different models, similar to the internal evaluation infrastructure used by AI labs. It combines automated metrics, LLM-based judging, and human evaluation to provide robust, multi-dimensional assessment of model outputs.

## Features

- **Benchmark Prompt Datasets**: Pre-built datasets for reasoning, safety, and Q&A evaluation
- **Multi-Model Support**: Run prompts against OpenAI models (GPT-4, GPT-3.5) and local models
- **Automated Evaluation Engine**: Rule-based metrics for correctness, hallucination, reasoning, and safety
- **LLM-as-Judge**: Use GPT-4 to evaluate responses with detailed rubrics
- **Human Evaluation Interface**: Web-based UI for human reviewers to score responses
- **Experiment Tracking**: Track and compare experiments across models and datasets
- **Metrics Dashboard**: Visualize performance with charts and leaderboards
- **Async Processing**: Background job processing with Celery/Redis for scalable evaluation

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React + TS)   │
└────────┬────────┘
         │
         │ REST API
         │
┌────────▼────────┐      ┌──────────────┐
│   Backend       │◄────►│  PostgreSQL  │
│   (FastAPI)     │      │   Database   │
└────────┬────────┘      └──────────────┘
         │
         │ Jobs Queue
         │
┌────────▼────────┐      ┌──────────────┐
│  Celery Worker  │◄────►│    Redis     │
│  (Async Tasks)  │      │    Cache     │
└─────────────────┘      └──────────────┘
         │
         │ API Calls
         │
┌────────▼────────┐
│   LLM APIs      │
│ (OpenAI, etc.)  │
└─────────────────┘
```

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database
- **Redis**: Cache and job queue
- **Celery**: Async task processing
- **OpenAI API**: LLM integration

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Recharts**: Data visualization
- **Vite**: Fast build tool

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **Uvicorn**: ASGI server

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (for LLM evaluation)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd llm-eval-framework
```

2. **Set up environment variables**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY

# Frontend
cp frontend/.env.example frontend/.env
```

3. **Start all services with Docker Compose**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- Backend API on port 8000
- Frontend on port 5173

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

### Manual Setup (Without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Run development server
npm run dev
```

## Usage

### Running an Experiment

1. Navigate to the **Experiments** page
2. Fill in the experiment form:
   - **Experiment Name**: Descriptive name for your experiment
   - **Model**: Select the LLM model (e.g., gpt-4o-mini)
   - **Dataset**: Choose a prompt dataset (reasoning, safety, qa)
3. Click **Run Experiment**
4. The system will:
   - Load prompts from the dataset
   - Run each prompt against the selected model
   - Automatically evaluate responses using rule-based metrics
   - Store all results in the database

### Viewing Results

- **Dashboard**: Overview of all experiments with aggregate metrics
- **Leaderboard**: Compare model performance across all evaluations
- **Metrics Charts**: Visualize performance by metric type

### Human Evaluation

1. Navigate to the **Human Evaluation** page
2. Review the prompt and model response
3. Assign a score (1-10)
4. Optionally add reviewer name and notes
5. Submit feedback
6. Navigate to the next response

### Adding Custom Prompts

1. Go to the **Prompts** page
2. Click **Add Prompt**
3. Enter prompt text, category, and dataset name
4. Submit to add to the database

## API Endpoints

### Prompts
- `GET /prompts/` - List all prompts
- `POST /prompts/` - Create a new prompt
- `GET /prompts/{id}` - Get a specific prompt
- `DELETE /prompts/{id}` - Delete a prompt

### Experiments
- `GET /experiments/` - List all experiments
- `POST /experiments/run` - Run a new experiment
- `GET /experiments/{id}` - Get experiment details
- `GET /evaluation/experiment/{id}/summary` - Get experiment summary

### Responses
- `GET /responses/` - List all model responses
- `GET /responses/{id}` - Get a specific response

### Evaluation
- `POST /evaluation/evaluate-response` - Evaluate a response
- `GET /evaluation/leaderboard` - Get model leaderboard
- `GET /evaluation/metrics/{model_name}` - Get metrics for a model

### Human Feedback
- `GET /human-feedback/` - List all human feedback
- `POST /human-feedback/` - Submit human feedback
- `GET /human-feedback/response/{id}` - Get feedback for a response

## Evaluation Metrics

### Rule-Based Metrics

1. **Correctness** (0-10)
   - Checks for error indicators
   - Validates response completeness
   - Measures prompt-response relevance

2. **Hallucination** (0-10, higher = less hallucination)
   - Detects overconfident statements
   - Identifies unsupported claims
   - Checks for internal contradictions

3. **Reasoning** (0-10)
   - Identifies logical connectors
   - Rewards structured thinking
   - Values examples and explanations

4. **Safety** (0-10)
   - Screens for harmful content
   - Validates appropriate disclaimers
   - Rewards safe refusals

### LLM-as-Judge

Uses GPT-4o-mini (configurable) to evaluate responses on:
- Correctness
- Reasoning quality
- Helpfulness
- Safety

Returns scores (1-10) with explanations.

## Adding New Metrics

1. Create a new evaluation module in `backend/app/evaluation/`:

```python
# backend/app/evaluation/my_metric.py
def check_my_metric(prompt: str, response: str) -> float:
    """
    Custom metric evaluation.
    Returns a score from 0 to 10.
    """
    score = 10.0
    # Your evaluation logic here
    return score
```

2. Register the metric in `evaluation_engine.py`:

```python
from app.evaluation.my_metric import check_my_metric

class EvaluationEngine:
    def __init__(self):
        self.metrics = {
            "my_metric": check_my_metric,
            # ... other metrics
        }
```

## Database Schema

### Tables

- **prompts**: Evaluation prompts and test cases
- **model_responses**: LLM responses to prompts
- **evaluations**: Automated evaluation scores
- **experiments**: Experiment tracking and metadata
- **human_feedback**: Human reviewer scores and notes

## Configuration

### Environment Variables

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port/0
OPENAI_API_KEY=your_api_key
JUDGE_MODEL=gpt-4o-mini
ENVIRONMENT=development
```

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:8000
```

## Development

### Backend Development

```bash
cd backend

# Run tests (when implemented)
pytest

# Format code
black app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Lint
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## Production Deployment

### Considerations

1. **Security**
   - Use strong database passwords
   - Secure API keys in environment variables or secret managers
   - Enable HTTPS/TLS
   - Implement authentication and authorization

2. **Scaling**
   - Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
   - Deploy Redis with persistence
   - Scale Celery workers horizontally
   - Use a reverse proxy (Nginx)
   - Implement rate limiting

3. **Monitoring**
   - Add logging (structured logging recommended)
   - Implement health checks
   - Monitor database performance
   - Track API response times
   - Set up alerts for failures

### Example Production Stack

- **Frontend**: Vercel, Netlify, or CloudFlare Pages
- **Backend**: AWS ECS, Google Cloud Run, or Kubernetes
- **Database**: AWS RDS PostgreSQL
- **Cache**: AWS ElastiCache Redis
- **Workers**: Separate container instances for Celery

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Inspired by evaluation frameworks used by leading AI labs
- Built with modern open-source tools and best practices

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ for the AI evaluation community**
