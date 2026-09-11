"""
🕸️ CAPA DE INFRAESTRUCTURA: ENTORNO DE ORQUESTACIÓN REPLICADO (TEMPORAL WORKFLOW)
========================================================================================
Define el pipeline determinista puro del Patrón Saga, delegando el cómputo pesado
a las actividades distributed del clúster e invocando las herramientas del Toolbelt.
"""

import os
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
        workflow.logger.info("[Temporal-Workflow] Inicializando Saga Distribuida Inmortal...")
        workflow.logger.info("[Temporal-Cluster] Despachando agentes de IA a las actividades concurrentes...")
        
        task_net = workflow.execute_activity("execute_network_worker_activity", incident_logs, start_to_close_timeout=timedelta(seconds=10))
        task_sec = workflow.execute_activity("execute_security_worker_activity", incident_logs, start_to_close_timeout=timedelta(seconds=10))
        
        results = await asyncio.gather(task_net, task_sec)
        workflow.logger.info("[Temporal-Workflow] Veredicto MoA consolidado desde las actividades con éxito.")
        
        mode = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
        if mode == "simulado":
            workflow.logger.info("[Temporal-Sandbox] Ejecutando en Modo Desarrollador. Evadiendo freno de mano humano...")
            self._human_approved = True
            self._approved_event.set()
        else:
            workflow.logger.warn("[Temporal-Checkpoint] Hilo pausado consistentemente en DB. Esperando señal humana real...")
            await self._approved_event.wait()
        
        workflow.logger.info(f"[Temporal-Workflow] Despertando. Ejecutando catálogo de mitigación Toolbelt para: [{mode.upper()}]")
        
        # 🚨 CORRECCIÓN SINTÁCTICA: Importación acoplada a la nueva nomenclatura de tu Mac
        from src.infrastructure.tools.mitigationToolbelt import MITIGATION_TOOLBELT
        
        tool_aws = MITIGATION_TOOLBELT.get_tool("AWS_ISOLATE_EC2")
        await tool_aws.execute_action(target_id="i-0f9c2d1b8490a73ef", metadata={"security_group_isolated": "sg-mitigation-jail-prod"})
        
        tool_ssh = MITIGATION_TOOLBELT.get_tool("SSH_FORENSIC_DUMP")
        await tool_ssh.execute_action(target_id="i-0f9c2d1b8490a73ef", metadata={"ip_address": "10.0.4.15"})
        
        return {
            "status": "Saga y Toolbelt completados con éxito distribuido",
            "results": results,
            "human_approved": self._human_approved,
            "actions_executed": ["AWS_ISOLATE_EC2", "SSH_FORENSIC_DUMP"]
        }

    @workflow.signal
    def receive_human_approval(self, approved: bool) -> None:
        self._human_approved = approved
        self._approved_event.set()
        workflow.logger.info(f"[Temporal-Signal] Recibida inyección humana en caliente: Aprobado={approved}")
