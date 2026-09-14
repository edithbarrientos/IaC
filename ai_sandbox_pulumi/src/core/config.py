"""
========================================================================================
⚙️ CAPA DE GOBERNANZA CENTRAL: SISTEMA ELÁSTICO DE CONFIGURACIÓN CONFIG.TOML
========================================================================================
Mapeador estático de bajo nivel encargado de volcar, parsear y exponer en la RAM.
MÁXIMA OPTIMIZACIÓN EN O(1): Externaliza los esquemas JSON para disolver el error de tomllib.
========================================================================================
"""

import os
import tomllib
from typing import Dict, Any

# MAPA DE TEMPLATES INMUTABLES DE IA EN RAM: Sincronizado dinámicamente con los adaptadores
AI_BODY_TEMPLATES_REGISTRY: Dict[str, dict] = {
    "ollama": {
        "model": "qwen2.5:1.5b",
        "prompt": "$PROMPT",
        "stream": False,
        "format": "json"
    },
    "bedrock": {
        "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": "$PROMPT"}]
    },
    "gcp_vertex": {
        "contents": [{"role": "user", "parts": [{"text": "$PROMPT"}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    },
    "azure_openai": {
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": "$PROMPT"}]
    }
}

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
        provider_activo = (os.getenv("CLOUD_PROVIDER") or infra_section["cloud_provider"]).lower().strip()
        return {
            "cloud_provider": provider_activo,
            "cluster_name": infra_section["cluster_name"],
            "variables": cls._CONFIG_DATA["providers"][provider_activo]
        }

    @classmethod
    def get_security_hardening_settings(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["security"]["hardening"]

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
        """🚀 DESPACHO MULTI-ENGINE EN O(1): Extrae el template directo de la tabla hash de Python."""
        if not cls._CONFIG_DATA:
            cls.load_registry()
        ai_root = cls._CONFIG_DATA["ai"]
        ai_provider = ai_root["provider"].lower().strip()
        engine_params = cls._CONFIG_DATA["ai_engines"][ai_provider]
        
        return {
            "provider": ai_provider,
            "endpoint_url": engine_params["api_endpoint_url"],
            "timeout_limit": int(engine_params["timeout_limit"]),
            "api_key": engine_params.get("api_key_token", ""),
            "body_template": AI_BODY_TEMPLATES_REGISTRY.get(ai_provider, {}) # 🚀 Mapeo atómico directo en RAM
        }

    @classmethod
    def get_persistence_settings(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return {
            "uri": cls._CONFIG_DATA["persistence"]["lance_db_uri"],
            "forensics_table": cls._CONFIG_DATA["persistence"]["tables"]["forensics_table_name"]
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
        return {
            "aws": cls._CONFIG_DATA["tools_aws"],
            "azure": cls._CONFIG_DATA["tools_azure"],
            "gcp": cls._CONFIG_DATA["tools_gcp"],
            "ssh_forensic": cls._CONFIG_DATA["tools_ssh_forensic"]
        }

    @classmethod
    def get_iac_settings(cls) -> Dict[str, Any]:
        if not cls._CONFIG_DATA:
            cls.load_registry()
        return cls._CONFIG_DATA["iac_pulumi"]

ProjectConfigurationRegistry.load_registry()
