"""
========================================================================================
🌌 PLANO DE CONTROL DE AIOPS DISTRIBUIDO: STATE-DRIVEN POLYMORPHIC TEMPORAL GATEWAY
========================================================================================
Mapea los entornos de infraestructura distributed mediante estados polimórficos con
despacho algorítmico voraz en O(1), optimizando los handshakes gRPC en caliente.
========================================================================================
"""

import os
import sys
import asyncio
import signal
from typing import Optional, Dict, Type
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner
from loguru import logger

os.environ["PYTHONIOENCODING"] = "utf-8"

from dotenv import load_dotenv
load_dotenv()


class BaseTemporalConnector:
    def __init__(self) -> None:
        self.client: Optional[Client] = None
        self.is_virtual: bool = False

    async def connect_engine(self, target_host: str) -> Client:
        raise NotImplementedError


class SimuladoTemporalConnector(BaseTemporalConnector):
    async def connect_engine(self, target_host: str) -> Client:
        logger.info("🧪 [CONECTOR_ESTADO] Activando Sandbox de desarrollo elástico local...")
        try:
            self.client = await asyncio.wait_for(Client.connect(target_host), timeout=0.5)
            return self.client
        except Exception:
            logger.warning("[CONECTOR_ESTADO] Sockets locales libres. Conmutando a Servidor Temporal de pruebas en memoria.")
            from temporalio.testing import WorkflowEnvironment
            self.env = await WorkflowEnvironment.start_local()
            self.client = self.env.client
            return self.client


class EnterpriseTemporalConnector(BaseTemporalConnector):
    async def connect_engine(self, target_host: str) -> Client:
        logger.info(f"🔒 [CONECTOR_ESTADO] Conectando por gRPC al clúster en: {target_host}")
        self.client = await Client.connect(target_host)
        return self.client


ACTIVE_CONNECTOR: Optional[BaseTemporalConnector] = None

async def main():
    global ACTIVE_CONNECTOR
    
    from src.core.config import ProjectConfigurationRegistry
    orch_settings = ProjectConfigurationRegistry.get_orchestration_settings()
    
    mode_key = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
    env_host = os.getenv("TEMPORAL_HOST") or "localhost:7233"
    
    logger.info(f"🏭 [FÁBRICA_O1] Buscando inicializador para: '{mode_key.upper()}'")

    environment_factory: Dict[str, Type[BaseTemporalConnector]] = {
        "simulado": SimuladoTemporalConnector,
        "real": EnterpriseTemporalConnector,
        "qa": EnterpriseTemporalConnector,
        "produccion": EnterpriseTemporalConnector
    }

    connector_class = environment_factory.get(mode_key, SimuladoTemporalConnector)
    ACTIVE_CONNECTOR = connector_class()
    
    try:
        client = await ACTIVE_CONNECTOR.connect_engine(target_host=env_host)

        if client is None:
            logger.critical("💥 [ENTORNO_GLOBAL] Imposible inicializar el cliente del clúster distributed.")
            sys.exit(1)

        from src.infrastructure.ai.supervisor import IncidentMitigationWorkflow
        from src.infrastructure.ai.workers import (
            execute_network_worker_activity, 
            execute_security_worker_activity,
            execute_pulumi_cli_activity,
            execute_toolbelt_mitigation_activity
        )

        from prometheus_client import start_http_server
        start_http_server(8000, addr="0.0.0.0")

        # 🚀 ZERO HARDCODE: La task_queue se inyecta elásticamente desde el archivo TOML
        worker = Worker(
            client,
            task_queue=orch_settings["task_queue"],
            workflows=[IncidentMitigationWorkflow],
            activities=[
                execute_network_worker_activity, 
                execute_security_worker_activity,
                execute_pulumi_cli_activity,
                execute_toolbelt_mitigation_activity
            ],
            workflow_runner=UnsandboxedWorkflowRunner()
        )
        
        logger.success(f"🌐 [ENTORNO_GLOBAL] Plano de control distribuido real sellado con éxito.")
        logger.info(f"🦾 [QUEUE_DAEMON] Escuchando activamente la cola '{orch_settings['task_queue']}'...")
        await worker.run()

    except Exception as e:
        logger.critical(f"💥 [ENTORNO_GLOBAL] Colapso crítico en el plano de control: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    def handler_silencioso(signum, frame):
        print("\n")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, handler_silencioso)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except Exception:
        sys.exit(0)
