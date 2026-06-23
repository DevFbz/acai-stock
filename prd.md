# PRD - Açaí Stock: Sistema de Gestão de Estoque para Açaiteria

## 1. Visão Geral

**Produto**: Sistema SaaS multi-tenant para gestão de estoque e monitoramento de açaiterias, com inteligência artificial integrada para geração de relatórios e insights.

**Objetivo**: Automatizar o controle de estoque, reduzir perdas por vencimento, otimizar compras e fornecer análises inteligentes via IA para donos de açaiterias.

**Modelo de Negócio**: Assinatura mensal/trimestral/anual. O sistema controla o acesso dos clientes (tenants) via pagamento — clientes que não pagam são bloqueados automaticamente.

## 2. Stack Tecnológica

| Camada        | Tecnologia                                  |
|---------------|---------------------------------------------|
| Backend       | Django 5.0 + Python 3.12                    |
| Task Queue    | Celery 5.x + Redis                          |
| IA / LLM      | LangChain 0.2 + LangGraph 0.1 + OpenAI      |
| Database      | SQLite (dev) / Azure SQL Database (prod)    |
| Frontend      | Django Templates + CSS custom               |
| Auth          | Django Auth + Session + JWT (DRF)           |
| Design        | Taste-Skill design framework (light/dark)   |

## 3. Requisitos Funcionais

### 3.1 Gestão de Estoque
- RF-01: Cadastro de produtos com nome, SKU, código de barras, categoria, unidade
- RF-02: Controle de estoque mínimo e máximo por produto
- RF-03: Registro de movimentações (entrada, saída, ajuste, perda)
- RF-04: Rastreamento de data de validade de produtos perecíveis
- RF-05: Alertas de estoque baixo e produtos vencendo
- RF-06: Gestão de fornecedores (CRUD)
- RF-07: Pedidos de compra com itens e status
- RF-08: Dashboard com métricas em tempo real

### 3.2 Inteligência Artificial
- RF-09: Geração de relatórios inteligentes via LangChain + LangGraph
- RF-10: Análise automática de padrões de consumo
- RF-11: Recomendações de reposição de estoque
- RF-12: Previsão de demanda por produto
- RF-13: Detecção de produtos com risco de vencimento
- RF-14: Relatórios personalizados por solicitação

### 3.3 Controle de Acesso e Assinaturas
- RF-15: Multi-tenant (cada açaiteria é um tenant isolado)
- RF-16: Roles: Super Admin, Administrador, Gerente, Funcionário
- RF-17: Gestão de assinaturas (planos: Free, Básico, Profissional, Empresarial)
- RF-18: Registro de pagamentos e vencimentos
- RF-19: Bloqueio automático de tenants com pagamento em atraso
- RF-20: Middleware que redireciona usuários bloqueados para tela de bloqueio
- RF-21: Reativação manual de tenant após pagamento

### 3.4 Interface
- RF-22: Painel lateral com navegação para todas as funcionalidades
- RF-23: Tema light e dark com toggle persistido por usuário
- RF-24: Design responsivo (desktop e mobile)
- RF-25: Login com tela personalizada
- RF-26: Tela de bloqueio com informações de contato

## 4. Requisitos Não-Funcionais

- RNF-01: Tempo de resposta da API < 200ms
- RNF-02: Disponibilidade de 99.9% em produção
- RNF-03: Dados isolados por tenant (segurança multi-tenant)
- RNF-04: Senhas com hash (PBKDF2)
- RNF-05: CSRF protection em todos os formulários
- RNF-06: Suporte a pt-BR e fuso America/Sao_Paulo

## 5. Arquitetura

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Frontend    │    │   Django     │    │   Celery     │
│  (Templates) │◄──►│   Views      │◄──►│   Workers    │
└──────────────┘    └──────────────┘    └──────────────┘
                           │                    │
                    ┌──────────────┐    ┌──────────────┐
                    │   Database   │    │  LangChain   │
                    │  Azure SQL   │    │  + LangGraph │
                    └──────────────┘    └──────────────┘
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

## 7. Sprints

### Sprint 1: Fundação (Concluído)
**Período**: Semana 1-2

**Entregas**:
- [x] Estrutura Django com settings split (base/dev/prod)
- [x] App tenants com modelo Tenant e middleware de bloqueio
- [x] App accounts com User customizado (role, tenant, theme)
- [x] App subscriptions com Subscription e Payment
- [x] App inventory com Product, Category, Supplier, StockMovement, PurchaseOrder
- [x] App reports com modelo Report
- [x] App ai_engine com LangChain + LangGraph (grafo de relatório)
- [x] Celery configurado com Redis
- [x] Templates base com sidebar, topbar, light/dark theme
- [x] Tela de login e tela de bloqueio
- [x] Dashboard com métricas (estoque baixo, vencidos, movimentações)
- [x] Listagem de produtos, fornecedores, movimentações, pedidos
- [x] Admin Django configurado com actions de bloqueio/reativação
- [x] .env e .gitignore
- [x] Guia de configuração Azure SQL

### Sprint 2: CRUD Completo via Interface
**Período**: Semana 3-4

**Entregas**:
- [ ] Formulários de criação/edição de produtos via interface
- [ ] Formulários de fornecedores
- [ ] Formulários de movimentações de estoque
- [ ] Formulários de pedidos de compra
- [ ] Página de detalhe de produto com histórico
- [ ] Busca e filtros avançados
- [ ] Exportação CSV/Excel
- [ ] Validações de negócio

### Sprint 3: Dashboards e Gráficos
**Período**: Semana 5-6

**Entregas**:
- [ ] Gráficos de consumo (Chart.js)
- [ ] Gráfico de movimentações por período
- [ ] Heatmap de validade
- [ ] Ranking de produtos mais movimentados
- [ ] Indicadores financeiros (valor em estoque)
- [ ] Filtros por período
- [ ] Cards de KPIs animados

### Sprint 4: IA Avançada
**Período**: Semana 7-8

**Entregas**:
- [ ] Previsão de demanda por produto
- [ ] Otimização de ponto de reposição
- [ ] Detecção de anomalias em consumo
- [ ] Relatório de desempenho de fornecedores
- [ ] Relatórios agendados via Celery Beat
- [ ] Chat com IA para consultas em linguagem natural
- [ ] Exportação de relatórios em PDF

### Sprint 5: API REST e Integrações
**Período**: Semana 9-10

**Entregas**:
- [ ] API REST completa com DRF
- [ ] Endpoints para todas as entidades
- [ ] Autenticação JWT
- [ ] Rate limiting
- [ ] Documentação OpenAPI/Swagger
- [ ] Webhooks de pagamento
- [ ] Integração com gateway de pagamento

### Sprint 6: Deploy e Produção
**Período**: Semana 11-12

**Entregas**:
- [ ] Migração para Azure SQL Database
- [ ] Deploy no Azure App Service
- [ ] Configuração de Redis no Azure
- [ ] CI/CD com GitHub Actions
- [ ] Monitoramento e logs
- [ ] Backup automático
- [ ] SSL e domínio
- [ ] Testes automatizados

### Sprint 7: Notificações e Tempo Real
**Período**: Semana 13-14

**Entregas**:
- [ ] Django Channels + WebSockets
- [ ] Notificações em tempo real de estoque baixo
- [ ] Alertas de validade
- [ ] Notificações por e-mail (Celery + SMTP)
- [ ] Centro de notificações na interface

### Sprint 8: App Mobile / PWA
**Período**: Semana 15-16

**Entregas**:
- [ ] PWA com service worker
- [ ] Interface otimizada para mobile
- [ ] Leitura de código de barras
- [ ] Modo offline
- [ ] Push notifications

## 8. Critérios de Aceite

- Sistema permite criar tenant e usuário
- Usuário consegue logar e ver dashboard
- Produtos podem ser cadastrados e movimentados
- Alertas de estoque baixo aparecem no dashboard
- Admin pode bloquear tenant e usuário é redirecionado
- IA gera relatório a partir dos dados de estoque
- Tema light/dark funciona e persiste
- Interface é responsiva

## 9. Riscos e Mitigações

| Risco                        | Mitigação                              |
|------------------------------|----------------------------------------|
| Custo de IA (OpenAI)         | Cache de relatórios, modelo mais barato|
| Azure SQL indisponível       | Failover automático do Azure           |
| Pico de uso                  | Celery workers escaláveis              |
| Perda de dados               | Backup automático Azure                |
| Não pagamento de clientes    | Bloqueio automático + notificações     |
