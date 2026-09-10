"""
🕸️ CAPA DE INFRAESTRUCTURA: ENTORNO DE ORQUESTACIÓN REPLICADO (TEMPORAL WORKFLOW)
========================================================================================
Define el pipeline determinista puro del Patrón Saga, delegando el cómputo pesado
a las actividades distributed del clúster para evitar congelamientos por Timeout.
"""

import asyncio
from datetime import timedelta
from temporalio import workflow

@workflow.defn
class IncidentMitigationWorkflow:
    """Workflow Distribuido encargado del ciclo autónomo de Auto-Healing de forma determinista."""

    def __init__(self) -> None:
        self._human_approved = None
        self._approved_event = asyncio.Event()

    @workflow.run
    async def run(self, incident_logs: str) -> dict:
        # El logger nativo de Temporal registra el inicio en el clúster distributed
        workflow.logger.info("[Temporal-Workflow] Inicializando Saga Distribuida Inmortal...")
        workflow.logger.info("[Temporal-Cluster] Despachando agentes de IA a las actividades concurrentes...")
        
        # 🚀 REFACTORIZACIÓN CLAVE: Mapeamos el Scatter-Gather delegando la ejecución a las Activities.
        # Al usar execute_activity con un timeout explícito, el Workflow no se congela esperando a Ollama.
        task_net = workflow.execute_activity(
            "execute_network_worker_activity", 
            incident_logs, 
            start_to_close_timeout=timedelta(seconds=10)
        )
        task_sec = workflow.execute_activity(
            "execute_security_worker_activity", 
            incident_logs, 
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        # Sincronizamos las actividades distribuidas remotas
        results = await asyncio.gather(task_net, task_sec)
        workflow.logger.info("[Temporal-Workflow] Veredicto MoA consolidado desde las actividades con éxito.")
        
        # Checkpoint distribuido persistente en la base de datos (HITL)
        workflow.logger.warn("[Temporal-Checkpoint] Hilo pausado consistentemente en DB. Esperando señal humana...")
        await self._approved_event.wait()
        
        workflow.logger.info("[Temporal-Workflow] Despertando de forma idónea. Mutación IaC Pulumi autorizada con éxito.")
        
        return {
            "status": "Saga completada con éxito distribuido",
            "results": results,
            "human_approved": self._human_approved
        }

    @workflow.signal
    def receive_human_approval(self, approved: bool) -> None:
        """Canal de comunicación distribuido encargado de recibir el callback de señales gRPC."""
        self._human_approved = approved
        self._approved_event.set()
        workflow.logger.info(f"[Temporal-Signal] Recibida inyección humana en caliente: Aprobado={approved}")
