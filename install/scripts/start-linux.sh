#!/bin/bash

echo "===================================="
echo "   Sistema Médico VIDAH - Linux"
echo "===================================="
echo

# Verificar se ambiente virtual existe
if [ -d "venv" ]; then
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "ERRO: Ambiente virtual não encontrado!"
    echo "Execute primeiro: python3 -m venv venv"
    exit 1
fi

# Configurar variáveis de ambiente
export SESSION_SECRET=vidah-medical-system-secure-key-2024
export FLASK_ENV=production

echo "Iniciando Sistema Médico VIDAH..."
echo "Acesse: http://localhost:5000"
echo
echo "Para parar o sistema, pressione Ctrl+C"
echo

# Iniciar aplicação
python3 main.py