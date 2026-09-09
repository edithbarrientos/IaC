"""
========================================================================================
🌌 PLATAFORMA DE AIOPS: GATEWAY DE INGESTA COGNITIVA Y PLANO DE CONTROL DE ESTADOS
========================================================================================
"""
import os
import sys

# 🚨 SEGURIDAD MANDATORIA EN RENGLÓN 1: Registros de entorno antes de levantar el compilador
os.environ["LANGGRAPH_ALLOWED_MSGPACK_MODULES"] = "src.core.entities"
os.environ["PYTHONIOENCODING"] = "utf-8"

from dotenv import load_dotenv
load_dotenv()

import asyncio
import tomllib  # <-- Uso de la biblioteca estándar y nativa de Python (Inmune a fallos de entorno)
from contextlib import asynccontextmanager
from typing import Literal, Optional, Dict, Any
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

# Función utilitaria lineal para cargar el archivo config.toml corporativo de forma nativa sin toml externo
def load_master_config_safely() -> Dict[str, Any]:
    try:
        with open("config.toml", "rb") as f:
            return tomllib.load(f)
    except Exception:
        # Fallback inmutable seguro si el archivo no es legible o no existe
        return {"iac": {"pulumi": {"stack": "sandbox", "mode": "simulado", "backend_url": "file://~"}}}

# 1. Carga inicial de datos de configuración de la plataforma
MASTER_CONFIG_DATA = load_master_config_safely()

# 2. Inicialización del enjambre de agentes y fábricas
POOL_DE_WORKERS_GLOBAL = [
    NetworkSpecialistWorker(agent_id="prod-worker-networking"),
    SecurityZeroTrustWorker(agent_id="prod-worker-zerotrust")
]

CHECKPOINTER_COMPARTIDO = MemorySaver()

# 3. Instanciación del Supervisor Global inyectando la configuración IaC leída del TOML
SUPERVISOR_GLOBAL = AsyncAgentSupervisor(
    workers=POOL_DE_WORKERS_GLOBAL, 
    memory_repo=None, 
    governance_engine=None,
    config=MASTER_CONFIG_DATA
)

GRAFO_COMPILADO_GLOBAL = compile_supervisor_workflow(SUPERVISOR_GLOBAL)
GRAFO_COMPILADO_GLOBAL.checkpointer = CHECKPOINTER_COMPARTIDO

# Caché atómica local para la sincronización y persistencia forense de hilos asíncronos
INCIDENT_STATE_CACHE: Dict[str, Any] = {}
INFRASTRUCTURE_STATE = {}

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("[Lifespan-Init] Configurando Pool Global de Conexiones de alta disponibilidad...")
    http_pool = httpx.AsyncClient(
        limits=httpx.Limits(max_connections=300, max_keepalive_connections=100),
        timeout=httpx.Timeout(5.0),
        headers={"X-Server-Engine": "AIOps-Control-Plano/3.0"}
    )
    INFRASTRUCTURE_STATE["http_pool"] = http_pool
    yield
    logger.warning("[Lifespan-Shutdown] Iniciando drenado seguro de sockets...")
    await http_pool.aclose()

class IncidentIngestPayload(BaseModel):
    incident_id: str = Field(..., description="ID del incidente")
    cloud_provider: Literal["aws", "gcp", "azure"] = Field(...)
    alert_description: str = Field(...)
    notification_channel: Literal["web", "slack", "email"] = Field("web")
    slack_webhook_url: Optional[str] = Field(None)
    model_config = ConfigDict(frozen=True)

app = FastAPI(title="AIOps Control Plane", version="3.0.0", lifespan=app_lifespan)

async def _background_saga_runner(payload: IncidentIngestPayload) -> None:
    try:
        logger.info(f"[Background-Worker] Despachando Saga Para Hilo de Control: {payload.incident_id}")
        from langchain_core.messages import HumanMessage
        from src.core.entities import IncidentContext
        
        incident_context = IncidentContext(
            incident_id=payload.incident_id, cloud_provider_target=payload.cloud_provider,
            self_healing_attempts=0, security_risk_score=0, is_approved_by_gov=True,
            raw_logs=f"[Mapeo-Automático]: {payload.alert_description}"
        )
        
        initial_graph_state = {
            "messages": [HumanMessage(content=f"[Telemetría Alerta]: {payload.alert_description}")],
            "next_action": "process_lifecycle", "human_approved": None, "incident_context": incident_context,
            "simulated_embedding": [0.1, 0.2, 0.3, 0.4],
            "notification_config": {"channel": payload.notification_channel, "webhook_url": payload.slack_webhook_url, "target_email": None, "callback_url": None}
        }
        
        INCIDENT_STATE_CACHE[payload.incident_id] = incident_context
        await GRAFO_COMPILADO_GLOBAL.ainvoke(initial_graph_state, config={"configurable": {"thread_id": payload.incident_id}})
    except Exception as e:
        logger.error(f"[Background-Worker-Failure] Error crítico en la Saga: {str(e)}")

@app.post("/v1/alerts/ingest", status_code=202)
async def ingest_production_incident(payload: IncidentIngestPayload):
    asyncio.create_task(_background_saga_runner(payload))
    return {"status": "accepted", "incident_id": payload.incident_id}

@app.post("/v1/alerts/resume-web")
async def web_callback_router(thread_id: str = Query(...), approved: bool = Query(...)):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        logger.info(f"[API-Router] Interceptando callback web para sincronizar Hilo: {thread_id}")
        historical_context = INCIDENT_STATE_CACHE.get(thread_id, None)
        
        await GRAFO_COMPILADO_GLOBAL.ainvoke(
            Command(resume={"approved": approved}, update={"incident_context": historical_context}), 
            config=config
        )
        return {"status": "success", "message": f"Hilo {thread_id} reanudado."}
    except Exception as e:
        logger.error(f"[API-Router-Failure] Error crítico detectado en hilo {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
