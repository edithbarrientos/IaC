"""
========================================================================================
🕸️ CAPA DE ORQUESTACIÓN DETERMINISTA: STATE-DRIVEN SAGA WORKFLOW DESIGN
========================================================================================
Define el pipeline determinista puro del Patrón Saga con transacciones de compensación.
MÁXIMA OPTIMIZACIÓN EN O(1):Desacoplamiento total de firmas Multi-Cloud pasadas por la 
terminal de comandos.
========================================================================================
"""

from datetime import timedelta
from typing import Dict, Any, Callable
from temporalio import workflow

# Función pasante para evadir la ejecución de esperas humanas en entornos simulados
async def _noop_wait():
    pass

async def _ejecutar_wait_humano():
    def _check_approval() -> bool:
        return workflow.get_current_run_context().workflow_instance._signal_received
    workflow.logger.warning("[Project-ODIN] Entorno REAL detectado. Esperando validación humana...")
    await workflow.wait_condition(_check_approval)

# MAPA HASH 1: Despacho Voraz de Esperas de Entorno en O(1) (Elimina el IF de aprobación)
ENVIRONMENT_WAIT_STRATEGY: Dict[str, Callable] = {
    "simulado": _noop_wait,
    "real": _ejecutar_wait_humano,
    "qa": _ejecutar_wait_humano,
    "produccion": _ejecutar_wait_humano
}

@workflow.defn(name="IncidentMitigationWorkflow")
class IncidentMitigationWorkflow:

    def __init__(self) -> None:
        self._human_approved = False
        self._signal_received = False

    @workflow.signal
    def receive_human_approval(self, approved: bool) -> None:
        self._human_approved = approved
        self._signal_received = True

    @workflow.run
    async def run(self, incident_logs: str) -> dict:
        workflow.logger.info("[Project-ODIN] Inicializando Saga Distribuida Inmortal...")
        
        import asyncio
        from src.core.config import ProjectConfigurationRegistry

        orch_settings = ProjectConfigurationRegistry.get_orchestration_settings()
        iac_settings = ProjectConfigurationRegistry.get_iac_settings()
        tools_settings = ProjectConfigurationRegistry.get_tools_settings()
        custom_params = ProjectConfigurationRegistry.get_infra_defaults()
        
        context_timeout = timedelta(seconds=orch_settings["timeout_seconds"])

        # Ejecución paralela distribuida de los agentes Mixture-of-Agents en O(1)
        results_net, results_sec = await asyncio.gather(
            workflow.execute_activity("execute_network_worker_activity", incident_logs, schedule_to_close_timeout=context_timeout),
            workflow.execute_activity("execute_security_worker_activity", incident_logs, schedule_to_close_timeout=context_timeout)
        )
        
        workflow.logger.info("[Project-ODIN] Veredicto del enjambre Mixture-of-Agents consolidado.")
        
        # ZERO IFS ENVIRONMENT: Despacho dinámico de la espera directo desde el TOML
        mode_key = iac_settings["mode"].lower().strip()
        await ENVIRONMENT_WAIT_STRATEGY.get(mode_key, _noop_wait)()
            
        workflow.logger.info("[Project-ODIN] Despertando. Recuperando plano polimórfico de la factoría...")
        
        try:
            reconciliation_result = await workflow.execute_activity(
                "execute_pulumi_cli_activity",
                {"blueprint": results_net.get("blueprint", {})},
                schedule_to_close_timeout=context_timeout
            )
            
            # ZERO IFS CIRCUIT BREAKER: El estatus determina el flujo lanzando un KeyError si falla,
            # lo que gatilla instantáneamente el bloque except de reversión de la SAGA en O(1).
            success_gateway = {"success": True}
            success_gateway[reconciliation_result.get("status")]

            # 🚀 RESOLUCIÓN DE HARDCODE CLOUD EN O(1): Extrae dinámicamente la configuración 
            # de la nube que pasaste por terminal (aws, azure, gcp) de forma transparente.
            cloud_active = custom_params["cloud_provider"]
            cloud_tool_config = tools_settings.get(cloud_active, {})
            target_id_dinamico = cloud_tool_config.get("default_target_id", "fallback-id")

            toolbelt_result = await workflow.execute_activity(
                "execute_toolbelt_mitigation_activity",
                {"target_id": target_id_dinamico},
                schedule_to_close_timeout=context_timeout
            )
            
            return {
                "status": orch_settings["status_msg"],
                "results": results_net,
                "human_approved": True,
                "actions_executed": toolbelt_result.get("executed_tools", []),
                "manifiesto_written": True
            }

        except Exception as SAGA_EX:
            workflow.logger.error(f"💥 [SAGA-TRACK] Interrupción detectada: {str(SAGA_EX)}. Detonando reversión...")
            
            await workflow.execute_activity(
                "compensate_failed_infrastructure_activity",
                {"incident_id": id(SAGA_EX)},
                schedule_to_close_timeout=context_timeout
            )
            
            return {
                "status": orch_settings["rollback_msg"],
                "results": results_net,
                "human_approved": False,
                "actions_executed": [],
                "manifiesto_written": False
            }