# Açai Stock

Sistema completo de gestão de estoque para açaiterias com IA interna (100% local), multi-tenant, e 3 modos de uso.

## Modos de Uso

| Modo | Plataforma | Banco | Acesso | Ideal para |
|------|-----------|-------|--------|------------|
| 🖥️ **Desktop (.exe)** | Windows | SQLite local | Localhost | Cliente final, sem internet |
| 💻 **Desenvolvimento** | Python | SQLite | Localhost | Desenvolvedor |
| ☁️ **Web (Azure)** | Azure App Service | Azure SQL | Qualquer dispositivo | Produção, multi-usuário |

---

## 🖥️ Modo Desktop (.exe) — Para Clientes

> O cliente NÃO precisa instalar Python, Django ou qualquer dependência.

### Requisitos
- Windows 10/11 (64 bits)
- Nenhum software adicional

### Como usar
1. Extraia o `AcaiStock.zip` em qualquer pasta
2. Execute `AcaiStock.exe`
3. O navegador abre automaticamente em `http://127.0.0.1:8000/`
4. Login: `admin` / Senha: `Admin123!`

### Como gerar o .exe
```bash
build.bat
```
O executável será gerado em `dist/AcaiStock/AcaiStock.exe`.

---

## 💻 Modo Desenvolvimento — Para Desenvolvedores

### Requisitos
- Python 3.12
- Redis (opcional, para Celery)

### Setup
```bash
# Ambiente virtual
python -m venv venv
venv\Scripts\activate

# Dependencias
pip install -r backend/requirements.txt

# Migracoes
cd backend
python manage.py migrate --settings=config.settings.development

# Superusuario (opcional, ja existe admin/Admin123!)
python manage.py createsuperuser

# Servidor
python manage.py runserver

# (Opcional) Celery + Redis para tarefas async
celery -A config worker -l info
celery -A config beat -l info
```

### Acessos
- **Sistema**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/
- **API docs**: http://localhost:8000/api/docs/
- Login: `admin` / `Admin123!`

### Testes
```bash
cd backend
python manage.py test
```

---

## ☁️ Modo Web (Azure) — Para Produção

> O sistema roda na nuvem, acessível de qualquer lugar por qualquer dispositivo.

### 1. Criar recursos no Azure
```bash
az group create --name rg-acai-stock --location brazilsouth
az acr create --resource-group rg-acai-stock --name acaistockregistry --sku Basic
az appservice plan create --name plan-acai-stock --resource-group rg-acai-stock --sku B1 --is-linux
az webapp create --name acai-stock --resource-group rg-acai-stock --plan plan-acai-stock -r "python:3.12"
az sql server create --name sql-acaiteria --resource-group rg-acai-stock --location brazilsouth --admin-user acaiadmin --password "Santos3@"
az sql db create --resource-group rg-acai-stock --server sql-acaiteria --name acaiteria-stock --service-objective Basic
az redis create --name redis-acai-stock --resource-group rg-acai-stock --location brazilsouth --sku Basic
```

### 2. Configurar variaveis no App Service
```bash
az webapp config appsettings set --name acai-stock --resource-group rg-acai-stock \
  --settings \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY="sua-chave-segura" \
    DEBUG=False \
    ALLOWED_HOSTS="acai-stock.azurewebsites.net" \
    AZURE_SQL_SERVER="sql-acaiteria.database.windows.net" \
    AZURE_SQL_DATABASE="acaiteria-stock" \
    AZURE_SQL_USER="acaiadmin" \
    AZURE_SQL_PASSWORD="Santos3@" \
    CELERY_BROKER_URL="redis://..." \
    EMAIL_HOST="smtp.gmail.com" \
    EMAIL_HOST_USER="seu-email@gmail.com" \
    EMAIL_HOST_PASSWORD="sua-senha-app" \
    DEFAULT_FROM_EMAIL="suporte@acaistock.com"
```

### 3. Deploy via GitHub Actions (automatico)
O arquivo `.github/workflows/deploy.yml` faz deploy automatico a cada push no branch `main`.

**Configuracao unica:** Adicione os secrets no GitHub (`Settings > Secrets and variables > Actions`):

| Secret | Descricao |
|--------|-----------|
| `AZURE_CREDENTIALS` | Service Principal JSON (`az ad sp create-for-rbac --name acai-stock-cd --role contributor --scope /subscriptions/SUBSCRIPTION_ID/resourceGroups/rg-acai-stock --sdk-auth`) |
| `REGISTRY_USERNAME` | Nome do ACR (ex: `acaistockregistry`) |
| `REGISTRY_PASSWORD` | `az acr credential show --name acaistockregistry --query "passwords[0].value" -o tsv` |
| `DJANGO_SECRET_KEY` | Chave secreta Django |
| `AZURE_SQL_SERVER` | `sql-acaiteria.database.windows.net` |
| `AZURE_SQL_DATABASE` | `acaiteria-stock` |
| `AZURE_SQL_USER` | `acaiadmin` |
| `AZURE_SQL_PASSWORD` | Senha do banco |
| `CELERY_BROKER_URL` | `rediss://:KEY@redis-acai-stock.redis.cache.windows.net:6380/0` |
| `CELERY_RESULT_BACKEND` | Mesma URL do broker |
| `EMAIL_HOST_USER` | Email para envio |
| `EMAIL_HOST_PASSWORD` | Senha de app do email |
| `DEFAULT_FROM_EMAIL` | `suporte@acaistock.com` |

---

## Arquitetura

```
                      ┌──────────────────────┐
                      │   Django + Gunicorn   │
                      │  config.settings.prod │
                      └──────┬───────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
      ┌────────────┐ ┌────────────┐ ┌────────────┐
      │  Azure SQL  │ │   Redis    │ │  Celery    │
      │  Database   │ │   Cache    │ │  Workers   │
      └────────────┘ └────────────┘ └────────────┘
                                         │
                                   ┌─────┴─────┐
                                   │  AI Engine │
                                   │ (internal) │
                                   └───────────┘
```

### AI Engine (100% local)
- **engine.py**: Analise estatistica (media movel, tendencia, previsao de demanda, financeiro)
- **nlg.py**: Geracao de relatorios em portugues
- **chatbot.py**: Chat com analise de dados
- **knowledge_base.py**: Compila dados do tenant para contexto
- **graph.py**: Orquestracao LangGraph dos fluxos

### Stack
| Componente | Tecnologia |
|-----------|-----------|
| Backend | Django 5.0 + Python 3.12 |
| Database | SQLite (dev/exe) / Azure SQL (prod) |
| Task Queue | Celery + Redis |
| AI | Engine estatistico interno (sem APIs externas) |
| Frontend | Django Templates + Chart.js |
| Auth | Session + JWT (DRF) |
| API | Django REST Framework + Swagger |
| Notificacoes | Email (SMTP) + In-app |
| CI/CD | GitHub Actions |
| Container | Docker |
| Portable | PyInstaller (.exe) |

---

## Funcionalidades

### Estoque
- Cadastro de produtos (SKU, codigo de barras, categoria)
- Controle de estoque minimo/maximo com alertas
- Rastreamento de validade de pereciveis
- Movimentacoes (entrada, saida, ajuste, perda)
- Fornecedores e pedidos de compra

### Inteligencia Artificial
- Relatorios inteligentes (geral, previsao, financeiro, validade, fornecedores)
- Previsao de demanda por produto
- Chat com IA para consultas em linguagem natural
- Exportacao de relatorios em PDF

### Multi-tenant
- Clientes (tenants) isolados com seus proprios dados
- Controle de assinaturas e pagamentos
- Bloqueio automatico de inadimplentes
- Roles: superadmin, admin, manager, staff

### API REST
- Endpoints para todas as entidades
- Autenticacao JWT
- Rate limiting
- Documentacao Swagger/OpenAPI
- Filtros, ordenacao, paginacao

### Interface
- Tema light/dark por usuario
- Sidebar com navegacao completa
- Dashboards com graficos Chart.js
- PWA (instalavel no celular/desktop)
- Notificacoes in-app com badge em tempo real
- Design responsivo

---

## Estrutura do Projeto

```
ProjetoAcai/
├── .github/workflows/
│   ├── ci.yml           # Testes automaticos
│   └── deploy.yml       # Deploy no Azure (automatico)
├── backend/
│   ├── config/settings/
│   │   ├── base.py       # Configuracao compartilhada
│   │   ├── development.py # Dev (SQLite)
│   │   ├── production.py  # Azure SQL
│   │   └── portable.py    # .exe (SQLite local)
│   ├── accounts/         # Usuarios, auth, tema
│   ├── tenants/          # Multi-tenant + middleware bloqueio
│   ├── subscriptions/    # Assinaturas e pagamentos
│   ├── inventory/        # Produtos, estoque, fornecedores
│   ├── ai_engine/        # IA interna (engine + nlg + chatbot)
│   ├── reports/          # Relatorios e PDF
│   ├── api/              # REST API (DRF)
│   ├── billing/          # Cobranca e notificacoes
│   ├── notifications/    # Notificacoes in-app e email
│   ├── templates/        # Django templates
│   ├── static/           # CSS, JS, imagens, PWA
│   ├── launcher.py       # Entry point do .exe
│   ├── Dockerfile        # Container web
│   ├── Dockerfile.celery # Container worker
│   └── requirements.txt
├── docs/
│   ├── deploy-azure.md   # Deploy manual no Azure
│   ├── azure-sql-setup.md # Config Azure SQL
│   └── build-exe.md      # Guia do .exe
├── acai_stock.spec       # PyInstaller spec
├── docker-compose.yml    # Docker local
├── build.bat             # Script build .exe
├── prd.md                # Documento de requisitos
└── README.md
```

---

## Licenciamento

O sistema controla acesso por assinatura. Clientes inadimplentes sao bloqueados automaticamente.

- **Free**: 1 usuario, 50 produtos
- **Basico**: 3 usuarios, 200 produtos
- **Profissional**: 10 usuarios, 1000 produtos
- **Empresarial**: Ilimitado

---

## Links

- **GitHub**: https://github.com/DevFbz/acai-stock
- **Documentacao**: `docs/`
- **PRD**: `prd.md`
