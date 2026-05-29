#!/bin/sh

echo "Waiting for postgres..."

until pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done

echo "Postgres started"

exec uvicorn main:app --host 0.0.0.0 --port 8000