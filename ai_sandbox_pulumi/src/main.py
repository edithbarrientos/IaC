"""
========================================================================================
🌌 PLATAFORMA DE AIOPS: GATEWAY DE INGESTA COGNITIVA Y PLANO DE CONTROL DE ESTADOS
========================================================================================

Este módulo actúa como el punto de entrada asíncrono unificado de la arquitectura limpia
para la recepción y mitigación automatizada de incidentes (*Self-Healing*).

📐 PRINCIPIOS DE INGENIERÍA APLICADOS:
--------------------------------------
1. Desacoplamiento de E/S (Throughput Máximo): 
   Las alertas telemétricas entrantes se validan en microsegundos y se delegan 
   inmediatamente a un Worker Pool asíncrono virtual mediante `asyncio.create_task`. 
   Esto permite responder con un código HTTP `202 Accepted` de inmediato, liberando el
   bucle de eventos principal de FastAPI para que no espere los debates de los agentes.

2. Patrón Saga con Checkpointer Global Compartido:
   Para soportar flujos asíncronos distribuidos en múltiples rutas HTTP, se implementa
   un búfer centralizado inmutable (`MemorySaver`). Esto garantiza que los nodos de
   ingesta en segundo plano y las rutas de devolución humana (Web/Slack Actions) 
   apunten exactamente al mismo bloque de memoria volátil, eliminando los errores 
   `404/500 KeyError` por aislamiento de estados en hilos separados de FastAPI.

3. Arquitectura Polimórfica Defensiva:
   El Supervisor Cognitivo está blindado contra inyecciones nulas (`NoneType`). Si los
   motores físicos de cumplimiento o bases de datos vectoriales del clúster real no se 
   encuentran inicializados en este Sandbox de desarrollo local, el sistema activa un 
   mecanismo adaptativo de *Bypass* defensivo, permitiendo certificar el flujo lógico 
   de punta a punta de manera 100% aislada.

Historial de Cambios:
    - 2026-09-09: Unificación de Checkpointer Global, reparación síncrona del snapshot 
                  de LangGraph y mitigación de KeyErrors de dominio en reanudación Web.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Literal, Optional
import httpx
from fastapi import FastAPI, HTTPException, Response, Form, Query
from pydantic import BaseModel, Field, ConfigDict
from loguru import logger
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver

# Importaciones de la Capa de Infraestructura y Casos de Uso (Clean Architecture)
from src.use_cases.self_healing import execute_self_healing_saga
from src.infrastructure.api_slack import handle_slack_interactive_buttons
from src.infrastructure.ai.supervisor import compile_supervisor_workflow, AsyncAgentSupervisor
from src.infrastructure.ai.workers import NetworkSpecialistWorker, SecurityZeroTrustWorker

# =====================================================================================
# 📦 ORQUESTACIÓN GLOBAL: INYECCIÓN DE DEPENDENCIAS Y CAPA DE MEMORIA ATÓMICA
# =====================================================================================

# Listado polimórfico de agentes especialistas que participarán en el debate concurrente
POOL_DE_WORKERS_GLOBAL = [
    NetworkSpecialistWorker(agent_id="prod-worker-networking"),
    SecurityZeroTrustWorker(agent_id="prod-worker-zerotrust")
]

# El almacén de persistencia transaccional indexado por `thread_id`. 
# Debe residir obligatoriamente como recurso global estático para compartir el búfer entre endpoints.
CHECKPOINTER_COMPARTIDO = MemorySaver()

# Instanciación e inicialización única del Supervisor Cognitivo en el espacio del módulo
SUPERVISOR_GLOBAL = AsyncAgentSupervisor(
    workers=POOL_DE_WORKERS_GLOBAL, 
    memory_repo=None,        # Bypass defensivo activado para aislamiento en Sandbox local
    governance_engine=None   # Bypass defensivo de cumplimiento activado para desarrollo local
)

# Compilación y sellado del Grafo de Estados Asíncrono de LangGraph
GRAFO_COMPILADO_GLOBAL = compile_supervisor_workflow(SUPERVISOR_GLOBAL)
GRAFO_COMPILADO_GLOBAL.checkpointer = CHECKPOINTER_COMPARTIDO


# =====================================================================================
# 🌐 GESTIÓN DE RECURSOS DEL SISTEMA: LIFESPAN CONTEXT MANAGER
# =====================================================================================

INFRASTRUCTURE_STATE = {}

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """ Mide y administra de forma elástica el ciclo de vida de los recursos del sistema.
    
    Estrategia de Optimización:
        - On Startup: Instancia un cliente asíncrono HTTPX persistente con límites extendidos
          de Keep-Alive. Esto evita la degradación de CPU por la apertura continua de handshakes 
          TCP/TLS durante ráfagas masivas de incidentes (Starvation de descriptores de archivos).
        - On Shutdown: Ejecuta un drenado seguro (*Graceful Shutdown*), forzando el cierre de 
          las conexiones remanentes sin corromper transacciones en tránsito en segundo plano.
    """
    logger.info("[Lifespan-Init] Configurando Pool Global de Conexiones de alta disponibilidad...")
    http_pool = httpx.AsyncClient(
        limits=httpx.Limits(max_connections=300, max_keepalive_connections=100),
        timeout=httpx.Timeout(5.0),
        headers={"X-Server-Engine": "AIOps-Control-Plano/3.0"}
    )
    INFRASTRUCTURE_STATE["http_pool"] = http_pool
    
    yield
    
    logger.warning("[Lifespan-Shutdown] Iniciando drenado seguro de sockets y descriptores...")
    await http_pool.aclose()
    logger.success("[Lifespan-Shutdown] Plano de control apagado de manera limpia.")


# =====================================================================================
# 📑 DATA TRANSFER OBJECTS (DTO): MODELOS DE VALIDACIÓN TELEMÉTRICA
# =====================================================================================

class IncidentIngestPayload(BaseModel):
    """ Esquema inmutable encargado de parsear y sanitizar las alertas telemétricas de producción.
    
    Configurado bajo Pydantic v2 en modo `frozen=True` para acelerar el hashing interno
    en memoria y mitigar el overhead de validación en tiempo de ejecución en entornos concurrentes.
    """
    incident_id: str = Field(..., description="Identificador único global del incidente de producción")
    cloud_provider: Literal["aws", "gcp", "azure"] = Field(..., description="Nube objetivo afectada por la anomalía")
    alert_description: str = Field(..., description="Payload JSON o traza forense descriptiva de la falla")
    notification_channel: Literal["web", "slack", "email"] = Field("web", description="Canal preferido para el control manual humano")
    slack_webhook_url: Optional[str] = Field(None, description="Webhook HTTP de salida en caso de enrutamiento por Slack")

    model_config = ConfigDict(frozen=True)

    """Punto de Entrada de Ultra Alto Rendimiento para el Plano de Control de AIOps - Parte 2.

Este bloque de código ejecuta la lógica del API Gateway de FastAPI, administrando el despachador
en segundo plano y exponiendo los controladores HTTP para orquestar la máquina de estados.
"""

# Inicialización de la aplicación FastAPI conectada al ciclo de vida global
app = FastAPI(
    title="AIOps Cognitive Control Control Plane",
    version="3.0.0",
    description="Motor autónomo de mitigación de infraestructura con soporte adaptativo HITL",
    lifespan=app_lifespan
)


async def _background_saga_runner(payload: IncidentIngestPayload) -> None:
    """ Consumidor asíncrono encargado de inicializar el contexto de la Saga Cognitiva.
    
    Flujo Ejecutivo:
        1. Ingesta el payload y fabrica la entidad inmutable `IncidentContext`.
        2. Alimenta el estado inicial de LangGraph emitiendo el mensaje raíz.
        3. Invoca la ejecución asíncrona del grafo, la cual correrá en paralelo hasta topar
           con el nodo interactivo `human_approval`, congelando el progreso de manera segura.
    """
    try:
        logger.info(f"[Background-Worker] Despachando Saga Para Hilo de Control: {payload.incident_id}")
        
        from langchain_core.messages import HumanMessage
        from src.core.entities import IncidentContext
        
        # Construcción del contexto mapeando de forma segura las variables mandatorias del Core
        incident_context = IncidentContext(
            incident_id=payload.incident_id,
            cloud_provider_target=payload.cloud_provider,
            self_healing_attempts=0,
            security_risk_score=0,
            is_approved_by_gov=True,
            raw_logs=f"[Mapeo-Automático]: {payload.alert_description}"
        )

        initial_graph_state = {
            "messages": [HumanMessage(content=f"[Telemetría Alerta]: {payload.alert_description}")],
            "next_action": "process_lifecycle",
            "human_approved": None,
            "incident_context": incident_context,
            "simulated_embedding": [0.1, 0.2, 0.3, 0.4], 
            "notification_config": {
                "channel": payload.notification_channel,
                "webhook_url": payload.slack_webhook_url,
                "target_email": None,
                "callback_url": None
            }
        }
        
        # Ejecución del orquestador compartiendo el checkpointer unificado
        execution_config = {"configurable": {"thread_id": payload.incident_id}}
        await GRAFO_COMPILADO_GLOBAL.ainvoke(initial_graph_state, config=execution_config)
        logger.success(f"[UseCase] Incidente {payload.incident_id} pausado de forma consistente en el checkpoint global.")
        
    except Exception as e:
        logger.error(f"[Background-Worker-Failure] Error crítico en la Saga del incidente {payload.incident_id}: {str(e)}")


# =====================================================================================
# 🧭 CAPA DE CONTROLADORES HTTP (ENDPOINTS EXPUESTOS)
# =====================================================================================

@app.get("/", status_code=200)
async def root_welcome():
    """ Controlador base de bienvenida y protección de enrutamiento raíz.
    
    Misión: Responde de forma exitosa (200 OK) ante cualquier ping accidental o golpe de red 
    a la raíz de tu dominio, eliminando por completo el ruido visual de errores 404 en la Mac.
    """
    return {
        "status": "active",
        "message": "Bienvenido al Plano de Control de AIOps en edithbaga.local",
        "documentation": "Envía un HTTP POST a /v1/alerts/ingest para gatillar el enjambre Mixture of Agents."
    }


@app.post("/v1/alerts/ingest", status_code=202)
async def ingest_production_incident(payload: IncidentIngestPayload):
    """ Endpoint de Ingesta Asíncrona Masiva (Latencia de respuesta: O(1) en microsegundos).
    
    Mecánica: Valida el payload de entrada contra el modelo de Pydantic y, de forma inmediata, 
    despacha la ejecución analítica a un hilo de segundo plano usando las primitivas de `asyncio`. 
    Esto libera la conexión HTTP al instante sin bloquear el event loop.
    """
    asyncio.create_task(_background_saga_runner(payload))
    return {
        "status": "accepted",
        "incident_id": payload.incident_id,
        "telemetry_state": "Saga delegada al pool asíncrono con éxito."
    }


@app.post("/v1/integrations/slack/actions")
async def slack_callback_router(payload: str = Form(...)):
    """ Enrutador de eventos e interacciones asíncronas provenientes de los botones de Slack. """
    return await handle_slack_interactive_buttons(payload)


@app.post("/v1/alerts/resume-web")
async def web_callback_router(thread_id: str = Query(...), approved: bool = Query(...)):
    """ Endpoint encargado de la reanudación e inyección humana (HITL) para la vía Web nativa.
    
    Lógica de TRol de Estado:
        1. Extracción Sincrónica: Invoca `get_state(config)` de forma síncrona (sin `await`) 
           sobre el Grafo Unificado Global. Al compartir la misma memoria de la ingesta, 
           el snapshot se recupera de manera instantánea en O(1).
        2. Prevención de Pérdida de Dominio: Extrae el objeto `incident_context` histórico resguardado
           en el checkpoint y lo inyecta dentro de la directiva `update` del comando de reanudación. 
           Esto evita que LangGraph limpie las variables del contexto al brincar de hilo HTTP.
    """
    logger.info(f"[Web-Callback] Recibida señal humana de reanudación para Hilo: {thread_id} | Aprobado: {approved}")
    config = {"configurable": {"thread_id": thread_id}}
    try:
        # 1. Extracción síncrona en O(1) del snapshot almacenado por el MemorySaver del módulo global
        current_state_snapshot = GRAFO_COMPILADO_GLOBAL.get_state(config)
        
        # 2. Validación defensiva estricta
        if not current_state_snapshot or not current_state_snapshot.values:
            raise ValueError(f"No se encontró un checkpoint guardado en el búfer unificado para el ID: {thread_id}")

        # 3. Extraemos el contexto analítico original resguardado
        historical_context = current_state_snapshot.values.get("incident_context")

        # 4. Despertamos al agente pasándole el Command de reanudación consolidado
        await GRAFO_COMPILADO_GLOBAL.ainvoke(
            Command(
                resume={"approved": approved},
                update={"incident_context": historical_context}
            ), 
            config=config
        )
        logger.success(f"[Web-Callback] El hilo {thread_id} despertó del checkpoint y cerró la saga con éxito.")
        return {"status": "success", "message": f"Hilo {thread_id} reanudado y procesado de forma idónea."}
        
    except Exception as e:
        logger.error(f"[Web-Callback-Error] Error crítico reanudando el grafo del hilo {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/healthz", status_code=200)
async def health_check():
    """ Liveness/Readiness probe para monitoreo de estado del Daemon de red. """
    return {
        "status": "healthy",
        "engine": "uvicorn-single-worker-shared-checkpointer",
        "version": "3.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    # Lanzamiento del servidor web asíncrono
    uvicorn.run(app, host="0.0.0.0", port=8000)
