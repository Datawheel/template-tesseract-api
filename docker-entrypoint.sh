#!/usr/bin/env bash

MAX_CONCURRENCY=${MAX_CONCURRENCY:-300}
PORT=${PORT:-7777}
WORKERS=${UVICORN_WORKERS:-1}  # Default to 1 if not set, for the cluster.

exec uvicorn \
  --host 0.0.0.0 \
  --port $PORT \
  --limit-concurrency $MAX_CONCURRENCY \
  --log-config ./etc/logging.json \
  --workers $WORKERS \
  app:layer
