#!/bin/bash
# 🌌 SCRIPT FORENSE INTEGRAL: INYECTOR gRPC REAL PARA PLATAFORMA DISTRIBUIDA

echo -e "\033[1;36m[1/3] Despachando ráfaga forense real de gRPC hacia el plano distribuido...\033[0m"

# 🚀 INYECCIÓN REAL DETERMINISTA: Iniciamos el workflow con un ID estático limpio de desarrollo
temporal workflow start \
  --workflow-id "incident-dev-temporal-sandbox-id" \
  --type "IncidentMitigationWorkflow" \
  --task-queue "aiops-incident-task-queue" \
  --input "\"Alerta Crítica: Anomalía de handshake detectada en el API Gateway corporativo.\""

echo -e "\n\033[1;36m[2/3] Interceptando canal de señales gRPC para inyección humana (HITL)...\033[0m"
sleep 1

# 🚀 SEÑAL REAL gRPC: Envía la aprobación humana inmutable directo a la base de datos distribuida
temporal workflow signal \
  --workflow-id "incident-dev-temporal-sandbox-id" \
  --name "receive_human_approval" \
  --input "true"

echo -e "\n\033[1;36m[3/3] Recuperando traza forense consolidada del clúster...\033[0m"
sleep 1

# Muestra el resultado real y crudo del cierre de la Saga transaccional de Temporal
temporal workflow show --workflow-id "incident-dev-temporal-sandbox-id"
