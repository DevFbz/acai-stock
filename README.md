# Açaí Stock - Sistema de Gestão de Estoque para Açaiteria

Sistema completo de controle de estoque e monitoramento para açaiterias, com IA integrada para relatórios inteligentes.

## Stack Tecnológica

- **Backend**: Django 5.0 + Python 3.12
- **Task Queue**: Celery + Redis
- **IA**: LangChain + LangGraph (OpenAI)
- **Database**: SQLite (dev) / Azure SQL Database (prod)
- **Frontend**: Django Templates + CSS custom (light/dark theme)

## Funcionalidades

### Gestão de Estoque
- Cadastro de produtos com SKU, código de barras e categorias
- Controle de estoque mínimo/máximo com alertas
- Rastreamento de validade de produtos perecíveis
- Movimentações de estoque (entrada, saída, ajuste, perda)
- Gestão de fornecedores
- Pedidos de compra

### Inteligência Artificial
- Relatórios gerados por IA usando LangChain + LangGraph
- Análise automática de estoque
- Recomendações de otimização
- Previsão de demanda

### Controle de Acesso Multi-Tenant
- Multi-tenant (múltiplas açaiterias)
- Controle de assinaturas e pagamentos
- Bloqueio automático de clientes que não pagaram
- Roles: Super Admin, Administrador, Gerente, Funcionário
- Tema light/dark por usuário

## Estrutura do Projeto

```
ProjetoAcai/
├── backend/
│   ├── config/              # Configuração Django + Celery
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── celery.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── accounts/            # Usuários, auth, tema
│   ├── tenants/             # Multi-tenant + middleware de bloqueio
│   ├── subscriptions/       # Assinaturas e pagamentos
│   ├── inventory/           # Produtos, estoque, fornecedores, POs
│   ├── reports/             # Relatórios
│   ├── ai_engine/           # LangChain + LangGraph
│   ├── templates/           # Templates Django
│   ├── static/              # CSS, JS, imagens
│   ├── requirements.txt
│   ├── .env
│   └── manage.py
├── docs/
│   └── azure-sql-setup.md
├── prd.md
├── .gitignore
└── README.md
```

## Como Rodar (Desenvolvimento)

```bash
# 1. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r backend/requirements.txt

# 3. Configurar .env
cp backend/.env.example backend/.env  # Editar conforme necessário

# 4. Migrar banco
cd backend
python manage.py migrate

# 5. Criar superusuário
python manage.py createsuperuser

# 6. Rodar servidor
python manage.py runserver
```

## Migrar para Azure SQL (Produção)

Veja as instruções em `docs/azure-sql-setup.md`.

## Acesso

- **Admin Django**: http://localhost:8000/admin/
- **Sistema**: http://localhost:8000/
- **Login**: admin / Admin123! (desenvolvimento)

## Próximos Passos (Sprints Futuros)

- [ ] Sprint 2: CRUD completo de produtos via interface (não só admin)
- [ ] Sprint 3: Dashboards avançados e gráficos
- [ ] Sprint 4: API REST completa
- [ ] Sprint 5: Deploy em produção (Azure App Service)
- [ ] Sprint 6: Notificações em tempo real (WebSockets)
- [ ] Sprint 7: App mobile
