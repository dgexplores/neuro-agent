#!/bin/bash
# Lambda Dependencies Fix Script
# Run this script in AWS Cloud9 or Linux/Mac environment

set -e  # Exit on error

echo "=========================================="
echo "NeuroAgent Lambda Dependencies Fix"
echo "=========================================="
echo ""

# Check environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "❌ Error: This script must run in Linux/Mac or AWS Cloud9"
    echo "Current OS: $OSTYPE (Windows detected)"
    echo ""
    echo "Options:"
    echo "1. Use AWS Cloud9 (Recommended)"
    echo "2. Use Linux VM or WSL2"
    echo "3. Use Mac"
    exit 1
fi

echo "✅ Environment check passed"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)
echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Create Lambda Layer directory structure
echo "📦 Creating Lambda Layer directory..."
rm -rf lambda_layer
mkdir -p lambda_layer/python

# Install dependencies
echo "📥 Installing Python dependencies..."
echo "This may take 5-10 minutes depending on your connection..."
echo ""

pip3 install -r requirements.txt -t lambda_layer/python/ --no-cache-dir --platform manylinux2014_x86_64 --only-binary=:all: || {
    echo "⚠️  Platform-specific installation failed, trying standard install..."
    pip3 install -r requirements.txt -t lambda_layer/python/
}

# Check if installation succeeded
if [ ! -d "lambda_layer/python" ] || [ -z "$(ls -A lambda_layer/python)" ]; then
    echo "❌ Error: Lambda Layer installation failed"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully"
echo ""

# Display layer size
LAYER_SIZE=$(du -sh lambda_layer | cut -f1)
echo "📊 Lambda Layer size: $LAYER_SIZE"
echo ""

# Check for problematic packages
echo "🔍 Checking for large packages..."
if [ -d "lambda_layer/python/pandas" ]; then
    PANDAS_SIZE=$(du -sh lambda_layer/python/pandas | cut -f1)
    echo "  - pandas: $PANDAS_SIZE"
fi
if [ -d "lambda_layer/python/numpy" ]; then
    NUMPY_SIZE=$(du -sh lambda_layer/python/numpy | cut -f1)
    echo "  - numpy: $NUMPY_SIZE"
fi

echo ""
echo "🧹 Cleaning up unnecessary files..."
# Remove __pycache__ and .pyc files
find lambda_layer/python -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find lambda_layer/python -type f -name "*.pyc" -delete 2>/dev/null || true
find lambda_layer/python -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove tests and examples
find lambda_layer/python -type d -name tests -exec rm -rf {} + 2>/dev/null || true
find lambda_layer/python -type d -name test -exec rm -rf {} + 2>/dev/null || true
find lambda_layer/python -type d -name examples -exec rm -rf {} + 2>/dev/null || true

CLEANED_SIZE=$(du -sh lambda_layer | cut -f1)
echo "📊 Lambda Layer size after cleanup: $CLEANED_SIZE"
echo ""

# Verify critical imports
echo "🔬 Verifying critical imports..."
python3 << 'EOF'
import sys
sys.path.insert(0, 'lambda_layer/python')

try:
    import fastapi
    print("  ✅ fastapi")
except Exception as e:
    print(f"  ❌ fastapi: {e}")
    sys.exit(1)

try:
    import boto3
    print("  ✅ boto3")
except Exception as e:
    print(f"  ❌ boto3: {e}")
    sys.exit(1)

try:
    import pydantic
    print("  ✅ pydantic")
except Exception as e:
    print(f"  ❌ pydantic: {e}")
    sys.exit(1)

try:
    import mangum
    print("  ✅ mangum")
except Exception as e:
    print(f"  ❌ mangum: {e}")
    sys.exit(1)

print("")
print("✅ All critical imports verified")
EOF

if [ $? -ne 0 ]; then
    echo "❌ Import verification failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Lambda Layer Ready!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Navigate to CDK directory:"
echo "   cd infrastructure/cdk-clean"
echo ""
echo "2. Deploy the updated stack:"
echo "   cdk deploy NeuroAgentStack"
echo ""
echo "3. Test Lambda function:"
echo "   aws lambda invoke --function-name NeuroAgentAPI \\"
echo "     --payload file://../../archive/testing_artifacts/test_lambda_event.json \\"
echo "     response.json"
echo ""
echo "4. Check response:"
echo "   cat response.json"
echo ""
echo "=========================================="
