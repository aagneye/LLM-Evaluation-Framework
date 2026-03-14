# Contributing to LLM Evaluation Framework

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

See the main README.md for detailed setup instructions.

## Code Style

### Python (Backend)
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and modular

### TypeScript/React (Frontend)
- Use functional components with hooks
- Follow React best practices
- Use TypeScript for type safety
- Keep components small and reusable

## Commit Messages

Write clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Provide detailed description in the body if needed

## Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update the README.md if you're adding new features
4. Request review from maintainers

## Adding New Features

### New Evaluation Metrics
1. Create a new file in `backend/app/evaluation/`
2. Implement the evaluation function
3. Register it in `evaluation_engine.py`
4. Add tests
5. Update documentation

### New API Endpoints
1. Create or update router in `backend/app/api/`
2. Add corresponding schemas if needed
3. Update API documentation
4. Add tests

### New Frontend Components
1. Create component in `frontend/src/components/`
2. Follow existing patterns for styling
3. Ensure responsive design
4. Add to appropriate page

## Testing

- Write tests for new features
- Ensure existing tests pass
- Test both backend and frontend changes

## Questions?

Open an issue for questions or discussions about contributions.
