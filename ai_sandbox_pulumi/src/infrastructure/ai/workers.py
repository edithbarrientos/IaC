"""Módulo de Workers Especialistas con Despacho Polimórfico de APIs de AIOps.

Implementa agentes de SRE y SecOps bajo contratos abstractos, erradicando
bloques if/else mediante tablas de despacho directo en memoria RAM,
maximizando la resiliencia ante errores del operador en config.toml.

Información del Módulo:
    * Autor: Edith Barrientos 💻
    * Año: 2026 🚀
    * Patrones: Registry Pattern, Polymorphic Dispatch, Short-Circuit Evaluation
"""

import asyncio
import random
from typing import Callable, List

from core.config import runtime_settings
from core.entities import IncidentContext
from core.interfaces import AgentStrategy
from loguru import logger

# Registro global memoizado en RAM para latencia cero
_API_SIGNATURE_CACHE: dict[str, List[str]] = {
    "pulumi:gcp:Vpc": ["name", "cidr", "enable_flow_logs"]
}


class SreDebuggerAgent(AgentStrategy):
    """Agente de SRE adaptable con extracción analítica libre de condicionales."""

    def __init__(self) -> None:
        """Inicializa el agente configurando el despacho por diccionario."""
        self._pruned_syntax_blacklist: List[str] = []
        self.epsilon_exploration: float = 0.10
        
        # Mapeo directo de funciones constructoras para eliminar sentencias if/else
        self._patch_builders: dict[bool, Callable[[str, str], str]] = {
            True: lambda v, c: f"pulumi:gcp:Vpc(name='{v}', cidr='{c}', enable_flow_logs=True)",
            False: lambda v, c: f"pulumi:gcp:Vpc(name='{v}', cidr='{c}')"
        }

    @property
    def agent_name(self) -> str:
        """Retorna el identificador unívoco del worker."""
        return "SreDebuggerAgent"

    async def execute_reasoning(self, context: IncidentContext) -> IncidentContext:
        """Diseña el parche IaC resolviendo la firma en el mapa directo de RAM."""
        logger.info(f"⚙️ [{self.agent_name}] Extrayendo esquema unificado de RAM...")
        await asyncio.sleep(0.01)
        
        vpc_name = runtime_settings.get("network_vpc_name", "fallback-vpc")
        cidr = runtime_settings.get("network_production_cidr", "172.16.20.0/24")
        
        supported_args = _API_SIGNATURE_CACHE.get("pulumi:gcp:Vpc", [])
        has_flow_logs = "enable_flow_logs" in supported_args
        
        patch_string = self._patch_builders[has_flow_logs](vpc_name, cidr)

        is_exploring = random.random() < self.epsilon_exploration
        patch_string += " // [Exploration Mode]" * is_exploring

        context.proposed_patch = patch_string
        logger.success(f"✅ [{self.agent_name}] Parche adaptativo polimórfico generado.")
        return context


class SecOpsGuardAgent(AgentStrategy):
    """Agente especialista en auditoría Zero-Trust con evaluación por cortocircuito."""

    def __init__(self) -> None:
        """Inicializa el agente SecOps configurando el mapeo de evaluación de riesgo."""
        self._risk_score_dispatch: dict[bool, float] = {
            True: 0.95,   # Con violación de política PaC
            False: 0.15   # Cumplimiento exitoso
        }

    @property
    def agent_name(self) -> str:
        """Retorna el identificador unívoco del worker."""
        return "SecOpsGuardAgent"

    async def execute_reasoning(self, context: IncidentContext) -> IncidentContext:
        """Audita el parche aplicando lógica booleana y cortocircuitos en memoria RAM."""
        logger.info(f"🛡️ [{self.agent_name}] Evaluando cumplimiento de politicas PaC...")
        await asyncio.sleep(0.01)
        
        try:
            patch_str = context.proposed_patch or ""
            allowed_cidr = runtime_settings.get("network_production_cidr", "172.16.20.0/24")
            disallow_public = runtime_settings.get("security_disallow_public_ips", True)
            
            # Evaluación por cortocircuito
            has_violation = (allowed_cidr not in patch_str) or (disallow_public and "0.0.0.0" in patch_str)
            
            context.security_risk_score = self._risk_score_dispatch[has_violation]
            
            host = runtime_settings.get("apisix_gateway_host", "platform.local")
            context.ai_suggested_metric = f"prometheus:apisix:host='{host}'"
            logger.success(f"✅ [{self.agent_name}] Filtro Zero-Trust completado en RAM.")
            
        except Exception as e:
            # [FIX E501]: Rompemos el string usando parentesis implicitos para el linter
            logger.error(
                (f"💥 [{self.agent_name}] Panico interno en guardrail: "
                 f"{str(e)}")
            )
            context.security_risk_score = 1.0
            
        return context
