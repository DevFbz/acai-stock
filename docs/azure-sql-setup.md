# Azure SQL Database - Guia de Configuração

Este guia explica como criar e configurar o Azure SQL Database para o sistema de estoque da açaiteria.

## Passo 1: Acessar o Portal do Azure

1. Acesse **https://portal.azure.com**
2. Faça login com sua conta Microsoft (se não tiver, crie uma - tem tier gratuito)

## Passo 2: Criar o SQL Database

1. No menu superior, clique em **"Create a resource"**
2. Pesquise por **"SQL Database"** e clique em **Create**
3. Preencha os campos:

| Campo                | Valor recomendado                          |
|----------------------|--------------------------------------------|
| **Subscription**     | Sua subscription (free ou pay-as-you-go)   |
| **Resource group**   | `rg-acaiteria` (crie novo)                 |
| **Database name**    | `acaiteria_stock`                          |
| **Server**           | Clique em "Create new"                     |
| **Server name**      | `sql-acaiteria` (nome único global)        |
| **Server admin login** | `acaiadmin`                              |
| **Password**         | Uma senha forte (anote!)                   |
| **Location**         | `Brazil South` (mais próximo)              |
| **Compute + storage**| **Basic** (mais barato, ~R$15/mês)         |

## Passo 3: Configurar Acesso de Rede

1. Após criar, vá para o SQL Server (não o database)
2. No menu lateral: **Security → Networking**
3. Em **Firewall rules**, adicione:
   - **Client IP**: clique em "Add your client IPv4 address"
   - **Allow Azure services**: marque como **Yes** (importante para Celery/functions)

## Passo 4: Obter a Connection String

1. No SQL Database criado, vá em **Settings → Connection strings**
2. Copie a string no formato **ADO.NET** ou **JDBC**
3. Terá este formato:

```
Server=tcp:sql-acaiteria.database.windows.net,1433;Initial Catalog=acaiteria_stock;User ID=acaiadmin;Password=SUA_SENHA;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;
```

## Passo 5: Configurar no Projeto

Após obter as credenciais, configure no arquivo `.env`:

```env
# Azure SQL Database (Produção)
AZURE_SQL_SERVER=sql-acaiteria.database.windows.net
AZURE_SQL_DATABASE=acaiteria_stock
AZURE_SQL_USER=acaiadmin
AZURE_SQL_PASSWORD=SUA_SENHA
AZURE_SQL_PORT=1433
```

### Driver necessário

Para conectar ao Azure SQL a partir do Django, será necessário instalar o driver `mssql-django`:

```bash
pip install mssql-django
```

E configurar o `DATABASES` no settings de produção:

```python
DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": env("AZURE_SQL_DATABASE"),
        "USER": env("AZURE_SQL_USER"),
        "PASSWORD": env("AZURE_SQL_PASSWORD"),
        "HOST": env("AZURE_SQL_SERVER"),
        "PORT": env("AZURE_SQL_PORT"),
        "OPTIONS": {
            "driver": "ODBC Driver 17 for SQL Server",
            "extra_params": "Encrypt=yes;TrustServerCertificate=no;",
        },
    }
}
```

## Migração de SQLite para Azure SQL

Quando estiver pronto para migrar de SQLite (desenvolvimento) para Azure SQL (produção):

1. Instale o driver: `pip install mssql-django`
2. Configure as variáveis no `.env`
3. Rode `python manage.py migrate` para criar as tabelas no Azure
4. Use `python manage.py loaddata backup.json` se quiser migrar dados
5. Teste a conexão: `python manage.py dbshell`

## Custos Estimados

| Tier       | Custo aproximado | Recursos                          |
|------------|------------------|-----------------------------------|
| **Basic**  | ~R$15/mês        | 5 DTUs, 2GB storage               |
| **S0**     | ~R$75/mês        | 10 DTUs, 250GB storage            |
| **S1**     | ~R$150/mês       | 20 DTUs, 250GB storage            |

Para desenvolvimento e uso inicial, o tier **Basic** é suficiente.
