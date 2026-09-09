#!/bin/bash

# =========================================================================
# 🧹 Limpieza Forense y Restauración de Red - Pruebas de Desarrollo
# =========================================================================

# Colores estéticos para la telemetría en consola Zsh de macOS
VERDE='\033[0;32m'
AZUL='\033[0;34m'
AMARILLO='\033[1;33m'
RESET='\033[0m'

echo -e "${AZUL}[1/3] Removiendo DNS de desarrollo del archivo /etc/hosts...${RESET}"

# Removemos de forma segura y atómica las líneas vinculadas al sandbox local
sudo sed -i '' '/edithbaga.local/d' /etc/hosts
sudo sed -i '' '/sandbox.local/d' /etc/hosts
sudo sed -i '' '/aiops.local/d' /etc/hosts

echo -e "${VERDE}✓ DNS locales de desarrollo eliminados con éxito.${RESET}"

echo -e "\n${AZUL}[2/3] Deshabilitando el redireccionador de paquetes pfctl de Apple...${RESET}"

# Apagamos el filtro de paquetes nativo de macOS para liberar el puerto 80
sudo pfctl -d 2>/dev/null

echo -e "${VERDE}✓ Filtro de paquetes deshabilitado y puerto 80 restaurado.${RESET}"

echo -e "\n${AZUL}[3/3] Limpiando sockets y procesos de Python en el puerto 8000...${RESET}"

# Purgamos de la memoria RAM cualquier proceso colgado de Uvicorn o FastAPI
PID_ZOMBI=$(lsof -t -i:8000)
if [ ! -z "$PID_ZOMBI" ]; then
    sudo kill -9 $PID_ZOMBI 2>/dev/null
    echo -e "${VERDE}✓ Sockets purgados y puerto 8000 completamente libre.${RESET}"
else
    echo -e "${AMARILLO}ℹ No se detectaron procesos zombis activos bloqueando el puerto 8000.${RESET}"
fi

echo -e "\n${VERDE}✨ [Éxito] Tu entorno de desarrollo ha sido restaurado de forma limpia.${RESET}"
