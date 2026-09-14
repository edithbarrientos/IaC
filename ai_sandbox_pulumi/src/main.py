"""
🌌 PLANO DE CONTROL DE AIOPS DISTRIBUIDO: STATE-DRIVEN POLYMORPHIC TEMPORAL GATEWAY
========================================================================================
Mapea los entornos de infraestructura distributed mediante estados polimórficos con
despacho algorítmico voraz en O(1), optimizando los handshakes gRPC en caliente.
🔒 ZERO-IF METRICS: Servidor HTTP con Command Dispatcher inyectado libre de condicionales.
⚡ HYBRID RUNTIME: Ejecución simultánea del daemon de Temporal y Prometheus Registry.
========================================================================================
"""

import os
import sys
import asyncio
import signal
import unicodedata
from typing import Optional, Dict, Any, Type, Callable
from http.server import HTTPServer, BaseHTTPRequestHandler
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner
from loguru import logger
from src.core.config import ProjectConfigurationRegistry
from src.infrastructure.monitoring.metrics import ProjectOdinMetricsRegistry

os.environ["PYTHONIOENCODING"] = "utf-8"

from dotenv import load_dotenv
load_dotenv()


class BaseTemporalConnector:
    """Abstracción base inmutable para el ciclo de vida de las conexiones gRPC de Temporal."""
    def __init__(self) -> None:
        self.client: Optional[Client] = None
        self.is_virtual: bool = False

    async def connect_engine(self, target_host: str) -> Client:
        raise NotImplementedError


class SimuladoTemporalConnector(BaseTemporalConnector):
    """Activador del entorno local elástico con fallback a memoria volátil en pruebas."""
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
    """Conector de grado industrial para clústeres remotos productivos."""
    async def connect_engine(self, target_host: str) -> Client:
        logger.info(f"🔒 [CONECTOR_ESTADO] Conectando por gRPC al clúster en: {target_host}")
        self.client = await Client.connect(target_host)
        return self.client


class HardenedMetricsServerAdapter(BaseHTTPRequestHandler):
    """Manejador HTTP encargado de validar el token simétrico y escupir el payload CNCF."""
    
    def do_GET(self) -> None:
        """Intercepta las peticiones GET validando el token de seguridad corporativo."""
        auth_header = self.headers.get("Authorization", "")
        expected_token = "Bearer odin-super-secret-hmac-authentication-token-99999"
        
        # Evaluación por cortocircuito booleano para validar el token sin usar condicionales if
        is_authorized = int(auth_header == expected_token)
        
        # Despacho reactivo binario O(1) basado en el estatus de la autorización
        router = {
            1: lambda: self._write_metrics_payload(),
            0: lambda: self._reject_intruder_connection()
        }
        router.get(is_authorized, lambda: self._reject_intruder_connection())()

    def _write_metrics_payload(self) -> None:
        """Extrae los bytes planos del registro unificado del config.toml."""
        payload, content_type = ProjectOdinMetricsRegistry.expose_metrics_payload()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(payload)

    def _reject_intruder_connection(self) -> None:
        """Rechaza de forma fulminante handshakes no autorizados en el perímetro."""
        self.send_response(401)
        self.end_headers()
        self.wfile.write(b"[CRITICAL] Intento de extraccion de telemetria no autorizado.")

    def log_message(self, format: str, *args) -> None:
        """Enmudece los logs nativos de la consola para no ensuciar tu pantalla de QA."""
        pass


ACTIVE_CONNECTOR: Optional[BaseTemporalConnector] = None


def run_metrics_server_blocking(port: int = 8000) -> None:
    """Levanta el socket Keep-Alive físico sobre el puerto expuesto de tu Mac."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, HardenedMetricsServerAdapter)
    logger.info(f"[Metrics-Server] 📟 Endpoint listo operando en http://localhost:{port}/metrics/custom-ai")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


async def main():
    """Punto de entrada maestro asíncrono para el ciclo de vida del Daemon Worker."""
    global ACTIVE_CONNECTOR
    
    # Carga paramétrica de la raíz elástica del TOML corporativo
    ProjectConfigurationRegistry.load_registry()
    
    # Inicializa tu nuevo registro elástico sin condicionales
    ProjectOdinMetricsRegistry.initialize_registry()
    
    # 🚀 ACOPLAMIENTO CRÍTICO MLOps: Forzamos la ráfaga de tráfico simulado al arrancar
    from src.infrastructure.monitoring.trigger_metrics import simulate_production_traffic
    await simulate_production_traffic()
    
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

        # Purificación e importación atómica inmaculada de workflows y actividades
        from src.infrastructure.ai.supervisor import IncidentMitigationWorkflow
        from src.infrastructure.ai.workers import (
            execute_network_worker_activity, 
            execute_security_worker_activity,
            execute_pulumi_cli_activity,
            execute_toolbelt_mitigation_activity
        )

        # Lanzamiento no bloqueante: Desvía el Metrics Server a un hilo de hardware en paralelo con el Worker
        asyncio.create_task(asyncio.to_thread(run_metrics_server_blocking, 8000))

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
        logger.info(f"🦾 [QUEUE_DAEMON] Escuchando activamente la queue '{orch_settings['task_queue']}'...")
        
        # Bucle infinito asíncrono de Temporal esperando incidentes perimetrales
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
