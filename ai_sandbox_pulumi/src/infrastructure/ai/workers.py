from typing import Dict, Any, List
from loguru import logger
from src.infrastructure.ai.brains.cortexLlm import CortexLlm

class BaseWorker:
    """Clase base inmutable que define el comportamiento del ciclo de inferencia de un agente."""
    def __init__(self, role_key: str, agent_role: str, system_prompt: str, log_identifier: str, *args, **kwargs):
        self.role_key: str = role_key
        self.agent_role: str = agent_role
        self.system_prompt: str = system_prompt
        
        # Asignación polimórfica: Usa agent_id si viene de los kwargs, de lo contrario usa el log_identifier por defecto
        self.log_identifier: str = kwargs.get("agent_id", log_identifier)

    async def execute_reasoning(self, cortex_brain: CortexLlm, incident_context: Any) -> str:
        """
        Template Method: Ejecuta de forma lineal y determinista el flujo de consulta hacia el Córtex.
        """
        logger.info(f"[{self.log_identifier}] Despertando agente. Consultando al Córtex LLM...")
        
        telemetry_logs: str = getattr(incident_context, "raw_logs", str(incident_context))
        
        veredicto_ia: str = await cortex_brain.reason_incident_telemetry(
            agent_role=self.agent_role,
            system_prompt=self.system_prompt,
            telemetry_logs=f"Contexto: {telemetry_logs}"
        )
        
        return veredicto_ia

class NetworkSpecialistWorker(BaseWorker):
    """Especialización que acepta e inyecta dinámicamente parámetros de inicialización del caso de uso."""
    def __init__(self, *args, **kwargs):
        super().__init__(
            "networking",
            "NetworkSpecialistWorker",
            "Eres un especialista de redes corporativas en AWS. Analiza anomalías de enrutamiento y CIDR.",
            "prod-worker-networking",
            *args,
            **kwargs
        )

class SecurityZeroTrustWorker(BaseWorker):
    """Especialización que acepta e inyecta dinámicamente parámetros de inicialización del caso de uso."""
    def __init__(self, *args, **kwargs):
        super().__init__(
            "zerotrust",
            "SecurityZeroTrustWorker",
            "Eres un auditor de seguridad Zero Trust. Evalúa riesgos críticos en el API Gateway y mTLS.",
            "prod-worker-zerotrust",
            *args,
            **kwargs
        )

class WorkerRegistry:
    """Fábrica O(1) encargada de almacenar y despachar las instancias preconfiguradas del enjambre."""
    def __init__(self):
        self._agents: Dict[str, BaseWorker] = {
            "networking": NetworkSpecialistWorker(),
            "zerotrust": SecurityZeroTrustWorker()
        }

    def get_all_workers(self) -> List[BaseWorker]:
        """Retorna el enjambre completo de agentes listo para el Scatter-Gather."""
        return list(self._agents.values())

    def get_worker(self, role_key: str) -> BaseWorker:
        """Retorna un agente específico mediante indexación directa O(1)."""
        return self._agents[role_key.lower()]

# Instancia global inmutable de la fábrica para consumo interno si es necesario
WORKER_FACTORY = WorkerRegistry()
