#!/bin/bash

# NeuroAgent Local Development Setup

set -e

echo "🔧 Setting up NeuroAgent for local development..."

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please update with your AWS credentials."
fi

# Install backend dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Start services with Docker Compose
echo "🐳 Starting development services..."
docker-compose up -d

echo "✅ Local development environment is ready!"
echo "🌐 Backend API: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo "📚 API Documentation: http://localhost:8000/docs"
