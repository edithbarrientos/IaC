"""
🩹 CAPA DE APLICACIÓN: CASO DE USO DE SELF-HEALING COGNITIVO (ALGORITMO VORAZ)
========================================================================================
Orquestador encargado de la ingesta de alertas telemétricas. Utiliza el patrón
Simultaneous Task Spawning para exprimir los núcleos concurrentes de la CPU en la Mac.
"""

import asyncio
import time
from typing import Any, Dict

from loguru import logger
from temporalio.client import Client

from src.infrastructure.ai.brains.hipocampoMemory import HipocampoMemoryController


class SelfHealingUseCase:
    """Caso de uso encargado de la ingesta, análisis y auto-recuperación de incidentes."""

    def __init__(self, temporal_client: Client) -> None:
        self.temporal_client = temporal_client
        self.hipocampo = HipocampoMemoryController()

    async def execute_incident_ingestion(
        self, alert_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Procesa la ingesta forense disparando la Saga y LanceDB en paralelo puro."""
        incident_id = alert_payload.get("incident_id", "incident-generic-id")
        raw_logs = alert_payload.get("alert_description", "")
        
        logger.info(f"🩹 [INGESTA] Procesando alerta crítica: {incident_id}")
        
        # 🚀 TRUE PARALLEL SPECULATION: Lanzamos las dos promesas al mismo tiempo
        wf_promise = asyncio.create_task(
            self.temporal_client.start_workflow(
                "IncidentMitigationWorkflow",
                raw_logs,
                id=f"workflow-{incident_id}",
                task_queue="aiops-incident-task-queue"
            )
        )
        
        mem_promise = asyncio.create_task(
            self.hipocampo.recall_similar_incidents_profiled(raw_logs, limit=1)
        )
        
        # Sincronización atómica sin hilos bloqueantes intermedios
        inicio_concurrente = time.perf_counter()
        handle_wf, metrics_memory = await asyncio.gather(wf_promise, mem_promise)
        latencia_net_ms = (time.perf_counter() - inicio_concurrente) * 1000
        
        logger.success("✨ [INGESTA] Alerta consolidada de forma concurrente exitosa.")
        
        return {
            "status": "ACCEPTED",
            "incident_id": incident_id,
            "workflow_run_id": handle_wf.first_execution_run_id,
            "throughput_net_ms": latencia_net_ms,
            "lancedb_internal": metrics_memory
        }
