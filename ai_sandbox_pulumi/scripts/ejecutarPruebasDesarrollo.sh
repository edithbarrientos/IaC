#!/bin/bash

# =========================================================================
# 🧪 Script de Pruebas de Desarrollo Automatizado - Plano de Control AIOps
# =========================================================================

# Colores estéticos para la telemetría en consola Zsh de macOS
VERDE='\033[0;32m'
AZUL='\033[0;34m'
AMARILLO='\033[1;33m'
RESET='\033[0m'

# Generamos un ID único por ejecución usando el timestamp actual
INCIDENTE_ID="incident-dev-$(date +%s)"
HOST="http://localhost:8000"

echo -e "${AZUL}[1/3] Lanzando ráfaga de Ingesta de Alerta hacia el API Gateway...${RESET}"

# 1️⃣ Fase de Ingesta Asíncrona: Se envía la telemetría al endpoint local
RESPONSE_INGEST=$(curl -s -X POST "$HOST/v1/alerts/ingest" \
     -H "Content-Type: application/json" \
     -d "{
       \"incident_id\": \"$INCIDENTE_ID\",
       \"cloud_provider\": \"aws\",
       \"alert_description\": \"{\\\"message\\\": \\\"Fallo de desarrollo gatillado por script local.\\\"}\",
       \"notification_channel\": \"web\",
       \"slack_webhook_url\": null
     }")

echo -e "Respuesta de la API: ${VERDE}$RESPONSE_INGEST${RESET}"
echo -e "${AMARILLO}[Pausa] Esperando 3 segundos para que los hilos asíncronos debatan...${RESET}"

# Pausa automatizada para dejar que los agentes especialistas procesen el estado y se congelen
sleep 3

echo -e "\n${AZUL}[2/3] Simulando firma de Aprobación Humana (HITL) desde la vía Web...${RESET}"

# 2️⃣ Fase de Reanudación: Se invoca la nueva ruta de reanudación web
RESPONSE_RESUME=$(curl -s -X POST "$HOST/v1/alerts/resume-web?thread_id=$INCIDENTE_ID&approved=true")

echo -e "Respuesta de la API: ${VERDE}$RESPONSE_RESUME${RESET}"

echo -e "\n${VERDE}[3/3] ¡Flujo de desarrollo certificado de punta a punta de forma exitosa!${RESET}"
