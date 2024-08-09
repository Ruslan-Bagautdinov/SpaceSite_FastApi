#!/bin/sh

wait_for_db() {
    echo "Waiting for database..."
    until pg_isready -h db -U postgres -d fastapi; do
        sleep 1
    done
    echo "Database is ready!"
}

wait_for_db

alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8000
