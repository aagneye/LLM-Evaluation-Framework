#!/bin/bash

# Simple API test script

API_URL="http://localhost:8000"

echo "🧪 Testing LLM Evaluation Framework API..."
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "${API_URL}/health" | jq '.'
echo ""

# Test root endpoint
echo "2. Testing root endpoint..."
curl -s "${API_URL}/" | jq '.'
echo ""

# Create a test prompt
echo "3. Creating a test prompt..."
PROMPT_RESPONSE=$(curl -s -X POST "${API_URL}/prompts/" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_text": "What is 2 + 2?",
    "category": "math",
    "dataset_name": "test"
  }')
echo "$PROMPT_RESPONSE" | jq '.'
PROMPT_ID=$(echo "$PROMPT_RESPONSE" | jq -r '.id')
echo ""

# List prompts
echo "4. Listing all prompts..."
curl -s "${API_URL}/prompts/" | jq '.'
echo ""

# Get experiments
echo "5. Listing experiments..."
curl -s "${API_URL}/experiments/" | jq '.'
echo ""

# Get leaderboard
echo "6. Getting leaderboard..."
curl -s "${API_URL}/evaluation/leaderboard" | jq '.'
echo ""

echo "✅ API tests complete!"
