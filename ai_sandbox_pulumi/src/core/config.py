"""
========================================================================================
⚙️ CAPA DE GOBERNANZA CENTRAL: SISTEMA ELÁSTICO DE CONFIGURACIÓN CONFIG.TOML
========================================================================================
Mapeador estático de bajo nivel encargado de volcar, parsear y exponer en la RAM
del clúster todas las llaves, firmas y diccionarios elásticos del plano perimetral.
CERO HARDCODE: Absolutamente ningún metatipo, ID, score o tabla se fija en Python.
========================================================================================
"""

import os
import tomllib
from typing import Dict, Any

class ProjectConfigurationRegistry:
    """Mapeador estático de la RAM encargado de centralizar los parámetros globales."""
    _CONFIG_DATA: Dict[str, Any] = {}

    @classmethod
    def load_registry(cls):
        """Carga de forma atómica el archivo config.toml. Lanza error si no existe."""
        config_path = "config.toml"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"💥 [CRÍTICO] Falta el manifiesto global de configuración: {config_path}")
            
        with open(config_path, "rb") as f:
            cls._CONFIG_DATA = tomllib.load(f)

    @classmethod
    def get_infra_defaults(cls) -> Dict[str, Any]:
        """Recupera el diccionario completo del proveedor activo."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        infra_section = cls._CONFIG_DATA["infrastructure"]
        provider_activo = infra_section["cloud_provider"].lower().strip()
        provider_params = cls._CONFIG_DATA["providers"][provider_activo]
        return {
            "cloud_provider": provider_activo,
            "cluster_name": infra_section["cluster_name"],
            "variables": provider_params
        }

    @classmethod
    def get_moa_agents_settings(cls) -> Dict[str, Any]:
        """Recupera el catálogo entero de identidades del enjambre de IA desde el TOML."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["moa"]["agents"]

    @classmethod
    def get_provider_blueprint(cls, provider: str) -> Dict[str, str]:
        """Recupera las firmas de tipos de recursos e identificadores directo desde el TOML."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        blueprints_section = cls._CONFIG_DATA["blueprints"]
        return blueprints_section[provider.lower().strip()]

    @classmethod
    def get_ai_settings(cls) -> Dict[str, Any]:
        """🚀 PARAMETRIZACIÓN TOTAL IA: Transporta el payload crudo y el template del cuerpo HTTP."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        ai_root = cls._CONFIG_DATA["ai"]
        ai_provider = ai_root["provider"].lower().strip()
        engine_params = cls._CONFIG_DATA["ai_engines"][ai_provider]
        return {
            "provider": ai_provider,
            "host_url": engine_params["host_url"],
            "timeout_limit": int(engine_params["timeout_limit"]),
            "body_template": engine_params["request_body_template"]
        }

    @classmethod
    def get_persistence_settings(cls) -> Dict[str, Any]:
        """🚀 ZERO HARDCODE PERSISTENCE: Extrae la URI y las tablas vectoriales dinámicamente."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        p_section = cls._CONFIG_DATA["persistence"]
        return {
            "uri": p_section["lance_db_uri"],
            "forensics_table": p_section["tables"]["forensics_table_name"]
        }

    @classmethod
    def get_orchestration_settings(cls) -> Dict[str, Any]:
        """Recupera las colas y nombres de tareas de Temporal IO."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["orchestration"]

    @classmethod
    def get_tools_settings(cls) -> Dict[str, Any]:
        """Recupera los metadatos de aislamiento del Toolbelt."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["tools"]

    @classmethod
    def get_iac_settings(cls) -> Dict[str, Any]:
        """Recupera las propiedades de ejecución de la CLI de Pulumi."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        iac_root = cls._CONFIG_DATA["iac"]
        return iac_root["pulumi"]

# Inicialización forzada estricta en el Runtime
ProjectConfigurationRegistry.load_registry()
