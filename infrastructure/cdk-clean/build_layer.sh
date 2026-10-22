#!/usr/bin/env bash
# Build Lambda-compatible wheels without starting Docker or AWS resources.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LAYER_DIR="$REPO_ROOT/infrastructure/cdk-clean/build/lambda_layer/python"
if [[ -d "$LAYER_DIR" ]]; then
  echo "Layer output already exists. Remove that generated build directory before rebuilding." >&2
  exit 1
fi
mkdir -p "$LAYER_DIR"
if command -v uv >/dev/null 2>&1; then
  uv pip install --python-version 3.11 --python-platform x86_64-manylinux2014 \
    --only-binary :all: --target "$LAYER_DIR" -r "$REPO_ROOT/requirements-lambda.txt"
else
  python -m pip install --platform manylinux2014_x86_64 --implementation cp \
    --python-version 3.11 --abi cp311 --only-binary=:all: \
    --target "$LAYER_DIR" -r "$REPO_ROOT/requirements-lambda.txt"
fi
printf 'Layer prepared at %s\n' "$LAYER_DIR"
