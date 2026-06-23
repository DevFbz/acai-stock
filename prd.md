# PRD — Açaí Stock: Sistema de Gestão de Estoque para Açaiteria

## 1. Visão Geral

**Produto**: Sistema SaaS multi-tenant para gestão de estoque e monitoramento de açaiterias, com inteligência artificial interna (100% local, sem APIs externas) para geração de relatórios e insights.

**Objetivo**: Automatizar o controle de estoque, reduzir perdas por vencimento, otimizar compras e fornecer análises inteligentes via IA para donos de açaiterias.

**Modelo de Negócio**: Assinatura mensal/trimestral/anual. O sistema controla o acesso dos clientes (tenants) via pagamento — clientes que não pagam são bloqueados automaticamente.

**Modos de Uso**:
| Modo | Descrição |
|------|-----------|
| 🖥️ Desktop (.exe) | Executável Windows portátil, sem dependências. SQLite local. |
| 💻 Desenvolvimento | `python manage.py runserver`. SQLite local. |
| ☁️ Web (Azure) | Azure App Service + Azure SQL. Acessível de qualquer lugar. |

## 2. Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Django 5.0 + Python 3.12 |
| Task Queue | Celery 5.x + Redis |
| IA | Engine estatístico interno (engine.py + nlg.py + chatbot.py) — 100% local |
| Database | SQLite (dev/exe) / Azure SQL Database (prod) |
| Frontend | Django Templates + CSS custom + Chart.js |
| Auth | Django Auth + Session + JWT (DRF) |
| Design | Light/dark theme por usuário |
| Deploy | GitHub Actions CI/CD + Azure App Service |
| Container | Docker + docker-compose |
| Portable | PyInstaller (.exe) |

## 3. Requisitos Funcionais

### 3.1 Gestão de Estoque
- RF-01: Cadastro de produtos com nome, SKU, código de barras, categoria, unidade
- RF-02: Controle de estoque mínimo e máximo por produto
- RF-03: Registro de movimentações (entrada, saída, ajuste, perda)
- RF-04: Rastreamento de data de validade de produtos perecíveis
- RF-05: Alertas de estoque baixo e produtos vencendo
- RF-06: Gestão de fornecedores (CRUD)
- RF-07: Pedidos de compra com itens e status
- RF-08: Dashboard com métricas em tempo real (Chart.js)
- RF-09: Exportação de dados para CSV/Excel
- RF-10: Relatórios em PDF (reportlab)

### 3.2 Inteligência Artificial (100% local)
- RF-11: Relatório geral de estoque com análises estatísticas
- RF-12: Previsão de demanda por produto (média móvel + tendência)
- RF-13: Relatório financeiro (valor em estoque, margem, giro)
- RF-14: Relatório de produtos próximos ao vencimento
- RF-15: Relatório de desempenho de fornecedores
- RF-16: Chat com IA para consultas em linguagem natural
- RF-17: Geração automática de relatórios via Celery Beat
- RF-18: Orquestração de fluxos via LangGraph

### 3.3 Controle de Acesso e Assinaturas
- RF-19: Multi-tenant (cada açaiteria é um tenant isolado)
- RF-20: Roles: Super Admin, Administrador, Gerente, Funcionário
- RF-21: Gestão de assinaturas (planos: Free, Básico, Profissional, Empresarial)
- RF-22: Notificações de cobrança por email (3 níveis: 7/3/1 dias antes)
- RF-23: Bloqueio automático de tenants com pagamento em atraso (>7 dias)
- RF-24: Middleware que redireciona usuários bloqueados para tela de bloqueio
- RF-25: Reativação manual de tenant após pagamento

### 3.4 Interface
- RF-26: Painel lateral com navegação para todas as funcionalidades
- RF-27: Tema light e dark com toggle persistido por usuário
- RF-28: Design responsivo (desktop e mobile)
- RF-29: Login com tela personalizada
- RF-30: Tela de bloqueio com informações de contato

### 3.5 API REST
- RF-31: Endpoints para todas as entidades (DRF ViewSets)
- RF-32: Autenticação JWT
- RF-33: Rate limiting
- RF-34: Documentação Swagger/OpenAPI
- RF-35: Filtros, ordenação e paginação
- RF-36: Scoping automático por tenant

### 3.6 Notificações
- RF-37: Notificações in-app com badge em tempo real
- RF-38: Notificações por email (SMTP + Celery)
- RF-39: Tarefas agendadas (Celery Beat): verificação diária de estoque, resumo semanal
- RF-40: 3 níveis de alerta de cobrança por email

### 3.7 PWA
- RF-41: Service worker com cache offline
- RF-42: Manifest.json para instalação no dispositivo
- RF-43: Interface otimizada para mobile

### 3.8 Deploy e Portabilidade
- RF-44: .exe portátil via PyInstaller (Windows, sem dependências)
- RF-45: Docker e docker-compose para containerização
- RF-46: CI/CD via GitHub Actions (testes + deploy automático Azure)
- RF-47: Suporte a Azure SQL Database

## 4. Requisitos Não-Funcionais

- RNF-01: Tempo de resposta da API < 200ms
- RNF-02: Disponibilidade de 99.9% em produção (Azure App Service)
- RNF-03: Dados isolados por tenant (segurança multi-tenant)
- RNF-04: Senhas com hash (PBKDF2)
- RNF-05: CSRF protection em todos os formulários
- RNF-06: Suporte a pt-BR e fuso America/Sao_Paulo
- RNF-07: IA funciona offline (sem depender de APIs externas)
- RNF-08: .exe funcional sem instalar Python ou qualquer dependência

## 5. Arquitetura

```
                    ┌──────────────────────────────────┐
                    │       Azure App Service          │
                    │  ┌────────────────────────────┐  │
                    │  │    Django (Gunicorn x4)    │  │
                    │  │  config.settings.production │  │
                    │  └──────┬─────────────────────┘  │
                    └─────────┼────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │  Azure SQL   │    │    Redis     │    │   Celery     │
  │  Database    │    │    Cache     │    │  Workers     │
  └──────────────┘    └──────────────┘    └──────────────┘
                                                │
                                          ┌─────┴─────┐
                                          │ AI Engine  │
                                          │ (internal) │
                                          └───────────┘
```

### Fluxo de IA
```
User Request → LangGraph (graph.py)
                ├── ReportFlow → KnowledgeBase → engine.py (stats) → nlg.py (texto) → Response
                └── ChatFlow → chatbot.py (pattern + análise) → Response
```

## 6. Modelo de Dados

### Tenants
- id, name, slug, plan, status (active/suspended/blocked/canceled), is_active

### Users
- id, username, email, role, tenant_id, theme, phone, is_tenant_owner

### Products
- id, tenant_id, name, sku, barcode, category_id, supplier_id, unit, min_stock, max_stock, current_stock, cost_price, sale_price, expiry_date, is_active

### StockMovements
- id, product_id, movement_type, quantity, reason, reference, created_at

### Suppliers
- id, tenant_id, name, contact_person, phone, email, cnpj, address, is_active

### PurchaseOrders
- id, tenant_id, supplier_id, status, total, expected_date, received_at, notes

### Subscriptions
- id, tenant_id, plan, status, billing_cycle, amount, current_period_start, current_period_end

### Payments
- id, subscription_id, amount, status, due_date, paid_at, method, reference

### Reports
- id, tenant_id, title, report_type, content, summary, metadata, generated_by

### Notifications
- id, tenant_id, user_id, notification_type, title, message, is_read, created_at

## 7. Sprints

### Sprint 1: Fundação ✅
- Estrutura Django com settings split (base/dev/prod/portable)
- App tenants (Tenant + middleware de bloqueio)
- App accounts (User customizado: role, tenant, theme)
- App subscriptions (Subscription + Payment)
- App inventory (Product, Category, Supplier, StockMovement, PurchaseOrder)
- App reports (Report)
- App ai_engine (engine.py + nlg.py + graph.py)
- Celery configurado com Redis
- Templates base (sidebar, topbar, light/dark)
- Login + tela de bloqueio
- Dashboard com métricas
- Admin Django + actions

### Sprint 2: CRUD via Interface ✅
- Formulários de criação/edição (produtos, fornecedores, movimentações, pedidos)
- Página de detalhe de produto com histórico
- Busca e filtros avançados
- Exportação CSV/Excel

### Sprint 3: Dashboards e Gráficos ✅
- Gráficos Chart.js (movimentações, estoque, top produtos, categorias)
- Cards de KPIs
- Filtros por período

### Sprint 4: IA Avançada ✅
- Engine estatístico completo (engine.py)
- NLG de relatórios (nlg.py) em português
- Chat com IA (chatbot.py)
- Knowledge base (knowledge_base.py)
- LangGraph (graph.py) orquestrando fluxos
- 5 tipos de relatório (geral, previsão, financeiro, validade, fornecedores)
- Relatórios PDF (reportlab)
- Relatórios agendados via Celery Beat

### Sprint 5: API REST + Cobrança ✅
- DRF ViewSets para todas as entidades
- JWT authentication
- Rate limiting
- Swagger docs
- Billing com notificações por email (3 níveis)
- Auto-bloqueio após 7 dias

### Sprint 6: Notificações + PWA + Deploy + Testes ✅
- Notificações in-app com badge
- Notificações email (Celery)
- Tarefas agendadas (Celery Beat)
- PWA (manifest.json + sw.js)
- 29 testes automatizados
- Azure SQL Database configurado
- Docker + docker-compose
- GitHub Actions CI
- .exe portátil (PyInstaller)
- CI/CD com deploy automático Azure

## 8. Critérios de Aceite

- Sistema permite criar tenant e usuário
- Usuário consegue logar e ver dashboard
- Produtos podem ser cadastrados e movimentados
- Alertas de estoque baixo aparecem no dashboard
- Admin pode bloquear tenant e usuário é redirecionado
- IA gera relatório a partir dos dados de estoque
- Tema light/dark funciona e persiste
- Interface é responsiva
- API REST retorna dados corretos por tenant
- Chat responde com análise real dos dados
- .exe funciona sem instalar dependências
- Deploy automático funciona via GitHub Actions

## 9. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Custo Azure SQL | Tier Basic (~R$15/mês) |
| Azure SQL indisponível | Failover automático do Azure |
| Perda de dados | Backup automático Azure + dump SQLite |
| Clientes inadimplentes | Bloqueio automático + 3 notificações |
| .exe antimalware falso positivo | Assinar digitalmente o executável |
| Usuário sem internet | Modo .exe funciona offline |
