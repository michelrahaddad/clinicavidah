@echo off
echo ====================================
echo    Sistema Médico VIDAH - Windows
echo ====================================
echo.

REM Ativar ambiente virtual
if exist venv\Scripts\activate (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate
) else (
    echo ERRO: Ambiente virtual não encontrado!
    echo Execute primeiro: python -m venv venv
    pause
    exit /b 1
)

REM Configurar variáveis de ambiente
set SESSION_SECRET=vidah-medical-system-secure-key-2024
set FLASK_ENV=production

echo Iniciando Sistema Médico VIDAH...
echo Acesse: http://localhost:5000
echo.
echo Para parar o sistema, pressione Ctrl+C
echo.

REM Iniciar aplicação
python main.py

pause