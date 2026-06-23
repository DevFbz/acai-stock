@echo off
echo ============================================
echo   Build Acai Stock - .exe Portable
echo ============================================
echo.

cd /d "%~dp0"

echo [1/5] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [2/5] Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/5] Coletando static files...
cd backend
python manage.py collectstatic --noinput --settings=config.settings.portable
cd ..

echo [4/5] Executando PyInstaller...
pyinstaller acai_stock.spec --noconfirm

echo [5/5] Copiando arquivos adicionais...
copy backend\.env dist\AcaiStock\.env 2>nul

echo.
echo ============================================
echo   Build concluido!
echo ============================================
echo.
echo   Arquivo: dist\AcaiStock\AcaiStock.exe
echo.
echo   Para distribuir:
echo   1. Compacte a pasta dist\AcaiStock em .zip
echo   2. Envie para o cliente
echo   3. O cliente so precisa extrair e executar
echo      AcaiStock.exe (nao precisa instalar nada)
echo.
echo   Login: admin
echo   Senha: Admin123!
echo.
pause
