"""
========================================================================================
⚙️ CAPA DE GOBERNANZA CENTRAL: SISTEMA ELÁSTICO DE CONFIGURACIÓN CONFIG.TOML
========================================================================================
Mapeador estático de bajo nivel encargado de volcar, parsear y exponer en la RAM.
CERO HARDCODE: Expone de forma atómica los mensajes tácticos de compensación.
========================================================================================
"""

import os
import tomllib
from typing import Dict, Any

class ProjectConfigurationRegistry:
    _CONFIG_DATA: Dict[str, Any] = {}

    @classmethod
    def load_registry(cls):
        config_path = "config.toml"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"💥 [CRÍTICO] Falta el manifiesto global de configuración: {config_path}")
        with open(config_path, "rb") as f:
            cls._CONFIG_DATA = tomllib.load(f)

    @classmethod
    def get_infra_defaults(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        infra_section = cls._CONFIG_DATA["infrastructure"]
        provider_activo = infra_section["cloud_provider"].lower().strip()
        return {
            "cloud_provider": provider_activo,
            "cluster_name": infra_section["cluster_name"],
            "variables": cls._CONFIG_DATA["providers"][provider_activo]
        }

    @classmethod
    def get_moa_agents_settings(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["moa"]["agents"]

    @classmethod
    def get_provider_blueprint(cls, provider: str) -> Dict[str, str]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["blueprints"][provider.lower().strip()]

    @classmethod
    def get_ai_settings(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        ai_provider = cls._CONFIG_DATA["ai"]["provider"].lower().strip()
        engine_params = cls._CONFIG_DATA["ai_engines"][ai_provider]
        return {
            "provider": ai_provider,
            "endpoint_url": engine_params["api_endpoint_url"],
            "timeout_limit": int(engine_params["timeout_limit"]),
            "body_template": engine_params["request_body_template"]
        }

    @classmethod
    def get_orchestration_settings(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        orch = cls._CONFIG_DATA["orchestration"]
        return {
            "task_queue": orch["task_queue"],
            "workflow_id": orch["workflow_id"],
            "timeout_seconds": int(orch.get("activity_schedule_to_close_seconds", 45)),
            "status_msg": orch.get("success_status_message", "COMPLETED"),
            "rollback_msg": orch.get("rollback_status_message", "ROLLBACK_TRIGGERED")
        }

    @classmethod
    def get_tools_settings(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["tools"]

    @classmethod
    def get_iac_settings(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["iac"]["pulumi"]

ProjectConfigurationRegistry.load_registry()
