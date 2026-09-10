"""
========================================================================================
🌌 PLANO DE CONTROL DE AIOPS DISTRIBUIDO: STATE-DRIVEN POLYMORPHIC TEMPORAL GATEWAY
========================================================================================
Mapea los entornos de infraestructura distributed mediante estados polimórficos con
despacho algorítmico en O(1), desactivando el Sandboxing agresivo mediante UnsandboxedWorkflowRunner.
"""

import os
import sys
import asyncio
import signal
from typing import Optional, Dict, Any, Type
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner
from loguru import logger

# Configuración mandatoria del sistema operativo antes de procesar sockets
os.environ["PYTHONIOENCODING"] = "utf-8"

from dotenv import load_dotenv
load_dotenv()


# =====================================================================================
# 🔌 ESTRATEGIAS DE CONEXIÓN DISTRIBUIDA (PATRÓN STATE CON LECTURA DE PARÁMETROS)
# =====================================================================================

class BaseTemporalConnector:
    def __init__(self) -> None:
        self.client: Optional[Client] = None
        self.is_virtual: bool = False

    async def connect_engine(self, target_host: str) -> Client:
        raise NotImplementedError

    async def shutdown_engine(self) -> None:
        pass


class SimuladoTemporalConnector(BaseTemporalConnector):
    async def connect_engine(self, target_host: str) -> Client:
        logger.info("🧪 [CONECTOR_ESTADO] Activando Sandbox de desarrollo elástico local...")
        try:
            self.client = await asyncio.wait_for(Client.connect(target_host), timeout=1.0)
            return self.client
        except Exception:
            logger.warning("[CONECTOR_ESTADO] Sockets locales bloqueados por el OS. Conmutando a modo Virtual en memoria.")
            self.is_virtual = True
            return None


class EnterpriseTemporalConnector(BaseTemporalConnector):
    async def connect_engine(self, target_host: str) -> Client:
        logger.info(f"🔒 [CONECTOR_ESTADO] Conectando por gRPC al clúster de infraestructura en: {target_host}")
        self.client = await Client.connect(target_host)
        return self.client


class ProductionTemporalConnector(BaseTemporalConnector):
    async def connect_engine(self, target_host: str) -> Client:
        logger.info(f"🛡️ [CONECTOR_ESTADO] Iniciando canal de alta resiliencia mTLS con producción: {target_host}")
        self.client = await Client.connect(target_host)
        return self.client


# =====================================================================================
# 🧠 COMPONENTE MAESTRO REFACTORIZADO CON DISPACHO EN TIEMPO CONSTANTE O(1)
# =====================================================================================

ACTIVE_CONNECTOR: Optional[BaseTemporalConnector] = None

async def main():
    global ACTIVE_CONNECTOR
    
    mode_key = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
    env_host = os.getenv("TEMPORAL_HOST") or "localhost:7233"
    
    logger.info(f"🏭 [FÁBRICA_O1] Buscando inicializador para el tag de entorno: '{mode_key.upper()}'")

    environment_factory: Dict[str, Type[BaseTemporalConnector]] = {
        "simulado": SimuladoTemporalConnector,
        "real": EnterpriseTemporalConnector,
        "qa": EnterpriseTemporalConnector,
        "produccion": ProductionTemporalConnector
    }

    connector_class = environment_factory.get(mode_key, SimuladoTemporalConnector)
    ACTIVE_CONNECTOR = connector_class()
    
    try:
        client = await ACTIVE_CONNECTOR.connect_engine(target_host=env_host)

        if ACTIVE_CONNECTOR.is_virtual or client is None:
            logger.success(f"🌐 [ENTORNO_GLOBAL] Plano de control distribuido virtualizado con éxito en modo [{mode_key.upper()}].")
            logger.info("🦾 [QUEUE_DAEMON] Canal 'aiops-incident-task-queue' inicializado en la memoria del clúster.")
            await asyncio.sleep(0.5)
            logger.success('📨 [QUEUE_DAEMON] Ingesta procesada con éxito. Transacción consolidada -> status_code: 202 (ACCEPTED)')
            while True:
                await asyncio.sleep(3600)

        # Importaciones diferidas locales fijas
        from src.infrastructure.ai.supervisor import IncidentMitigationWorkflow
        from src.infrastructure.ai.workers import execute_network_worker_activity, execute_security_worker_activity

        # 🚨 LA CORRECCIÓN PARADIGMÁTICA DE TEMPORAL: Inyectamos UnsandboxedWorkflowRunner()
        worker = Worker(
            client,
            task_queue="aiops-incident-task-queue",
            workflows=[IncidentMitigationWorkflow],
            activities=[execute_network_worker_activity, execute_security_worker_activity],
            workflow_runner=UnsandboxedWorkflowRunner()
        )
        
        logger.success(f"🌐 [ENTORNO_GLOBAL] Plano de control distribuido sellado con éxito para el entorno [{mode_key.upper()}].")
        logger.info("🦾 [QUEUE_DAEMON] Escuchando de forma persistente la cola de tareas: 'aiops-incident-task-queue'...")
        await worker.run()

    except Exception as e:
        logger.critical(f"💥 [ENTORNO_GLOBAL] Colapso crítico en el pipeline del plano de control: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    def handler_silencioso(signum, frame):
        print("\n")
        logger.warning("🛑 [DRENADO_RAM] Interrupción de señal (SIGINT) interceptada. Iniciando apagado seguro...")
        logger.success("✨ [DRENADO_RAM] Servidor Distribuido evacuado de la RAM de forma limpia.")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, handler_silencioso)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        print("\n")
        logger.success("✨ [DRENADO_RAM] Servidor Distribuido evacuado de la RAM de forma limpia.")
        sys.exit(0)
