"""Caso de Uso: Mitigación Automatizada de Incidentes (Self-Healing).

Este módulo coordina la regla de negocio de auto-recuperación. Ingesta las alertas
de infraestructura, inicializa el contexto analítico del incidente y dispara el 
plano de control cognitivo configurando dinámicamente el transporte omnicanal.
"""

from typing import List, Literal, Optional
from loguru import logger
from langchain_core.messages import HumanMessage

# Importaciones de la capa Core y de Infraestructura de tu árbol
from src.core.entities import IncidentContext
from src.infrastructure.ai.supervisor import compile_supervisor_workflow, AsyncAgentSupervisor
from src.infrastructure.ai.workers import NetworkSpecialistWorker, SecurityZeroTrustWorker

# Instanciación e Inyección de Dependencias del Enjambre de Workers Especialistas
POOL_DE_WORKERS = [
    NetworkSpecialistWorker(agent_id="prod-worker-networking"),
    SecurityZeroTrustWorker(agent_id="prod-worker-zerotrust")
]


async def execute_self_healing_saga(
    incident_id: str,
    cloud_target: str,
    alert_payload: str,
    notification_channel: Literal["web", "slack", "email"],
    webhook_url: Optional[str] = None,
    target_email: Optional[str] = None,
    callback_url: Optional[str] = None,
    memory_repo_instance: Optional[any] = None,      
    governance_engine_instance: Optional[any] = None 
) -> bool:
    """Orquesta la saga cognitiva inyectando las preferencias de notificación del cliente.

    Args:
        incident_id (str): ID único global correlacionado con el incidente.
        cloud_target (str): Proveedor de nube afectado (ej. 'aws', 'gcp').
        alert_payload (str): Mensaje descriptivo de la falla telemétrica.
        notification_channel (str): Canal por el cual el humano desea recibir el interrupt.
        webhook_url (str, optional): Destino HTTP si el canal es Slack.
        target_email (str, optional): Destino si el canal es correo.
        callback_url (str, optional): Endpoint del panel si el canal es Web.

    Returns:
        bool: True si el flujo completó su ejecución, False si ocurrió un fallo.
    """
    logger.info(f"[UseCase] Inicializando Saga de Auto-Recuperación para Incidente: {incident_id}")

    # 🚨 SOLUCIÓN AL VALIDATION ERROR: Inyectamos raw_logs de forma mandatoria al constructor
    incident_context = IncidentContext(
        incident_id=incident_id,
        cloud_provider_target=cloud_target,
        self_healing_attempts=0,
        security_risk_score=0,
        is_approved_by_gov=True,
        raw_logs=f"[Mapeo-Automático]: {alert_payload}"
    )

    # Inicializamos el estado base requerido por el grafo de LangGraph
    initial_graph_state = {
        "messages": [HumanMessage(content=f"[Telemetría Alerta]: {alert_payload}")],
        "next_action": "process_lifecycle",
        "human_approved": None,
        "incident_context": incident_context,
        "simulated_embedding": [0.1, 0.2, 0.3, 0.4], 
        "notification_config": {
            "channel": notification_channel,
            "webhook_url": webhook_url,
            "target_email": target_email,
            "callback_url": callback_url
        }
    }

    # Configuramos las llaves de persistencia atómica para el Checkpointer (Thread Control)
    execution_config = {"configurable": {"thread_id": incident_id}}

    try:
        # Instanciamos dinámicamente el supervisor con sus dependencias
        supervisor_instance = AsyncAgentSupervisor(
            workers=POOL_DE_WORKERS,
            memory_repo=memory_repo_instance,
            governance_engine=governance_engine_instance
        )

        # Fabricamos y compilamos el Grafo de Estados
        compiled_graph = compile_supervisor_workflow(supervisor_instance)

        # Disparamos la IA de forma asíncrona. Correrá hasta topar con el 'interrupt()'
        logger.info(f"[UseCase] Ejecutando plano cognitivo. Hilo de control: {incident_id}")
        await compiled_graph.ainvoke(initial_graph_state, config=execution_config)
        
        logger.success(f"[UseCase] Transacción procesada o pausada en checkpoint de manera exitosa.")
        return True

    except Exception as e:
        logger.error(f"[UseCase-Error] Error crítico ejecutando la saga del incidente {incident_id}: {str(e)}")
        return False
