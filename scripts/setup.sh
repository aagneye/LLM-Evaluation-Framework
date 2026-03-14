#!/bin/bash

# LLM Evaluation Framework Setup Script

set -e

echo "🚀 Setting up LLM Evaluation Framework..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your OPENAI_API_KEY"
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend/.env from example..."
    cp frontend/.env.example frontend/.env
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "✅ Setup complete!"
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:5173"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
echo "⚠️  Don't forget to add your OPENAI_API_KEY to backend/.env!"
