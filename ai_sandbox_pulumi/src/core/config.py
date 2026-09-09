"""Módulo de Ingestión de Configuración Maestra Externa.

Carga y parsea en caliente el archivo físico 'config.toml' de la raíz en cada
ciclo operativo de despliegue, garantizando que el operario pueda reescribir
el proveedor cloud o los segmentos de red tras fallos catastróficos.

Información del Módulo:
    * Autor: Edith Barrientos 💻
    * Año: 2026 🚀
"""

import os
import sys
import tomllib
from typing import Any, Dict

from loguru import logger


def load_master_config(config_path: str = "config.toml") -> Dict[str, Any]:
    """Lee y parsea el archivo TOML externo de la raíz en tiempo de ejecución.

    [PATTERN: CONFIGURATION REGISTRY]
    Garantiza que la fuente de verdad sea externa. Si el archivo no existe,
    genera un pánico controlado para forzar la existencia del manifiesto corporativo.

    Args:
        config_path (str): Ruta del archivo físico.

    Returns:
        Dict[str, Any]: Diccionario aplanado con las variables en memoria RAM.
    """
    absolute_path = os.path.abspath(config_path)

    if not os.path.exists(config_path):
        logger.critical(
            f"🔥 [Config] Archivo crítico no encontrado. "
            f"Ruta intentada: {absolute_path} | Abortando plano de control."
        )
        sys.exit(1)

    try:
        with open(config_path, "rb") as f:
            raw_data = tomllib.load(f)
            
        flat_config = {
            "environment": raw_data["global"]["environment"],
            "project_name": raw_data["global"]["pulumi_project_name"],
            "cloud_provider": raw_data["infrastructure"]["cloud_provider"].lower(),
            "cloud_region": raw_data["infrastructure"]["cloud_region"],
            "cluster_name": raw_data["infrastructure"]["cluster_name"],
            "network_control_cidr": raw_data["networking"]["network_control_cidr"],
            "network_production_cidr": raw_data["networking"]["network_production_cidr"],
            "network_vpc_name": raw_data["networking"]["network_vpc_name"],
            "apisix_gateway_host": raw_data["security"]["apisix_gateway_host"],
            "apisix_admin_token": raw_data["security"]["apisix_admin_token"],
            "enable_mtls": raw_data["security"]["enable_mtls"],
            "max_self_healing_attempts": raw_data["governance"]["max_self_healing_attempts"],
            "governance_risk_threshold": raw_data["governance"]["governance_risk_threshold"],
            "lance_db_uri": raw_data["persistence"]["lance_db_uri"],
        }
        
        # Log de alta visibilidad exponiendo la ruta física absoluta leída
        logger.info("ℹ️ [Config] Configuración cargada con éxito.")
        logger.info(f"📂 [Config] Archivo de origen: {absolute_path}")
        logger.info(
            f"🌐 [Config] Nube activa para el despliegue: "
            f"{flat_config['cloud_provider'].upper()}"
        )
        
        return flat_config

    except Exception as e:
        logger.critical(f"🚨 [Config] Error estructural parseando el archivo TOML: {str(e)}")
        sys.exit(1)

# Invocación inicial para el arranque del plano de control
runtime_settings = load_master_config()
