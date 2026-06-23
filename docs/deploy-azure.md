# Deploy no Azure App Service

## Opcao 1: Azure Container Registry + App Service

### 1. Criar recursos no Azure
```bash
# Resource group
az group create --name rg-acai-stock --location brazilsouth

# Container Registry
az acr create --resource-group rg-acai-stock --name acaistockregistry --sku Basic

# App Service Plan
az appservice plan create --name plan-acai-stock --resource-group rg-acai-stock --sku B1 --is-linux

# Web App
az webapp create --name acai-stock --resource-group rg-acai-stock --plan plan-acai-stock --deployment-container-image-name acaistockregistry.azurecr.io/acai-stock:latest

# Redis Cache
az redis create --name redis-acai-stock --resource-group rg-acai-stock --location brazilsouth --sku Basic
```

### 2. Build e push da imagem
```bash
az acr login --name acaistockregistry

docker build -t acaistockregistry.azurecr.io/acai-stock:latest ./backend
docker push acaistockregistry.azurecr.io/acai-stock:latest
```

### 3. Configurar env vars no App Service
```bash
az webapp config appsettings set --name acai-stock --resource-group rg-acai-stock \
  --settings \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=sua-secret-key-producao \
    DEBUG=False \
    ALLOWED_HOSTS=seu-dominio.azurewebsites.net \
    CELERY_BROKER_URL=redis://redis-acai-stock.redis.cache.windows.net:6379/0 \
    AZURE_SQL_SERVER=sql-acaiteria.database.windows.net \
    AZURE_SQL_DATABASE=acaiteria_stock \
    AZURE_SQL_USER=acaiadmin \
    AZURE_SQL_PASSWORD=sua-senha \
    EMAIL_HOST=smtp.gmail.com \
    EMAIL_HOST_USER=seu-email@gmail.com \
    EMAIL_HOST_PASSWORD=sua-senha-app
```

### 4. Configurar deploy continuo
```bash
az webapp config container set --name acai-stock --resource-group rg-acai-stock \
  --docker-registry-server-url https://acaistockregistry.azurecr.io \
  --docker-registry-server-user acaistockregistry \
  --docker-registry-server-password sua-senha-registry \
  --docker-custom-image-name acaistockregistry.azurecr.io/acai-stock:latest
```

## Opcao 2: GitHub Actions (CI/CD automatico)

O workflow em `.github/workflows/ci.yml` roda testes a cada push.
Para deploy automatico, adicione suas credenciais Azure como secrets no GitHub:

- `AZURE_CREDENTIALS` - service principal JSON
- `AZURE_REGISTRY_NAME` - nome do registry
- `AZURE_REGISTRY_PASSWORD` - senha do registry

## Migracao de SQLite para Azure SQL

1. Crie o Azure SQL Database (veja docs/azure-sql-setup.md)
2. Configure as credenciais no .env de producao
3. Rode: `python manage.py migrate`
4. (Opcional) Migre dados: `python manage.py dumpdata > backup.json` (SQLite) -> `python manage.py loaddata backup.json` (Azure SQL)

## Celery em producao

Para rodar Celery no Azure, use uma das opcoes:
- Azure Container Apps (recomendado)
- Azure Container Instances
- Maquina virtual separada

O docker-compose.yml inclui celery, celery-beat e redis para deploy local/staging.
