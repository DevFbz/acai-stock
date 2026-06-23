#!/bin/bash
# Script de deploy para Azure App Service
# Uso: ./deploy.sh

set -e

echo "=== Deploy Acai Stock ==="

# 1. Build das imagens
echo "1. Building Docker images..."
docker-compose build

# 2. Migracoes
echo "2. Running migrations..."
docker-compose run --rm web python manage.py migrate --noinput

# 3. Collect static
echo "3. Collecting static files..."
docker-compose run --rm web python manage.py collectstatic --noinput

# 4. Iniciar servicos
echo "4. Starting services..."
docker-compose up -d

echo "=== Deploy concluido! ==="
echo "Web: http://localhost:8000"
echo "Admin: http://localhost:8000/admin/"
