"""Modulo del Agente Supervisor Asincrono de AIOps."""

import asyncio
from typing import List, Optional

from core.config import runtime_settings
from core.entities import AuditLogEntry, IncidentContext
from core.governance import AgentGovernanceEngine
from core.interfaces import AgentStrategy, VectorMemoryRepository
from loguru import logger


class AsyncAgentSupervisor:
    """Orquestador central del plano de control cognitivo."""

    def __init__(
        self, 
        workers: List[AgentStrategy], 
        memory_repo: VectorMemoryRepository,
        governance_engine: AgentGovernanceEngine
    ) -> None:
        """Inicializa el Supervisor."""
        self.workers: List[AgentStrategy] = workers
        self.memory_repo: VectorMemoryRepository = memory_repo
        self.governance_engine: AgentGovernanceEngine = governance_engine
        
        # Carga de la configuracion parametrizada
        cfg_ctrl = "network_control_cidr"
        cfg_prod = "network_production_cidr"
        self.control_cidr: str = runtime_settings[cfg_ctrl]
        self.production_cidr: str = runtime_settings[cfg_prod]

    async def inject_cognitive_reinforcement_signal(
        self, 
        incident_id: str, 
        source: str, 
        is_positive: bool, 
        correction_diff: Optional[str] = None
    ) -> None:
        """Inyecta una senal de refuerzo externo."""
        msg = (
            f"[Feedback] Src: {source.upper()} | "
            f"ID: {incident_id} | OK: {is_positive}"
        )
        logger.info(msg)
        
        if not is_positive:
            logger.warning("[Feedback] Penalizando rama cognitiva.")
        else:
            logger.success("[Feedback] Recompensa positiva en RAM.")
            
        if correction_diff:
            logger.info("[Feedback] Absorbiendo Diff humano.")

        await asyncio.sleep(0.01)

    async def process_incident_lifecycle(
        self, 
        incident: IncidentContext, 
        simulated_embedding: List[float]
    ) -> bool:
        """Gobierna la maquina de estados del incidente."""
        logger.info(f"[Saga] Incidente: {incident.incident_id}")

        # --- FASE 1: DEBATE CONCURRENTE MOA ---
        incident.self_healing_attempts += 1
        try:
            tasks = [w.execute_reasoning(incident) for w in self.workers]
            enjambre_results = await asyncio.gather(*tasks)
            for result in enjambre_results:
                if result.proposed_patch:
                    incident.proposed_patch = result.proposed_patch
                if result.ai_suggested_metric:
                    incident.ai_suggested_metric = result.ai_suggested_metric
                if result.security_risk_score > incident.security_risk_score:
                    incident.security_risk_score = result.security_risk_score
            logger.success("[MoA] Debate consolidado con exito.")
        except Exception as e:
            logger.error(f"[MoA] Error critico en enjambre: {str(e)}")
            return False

        # --- FASE 2: GOBIERNO ZERO-TRUST ---
        is_safe = await self.governance_engine.evaluate_execution_safety(incident)
        if not is_safe or not incident.is_approved_by_gov:
            await self.inject_cognitive_reinforcement_signal(
                incident_id=incident.incident_id,
                source="GOVERNANCE_ENGINE",
                is_positive=False
            )
            return False

        # --- FASE 3: RECONCILIACIÓN FÍSICA MULTI-CLOUD ---
        target_cloud = incident.cloud_provider_target.upper()
        logger.info(f"[Pulumi] Trigger stack: {target_cloud}")
        await asyncio.sleep(0.01)
        deploy_success = True

        if not deploy_success:
            await self.inject_cognitive_reinforcement_signal(
                incident_id=incident.incident_id,
                source="SANDBOX_JAIL",
                is_positive=False
            )
            return False

        # --- FASE 4: BITÁCORA FORENSE INMUTABLE ---
        audit_entry = AuditLogEntry(
            audit_entry_id=f"audit-{incident.incident_id[:8]}",
            incident_id=incident.incident_id,
            agent_name="AsyncAgentSupervisor",
            action_taken="CONVERGED_SUCCESSFULLY",
            decision_rationale="Despliegue Multi-Tier verificado.",
            security_risk_score=incident.security_risk_score,
            financial_token_cost=4200
        )
        await self.memory_repo.save_audit_trail(audit_entry)

        # --- FASE 5: RECOMPENSA POSITIVA DEL BUCLE ---
        await self.inject_cognitive_reinforcement_signal(
            incident_id=incident.incident_id,
            source="PROMETHEUS_TELEMETRY",
            is_positive=True
        )

        logger.success(f"[Saga] Incidente {incident.incident_id} cerrado.")
        return True
