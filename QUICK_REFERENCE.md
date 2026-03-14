# Quick Reference Guide

## 🚀 Quick Start Commands

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Restart a service
docker-compose restart backend

# Access database
docker exec -it llm-eval-framework-postgres-1 psql -U postgres -d llm_eval
```

## 🌐 URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📁 Project Structure

```
llm-eval-framework/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── evaluation/     # Evaluation metrics
│   │   ├── workers/        # Async tasks
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # DB setup
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt    # Python deps
│   └── Dockerfile
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── App.tsx        # Main app
│   │   └── main.tsx       # Entry point
│   ├── package.json       # Node deps
│   └── Dockerfile
├── prompts/               # Evaluation datasets
│   ├── reasoning.json
│   ├── safety.json
│   └── qa.json
├── docker-compose.yml     # Docker orchestration
└── README.md             # Full documentation
```

## 🔑 Key Files to Edit

### Add Your API Key
```bash
backend/.env
# Add: OPENAI_API_KEY=sk-...
```

### Customize Models
```python
backend/app/services/model_runner.py
# Add support for new LLM providers
```

### Add New Metrics
```python
backend/app/evaluation/your_metric.py
# Create new evaluation function

backend/app/services/evaluation_engine.py
# Register the new metric
```

### Add New Datasets
```json
prompts/your_dataset.json
# Add array of prompt objects
```

## 📊 Database Tables

| Table | Purpose |
|-------|---------|
| `prompts` | Test prompts and questions |
| `model_responses` | LLM outputs with latency |
| `evaluations` | Automated scores |
| `experiments` | Experiment tracking |
| `human_feedback` | Human reviewer scores |

## 🛠️ Common Tasks

### Run an Experiment
1. Go to Experiments page
2. Fill in: name, model, dataset
3. Click "Run Experiment"
4. Check Dashboard for results

### Add Custom Prompts
1. Go to Prompts page
2. Click "Add Prompt"
3. Enter text, category, dataset
4. Submit

### Human Evaluation
1. Go to Human Eval page
2. Review prompt and response
3. Set score (1-10)
4. Add notes (optional)
5. Submit feedback

### View Leaderboard
1. Go to Dashboard
2. See model rankings
3. Click model for details

## 🔧 Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000  # or :5173, :5432, :6379

# Kill the process
kill -9 <PID>
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Frontend Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/app/main.py
# Check VITE_API_URL in frontend/.env
```

### OpenAI API Error
```bash
# Verify API key is set
cat backend/.env | grep OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## 📝 API Endpoints Quick Reference

### Prompts
- `GET /prompts/` - List all
- `POST /prompts/` - Create
- `GET /prompts/{id}` - Get one
- `DELETE /prompts/{id}` - Delete

### Experiments
- `GET /experiments/` - List all
- `POST /experiments/run` - Run new
- `GET /experiments/{id}` - Get one

### Evaluation
- `POST /evaluation/evaluate-response?response_id={id}&method=rule` - Evaluate
- `GET /evaluation/leaderboard` - Get rankings
- `GET /evaluation/metrics/{model}` - Model metrics

### Human Feedback
- `GET /human-feedback/` - List all
- `POST /human-feedback/` - Submit
- `GET /human-feedback/response/{id}` - Get for response

## 🎨 UI Components

| Component | Purpose |
|-----------|---------|
| ScoreCard | Display metric with progress bar |
| Leaderboard | Show model rankings |
| ResponseViewer | Display prompt and response |
| PromptRunner | Form to start experiments |
| MetricsChart | Bar chart visualization |

## 🔐 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
OPENAI_API_KEY=sk-...
JUDGE_MODEL=gpt-4o-mini
ENVIRONMENT=development
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 📦 Docker Commands

```bash
# Build images
docker-compose build

# Start in background
docker-compose up -d

# Start with logs
docker-compose up

# Stop services
docker-compose down

# Remove volumes (⚠️ deletes data)
docker-compose down -v

# Restart service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash
```

## 🧪 Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Create prompt
curl -X POST http://localhost:8000/prompts/ \
  -H "Content-Type: application/json" \
  -d '{"prompt_text": "Test", "category": "test"}'

# List prompts
curl http://localhost:8000/prompts/

# Get leaderboard
curl http://localhost:8000/evaluation/leaderboard
```

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Commit Strategy**: See `COMMIT_PLAN.md`
- **Project Overview**: See `PROJECT_SUMMARY.md`
- **Contributing**: See `CONTRIBUTING.md`
- **API Docs**: http://localhost:8000/docs

## 🆘 Getting Help

1. Check the logs: `docker-compose logs -f`
2. Review the README.md
3. Check API docs at /docs
4. Open an issue on GitHub

## 💡 Pro Tips

- Use the API docs at `/docs` for interactive testing
- Check `docker-compose logs` for debugging
- Use `docker-compose restart <service>` for quick fixes
- Keep your OpenAI API key secure (never commit it)
- Use `.env.example` as a template
- Run experiments with small datasets first
- Monitor costs when using OpenAI API

---

**Happy Evaluating! 🎉**
