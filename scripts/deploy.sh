#!/bin/bash

# NeuroAgent Deployment Script

set -e

echo "🚀 Starting NeuroAgent deployment..."

# Check prerequisites
command -v aws >/dev/null 2>&1 || { echo "❌ AWS CLI is required but not installed. Aborting." >&2; exit 1; }
command -v python >/dev/null 2>&1 || { echo "❌ Python is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Build frontend
echo "🏗️ Building frontend..."
cd frontend
npm run build
cd ..

# Deploy infrastructure
echo "☁️ Deploying AWS infrastructure..."
cd infrastructure/cdk
pip install -r requirements.txt
cdk bootstrap
cdk deploy --require-approval never
cd ../..

echo "✅ Deployment completed successfully!"
echo "🌐 Your NeuroAgent application is now deployed!"
