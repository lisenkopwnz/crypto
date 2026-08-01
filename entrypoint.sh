#!/bin/bash
set -e


while ! nc -z db 5432; do
  sleep 1
done


echo "🔄 Creating tables..."
python -m app.create_tables

echo "🚀 Starting application..."
exec "$@"