#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run database migrations if needed
python -c "from app.database import init_db; init_db()"

# Start Gunicorn with Uvicorn workers
gunicorn app.main:app \
    --config gunicorn_config.py \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
