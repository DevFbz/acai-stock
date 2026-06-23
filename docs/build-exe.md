# Build do .exe Portátil

Gera um executável Windows que roda o Django sem precisar instalar Python.

## Requisitos
- Windows 10/11
- Python 3.12
- Ambiente virtual com dependências instaladas

## Como Buildar

### 1. Preparar ambiente
```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
pip install pyinstaller
```

### 2. Executar build
```bash
build.bat
```

Ou manualmente:
```bash
cd backend
python manage.py collectstatic --noinput --settings=config.settings.portable
cd ..
pyinstaller acai_stock.spec --noconfirm
```

### 3. Resultado
O executável é gerado em:
```
dist/AcaiStock/AcaiStock.exe
```

## Distribuição
1. Compacte a pasta `dist/AcaiStock` em um arquivo `.zip`
2. Envie para o cliente
3. O cliente extrai e executa `AcaiStock.exe`
4. Navegador abre automaticamente em `http://127.0.0.1:8000/`

## Funcionamento do .exe
- Cria um banco SQLite (`acai_stock.db`) ao lado do executável
- Roda migrações automaticamente na primeira execução
- Cria usuário admin: `admin` / `Admin123!`
- Abre o navegador após 3 segundos
- Servidor roda em `127.0.0.1:8000`

## Notas
- O .exe usa `config.settings.portable` (SQLite, sem Redis, tarefas síncronas)
- Para produção multiusuário, use o modo Azure Web
- O .exe é autocontido — não precisa de Python, Django ou dependências
