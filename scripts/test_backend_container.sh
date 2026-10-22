#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
IMAGE="neuroagent-backend-tests:local"
# A whitelisted context avoids local caches, credentials, frontend dependencies
# and the production .dockerignore's intentional omission of test sources.
COPYFILE_DISABLE=1 tar --no-xattrs --exclude='__pycache__' --exclude='*.pyc' -cf - \
  Dockerfile.test requirements-lambda.txt requirements-test.in backend tests data pyproject.toml \
  | docker build -f Dockerfile.test -t "$IMAGE" -
mkdir -p reports
docker run --rm --network none \
  -e AWS_EC2_METADATA_DISABLED=true -e AWS_REGION=us-east-1 \
  -e AWS_DEFAULT_REGION=us-east-1 -e AWS_ACCESS_KEY_ID=testing \
  -e AWS_SECRET_ACCESS_KEY=testing -v "$ROOT/reports:/reports" "$IMAGE"
