# Commit Plan for LLM Evaluation Framework

This document provides a detailed commit plan with 50+ commits to build the project incrementally.

## Initial Setup (Commits 1-5)

### Commit 1: Initialize project structure
**Files:**
- `.gitignore`
- `README.md` (basic)
- `.cursor/rules/project-core.mdc`

**Message:**
```
Initialize project structure and add Cursor rules

- Add .gitignore for Python, Node, and editor files
- Create basic README with project overview
- Add Cursor rules for tech stack and git workflow
```

### Commit 2: Add backend requirements and config
**Files:**
- `backend/requirements.txt`
- `backend/.env.example`

**Message:**
```
Add backend Python dependencies and environment template

- Add FastAPI, SQLAlchemy, PostgreSQL, Redis dependencies
- Create .env.example with database and API key configuration
```

### Commit 3: Set up backend core configuration
**Files:**
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/app/__init__.py`

**Message:**
```
Set up backend configuration and database connection

- Add Pydantic settings for environment variables
- Configure SQLAlchemy engine and session management
- Add database initialization function
```

### Commit 4: Create database models - Prompt
**Files:**
- `backend/app/models/prompt.py`
- `backend/app/models/__init__.py`

**Message:**
```
Add Prompt database model

- Create SQLAlchemy model for evaluation prompts
- Include fields: id, prompt_text, category, dataset_name, created_at
```

### Commit 5: Create database models - ModelResponse
**Files:**
- `backend/app/models/response.py`

**Message:**
```
Add ModelResponse database model

- Create model for storing LLM responses
- Include fields: id, prompt_id, model_name, response_text, latency
- Add foreign key relationship to Prompt
```

## Database Models (Commits 6-8)

### Commit 6: Create database models - Evaluation
**Files:**
- `backend/app/models/evaluation.py`

**Message:**
```
Add Evaluation database model

- Create model for storing evaluation scores
- Include fields: id, response_id, metric, score, evaluation_method
- Add foreign key relationship to ModelResponse
```

### Commit 7: Create database models - Experiment
**Files:**
- `backend/app/models/experiment.py`

**Message:**
```
Add Experiment database model

- Create model for tracking experiments
- Include fields: id, experiment_name, model_name, dataset_name, status
```

### Commit 8: Create database models - HumanFeedback
**Files:**
- `backend/app/models/human_score.py`

**Message:**
```
Add HumanFeedback database model

- Create model for human evaluation scores
- Include fields: id, response_id, score, reviewer_name, notes
- Add foreign key relationship to ModelResponse
```

## Pydantic Schemas (Commits 9-11)

### Commit 9: Add Pydantic schemas for Prompt
**Files:**
- `backend/app/schemas/prompt_schema.py`
- `backend/app/schemas/__init__.py`

**Message:**
```
Add Pydantic schemas for Prompt API

- Create PromptBase, PromptCreate, PromptResponse schemas
- Enable request validation and response serialization
```

### Commit 10: Add Pydantic schemas for ModelResponse
**Files:**
- `backend/app/schemas/response_schema.py`

**Message:**
```
Add Pydantic schemas for ModelResponse API

- Create response schemas for API validation
- Include latency and timestamp fields
```

### Commit 11: Add Pydantic schemas for Evaluation and Experiment
**Files:**
- `backend/app/schemas/evaluation_schema.py`

**Message:**
```
Add Pydantic schemas for Evaluation, Experiment, and HumanFeedback

- Create schemas for all evaluation-related endpoints
- Enable comprehensive API validation
```

## Services Layer (Commits 12-15)

### Commit 12: Implement ModelRunner service
**Files:**
- `backend/app/services/model_runner.py`
- `backend/app/services/__init__.py`

**Message:**
```
Add ModelRunner service for LLM execution

- Implement OpenAI API integration
- Add latency tracking
- Include placeholder for local model support
```

### Commit 13: Implement LLMJudge service
**Files:**
- `backend/app/services/llm_judge.py`

**Message:**
```
Add LLMJudge service for LLM-as-judge evaluation

- Implement GPT-4 based evaluation with rubrics
- Return structured scores for multiple metrics
- Include JSON response parsing
```

### Commit 14: Implement EvaluationEngine service
**Files:**
- `backend/app/services/evaluation_engine.py`

**Message:**
```
Add EvaluationEngine for rule-based evaluation

- Create orchestration layer for evaluation metrics
- Support multiple evaluation methods
- Enable selective metric evaluation
```

### Commit 15: Implement MetricsService
**Files:**
- `backend/app/services/metrics_service.py`

**Message:**
```
Add MetricsService for aggregating evaluation data

- Implement leaderboard generation
- Add model-specific metrics aggregation
- Create experiment summary statistics
```

## Evaluation Modules (Commits 16-19)

### Commit 16: Add correctness evaluation module
**Files:**
- `backend/app/evaluation/correctness.py`
- `backend/app/evaluation/__init__.py`

**Message:**
```
Add rule-based correctness evaluation

- Check for error indicators and completeness
- Validate prompt-response relevance
- Return score 0-10
```

### Commit 17: Add hallucination detection module
**Files:**
- `backend/app/evaluation/hallucination.py`

**Message:**
```
Add hallucination detection evaluation

- Detect overconfident statements
- Identify unsupported claims
- Check for internal contradictions
```

### Commit 18: Add reasoning quality evaluation
**Files:**
- `backend/app/evaluation/reasoning.py`

**Message:**
```
Add reasoning quality evaluation

- Identify logical connectors and structure
- Reward explanations and examples
- Penalize incomplete reasoning
```

### Commit 19: Add safety evaluation module
**Files:**
- `backend/app/evaluation/safety.py`

**Message:**
```
Add safety evaluation module

- Screen for harmful content patterns
- Validate appropriate disclaimers
- Reward safe refusals of harmful requests
```

## API Endpoints (Commits 20-24)

### Commit 20: Add Prompts API endpoints
**Files:**
- `backend/app/api/prompts.py`
- `backend/app/api/__init__.py`

**Message:**
```
Add Prompts API endpoints

- Implement GET /prompts/ (list with pagination)
- Implement POST /prompts/ (create)
- Implement GET /prompts/{id} (retrieve)
- Implement DELETE /prompts/{id} (delete)
```

### Commit 21: Add Responses API endpoints
**Files:**
- `backend/app/api/responses.py`

**Message:**
```
Add Responses API endpoints

- Implement GET /responses/ with filtering
- Implement GET /responses/{id}
- Implement POST /responses/
```

### Commit 22: Add Experiments API endpoints
**Files:**
- `backend/app/api/experiments.py`

**Message:**
```
Add Experiments API endpoints

- Implement GET /experiments/
- Implement POST /experiments/run (with background tasks)
- Implement GET /experiments/{id}
```

### Commit 23: Add Evaluation API endpoints
**Files:**
- `backend/app/api/evaluation.py`

**Message:**
```
Add Evaluation API endpoints

- Implement POST /evaluation/evaluate-response
- Implement GET /evaluation/leaderboard
- Implement GET /evaluation/metrics/{model_name}
- Implement GET /evaluation/experiment/{id}/summary
```

### Commit 24: Add HumanFeedback API endpoints
**Files:**
- `backend/app/api/human_feedback.py`

**Message:**
```
Add HumanFeedback API endpoints

- Implement GET /human-feedback/
- Implement POST /human-feedback/
- Implement GET /human-feedback/response/{id}
```

## Workers and Tasks (Commits 25-26)

### Commit 25: Add Celery worker configuration
**Files:**
- `backend/app/workers/worker.py`
- `backend/app/workers/__init__.py`

**Message:**
```
Add Celery worker configuration

- Configure Celery with Redis backend
- Set up task serialization and timezone
```

### Commit 26: Implement experiment execution tasks
**Files:**
- `backend/app/workers/tasks.py`

**Message:**
```
Add async experiment execution tasks

- Implement run_experiment_task for background processing
- Add dataset loading from JSON files
- Integrate model runner and evaluation engine
```

## Main Application (Commit 27)

### Commit 27: Create FastAPI main application
**Files:**
- `backend/app/main.py`

**Message:**
```
Create FastAPI main application

- Initialize FastAPI with metadata
- Add CORS middleware
- Register all API routers
- Add health check and root endpoints
- Initialize database on startup
```

## Prompt Datasets (Commits 28-30)

### Commit 28: Add reasoning prompt dataset
**Files:**
- `prompts/reasoning.json`

**Message:**
```
Add reasoning evaluation dataset

- Include math, logic, and problem-solving prompts
- Add 8 diverse reasoning test cases
```

### Commit 29: Add safety prompt dataset
**Files:**
- `prompts/safety.json`

**Message:**
```
Add safety evaluation dataset

- Include safety advice, emergency, and privacy prompts
- Add 8 safety-focused test cases
```

### Commit 30: Add Q&A prompt dataset
**Files:**
- `prompts/qa.json`

**Message:**
```
Add Q&A evaluation dataset

- Include factual knowledge questions
- Cover geography, history, science, and arts
- Add 10 diverse Q&A test cases
```

## Docker Setup (Commits 31-33)

### Commit 31: Add backend Dockerfile
**Files:**
- `backend/Dockerfile`

**Message:**
```
Add backend Dockerfile

- Use Python 3.11 slim image
- Install system dependencies
- Configure uvicorn server
```

### Commit 32: Add frontend Dockerfile
**Files:**
- `frontend/Dockerfile`

**Message:**
```
Add frontend Dockerfile

- Use Node 20 slim image
- Configure Vite dev server
```

### Commit 33: Create docker-compose configuration
**Files:**
- `docker-compose.yml`

**Message:**
```
Add docker-compose for full stack

- Configure PostgreSQL with health checks
- Configure Redis with persistence
- Set up backend with environment variables
- Set up frontend with hot reload
- Add volume mounts and networking
```

## Frontend Setup (Commits 34-38)

### Commit 34: Initialize frontend package configuration
**Files:**
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/tsconfig.node.json`

**Message:**
```
Initialize frontend with React, TypeScript, and Tailwind

- Add React 18 and TypeScript dependencies
- Add Recharts for data visualization
- Configure TypeScript compiler options
```

### Commit 35: Add frontend build configuration
**Files:**
- `frontend/vite.config.ts`
- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- `frontend/index.html`

**Message:**
```
Configure Vite, Tailwind, and PostCSS

- Set up Vite with React plugin
- Configure Tailwind CSS utility classes
- Add PostCSS for CSS processing
```

### Commit 36: Add frontend environment and types
**Files:**
- `frontend/.env.example`
- `frontend/src/vite-env.d.ts`

**Message:**
```
Add frontend environment configuration

- Create .env.example for API URL
- Add TypeScript environment types
```

### Commit 37: Create frontend API client
**Files:**
- `frontend/src/api/client.ts`

**Message:**
```
Create TypeScript API client

- Add axios-based API client
- Define TypeScript interfaces for all models
- Implement typed API methods for all endpoints
```

### Commit 38: Add global styles
**Files:**
- `frontend/src/index.css`

**Message:**
```
Add global styles with Tailwind

- Import Tailwind base, components, utilities
- Configure dark theme colors
- Set up root styling
```

## Frontend Components (Commits 39-43)

### Commit 39: Create ScoreCard component
**Files:**
- `frontend/src/components/ScoreCard.tsx`

**Message:**
```
Add ScoreCard component for displaying metrics

- Show score with visual progress bar
- Color-coded based on performance
- Responsive design with Tailwind
```

### Commit 40: Create Leaderboard component
**Files:**
- `frontend/src/components/Leaderboard.tsx`

**Message:**
```
Add Leaderboard component for model comparison

- Fetch and display model rankings
- Show average scores and response counts
- Styled table with hover effects
```

### Commit 41: Create ResponseViewer component
**Files:**
- `frontend/src/components/ResponseViewer.tsx`

**Message:**
```
Add ResponseViewer component

- Display prompt and model response
- Show model name and latency
- Clean card-based layout
```

### Commit 42: Create PromptRunner component
**Files:**
- `frontend/src/components/PromptRunner.tsx`

**Message:**
```
Add PromptRunner component for starting experiments

- Form for experiment configuration
- Model and dataset selection
- Submit experiment to API
```

### Commit 43: Create MetricsChart component
**Files:**
- `frontend/src/components/MetricsChart.tsx`

**Message:**
```
Add MetricsChart component with Recharts

- Bar chart for metric visualization
- Responsive container
- Dark theme styling
```

## Frontend Pages (Commits 44-47)

### Commit 44: Create Dashboard page
**Files:**
- `frontend/src/pages/Dashboard.tsx`

**Message:**
```
Add Dashboard page with overview metrics

- Display aggregate statistics in ScoreCards
- Show leaderboard and metrics chart
- Fetch data from multiple endpoints
```

### Commit 45: Create Experiments page
**Files:**
- `frontend/src/pages/Experiments.tsx`

**Message:**
```
Add Experiments page

- List recent experiments with status
- Integrate PromptRunner component
- Color-coded status badges
```

### Commit 46: Create Prompts page
**Files:**
- `frontend/src/pages/Prompts.tsx`

**Message:**
```
Add Prompts page for managing prompts

- List all prompts with categories
- Add new prompt form
- Category and dataset badges
```

### Commit 47: Create HumanEvaluation page
**Files:**
- `frontend/src/pages/HumanEvaluation.tsx`

**Message:**
```
Add HumanEvaluation page

- Display responses for human review
- Score slider and feedback form
- Navigation between responses
```

## Frontend App (Commits 48-49)

### Commit 48: Create main App with routing
**Files:**
- `frontend/src/App.tsx`

**Message:**
```
Add main App component with React Router

- Set up navigation with active states
- Configure routes for all pages
- Dark theme layout
```

### Commit 49: Create main entry point
**Files:**
- `frontend/src/main.tsx`

**Message:**
```
Add React application entry point

- Mount React app to DOM
- Enable strict mode
- Import global styles
```

## Documentation (Commits 50-52)

### Commit 50: Write comprehensive README
**Files:**
- `README.md`

**Message:**
```
Add comprehensive README documentation

- Project overview and architecture
- Complete setup instructions
- API endpoint documentation
- Usage guide and examples
- Deployment considerations
```

### Commit 51: Add contributing guidelines
**Files:**
- `CONTRIBUTING.md`
- `LICENSE`

**Message:**
```
Add contributing guidelines and MIT license

- Code style guidelines
- Pull request process
- Development workflow
- MIT license text
```

### Commit 52: Add root environment example
**Files:**
- `.env.example`

**Message:**
```
Add root environment example file

- Document required API keys
- Reference service-specific env files
```

## Final Touches (Commits 53-55)

### Commit 53: Update gitignore for production
**Files:**
- `.gitignore`

**Message:**
```
Update .gitignore for production readiness

- Add build artifacts
- Exclude environment files
- Ignore IDE and OS files
```

### Commit 54: Add commit plan documentation
**Files:**
- `COMMIT_PLAN.md`

**Message:**
```
Add detailed commit plan documentation

- Document 50+ commit strategy
- Provide commit messages and file lists
- Enable incremental development workflow
```

### Commit 55: Final project polish and verification
**Files:**
- (Review all files)

**Message:**
```
Final project verification and polish

- Verify all imports and dependencies
- Check file structure completeness
- Ensure consistent code style
- Validate configuration files
```

---

## How to Use This Commit Plan

1. Start from commit 1 and work sequentially
2. For each commit:
   - Create/modify the files listed
   - Stage the changes: `git add <files>`
   - Commit with the provided message: `git commit -m "message"`
3. Review your work after every 5-10 commits
4. Test functionality at major milestones (after backend setup, after frontend setup, etc.)

## Notes

- Each commit is atomic and focused on a specific feature or component
- Commits are ordered to minimize dependencies and enable incremental testing
- You can adjust commit messages to match your team's conventions
- Consider creating feature branches for major sections (backend, frontend, etc.)
