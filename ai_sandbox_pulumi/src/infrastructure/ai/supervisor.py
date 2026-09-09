import asyncio
import json
import os
from typing import Dict, Any, List, Optional, Callable
from loguru import logger
from src.infrastructure.ai.brains.cortexLlm import CortexLlm
from src.infrastructure.persistence.vector_repo import IncidentVectorRepository

# Registro inmutable de estrategias de comandos de la CLI según el modo de configuración
COMMAND_FLAGS_REGISTRY: Dict[str, List[str]] = {
    "simulado": ["preview", "--skip-preview"], 
    "real": ["up", "--yes", "--skip-preview"]   
}

class BaseMutationCommand:
    """Interfaz abstracta para los comandos de mutación física de Pulumi."""
    async def execute_async(self, stack_name: str, mode: str, backend_url: str, mutation_data: Dict[str, Any]) -> bool:
        raise NotImplementedError

class PulumiAislarVPCCommand(BaseMutationCommand):
    """
    Estrategia de Mutación Desacoplada de Datos (Data-Driven).
    Escribe el payload de infraestructura de la IA a disco para que Pulumi lo consuma de forma aislada.
    """
    async def execute_async(self, stack_name: str, mode: str, backend_url: str, mutation_data: Dict[str, Any]) -> bool:
        target_flags = COMMAND_FLAGS_REGISTRY.get(mode, COMMAND_FLAGS_REGISTRY["simulado"])
        logger.warning(f"[Pulumi-Engine] Orquestando CLI en Modo: [{mode.upper()}] | Stack: {stack_name}")
        
        mutation_file_path = "dynamic_mutation.json"
        try:
            with open(mutation_file_path, "w", encoding="utf-8") as f:
                json.dump(mutation_data, f, indent=2)
            logger.info(f"[Pulumi-Engine] Archivo de mutación dirigido por datos generado: {mutation_file_path}")
        except IOError as e:
            logger.error(f"[Pulumi-Failure] No se pudo escribir el archivo de intercambio de datos: {str(e)}")
            return False

        args = ["pulumi"] + target_flags + ["--stack", stack_name]
        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "PULUMI_BACKEND_URL": backend_url}
            )
            stdout, stderr = await process.communicate()
            success = process.returncode == 0
            logger.info(f"[Pulumi-Execution-Output]\n{stdout.decode('utf-8', errors='ignore')}")
            return success
        except FileNotFoundError:
            logger.error("[Pulumi-Failure] El binario de 'pulumi' no se encuentra disponible en el PATH local.")
            return False

class PulumiBypassCommand(BaseMutationCommand):
    """Comando de contingencia virtual cuando no se requiere mutar la infraestructura."""
    async def execute_async(self, stack_name: str, mode: str, backend_url: str, mutation_data: Dict[str, Any]) -> bool:
        logger.success(f"[Memory-Bypass] Cierre forense de la saga completado (Aislamiento local virtual).")
        return True

class ThreadCoordinator:
    """Mapeo estático global de sincronización de hilos."""
    _events: Dict[str, asyncio.Event] = {}

    @classmethod
    def get_event(cls, thread_id: str) -> asyncio.Event:
        if thread_id not in cls._events:
            cls._events[thread_id] = asyncio.Event()
        return cls._events[thread_id]

    @classmethod
    def signal_ready(cls, thread_id: str) -> None:
        cls.get_event(thread_id).set()
        logger.info(f"[Thread-Sync] Hilo {thread_id} sincronizado con éxito.")

        class AsyncAgentSupervisor:
    """Orquestador central parametrizado con ordenación RAG e inyección de contexto histórico."""
    def __init__(self, *args, **kwargs):
        self.workers: List[Any] = kwargs.get("workers", [])
        self.governance_engine: Optional[Any] = kwargs.get("governance_engine", None)
        
        self.cortex = kwargs.get("cortex_brain", CortexLlm())
        self.risk_threshold: int = getattr(self.governance_engine, "risk_threshold", 70)
        
        self.config_data: Dict[str, Any] = kwargs.get("config", {})
        iac_conf = self.config_data.get("iac", {}).get("pulumi", {})
        self.stack_name: str = iac_conf.get("stack", "sandbox")
        self.mode: str = iac_conf.get("mode", "simulado").lower()
        self.backend_url: str = iac_conf.get("backend_url", "file://~")
        
        self.vector_repo = IncidentVectorRepository(config=self.config_data)
        
        self._register_governance_modes()
        self._register_mutation_commands()
        
        self._internal_state: Dict[str, Any] = {
            "messages": [], "incident_context": {}, "next_step": "end"
        }
        self._latest_raw_infra_payload: Dict[str, Any] = {}
        self._historical_rag_context: str = ""  # Buffer para inyectar los resultados del query

    def _register_governance_modes(self) -> None:
        self.governance_pipeline: Dict[bool, Callable[[], Any]] = {
            True: self._execute_automated_mitigation,
            False: self._skip_mitigation
        }

    def _register_mutation_commands(self) -> None:
        self.mutation_registry: Dict[str, BaseMutationCommand] = {
            "ACTIVAR_AISLAMIENTO_LOCAL": PulumiAislarVPCCommand(),
            "Bypass": PulumiBypassCommand()
        }

    async def ainvoke(self, command: Any, config: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        configurable = config.get("configurable", {}) if config else {}
        thread_id = configurable.get("thread_id", "incident-global-default")
        
        is_initial_ingest = isinstance(command, dict)
        
        # Mapeo lineal de acciones de inicio vs reanudación
        action_mapping = {
            True: lambda: self._handle_initial_ingest_persistence(thread_id, command),
            False: lambda: logger.info(f"[Supervisor-Adapter] Reanudando canal web para Hilo: {thread_id}")
        }
        action_mapping[is_initial_ingest]()
        
        ThreadCoordinator.signal_ready(thread_id)
        approved = getattr(command, "resume", {}).get("approved", True) if not is_initial_ingest else True
        
        debate_summary = await self.process_incident_lifecycle(self.workers, approved)
        
        if not is_initial_ingest:
            self.vector_repo.insert_incident_vector(
                incident_id=thread_id,
                description="Incidente cerrado con aprobación de gobernanza.",
                embedding=[0.1, 0.5, 0.8, 0.2],
                acciones=debate_summary["acciones_consolidadas"]
            )
        
        self._internal_state = {
            "messages": [{"content": f"Gobernanza procesada: {debate_summary['max_risk']}% de riesgo.", "type": "ai"}],
            "incident_context": {
                "max_risk_score": debate_summary["max_risk"],
                "acciones_consolidadas": debate_summary["acciones_consolidadas"],
                "bypass_executed": debate_summary["bypass"]
            },
            "next_step": "end"
        }
        return self

    def _handle_initial_ingest_persistence(self, thread_id: str, command: Dict[str, Any]) -> None:
        """Estrategia de persistencia corregida: Busca primero en LanceDB e inyecta el resultado al contexto."""
        logger.info(f"[Supervisor-Adapter] 🌌 Ingesta inicial detectada para Hilo: {thread_id}")
        
        context_obj = command.get("incident_context", None)
        raw_description = getattr(context_obj, "raw_logs", "Telemetría de alerta inicial.")
        
        # 1. ORDEN CORREGIDO: Buscar antecedentes en la base de datos ANTES de guardar el incidente actual
        query_results = self.vector_repo.search_similar_incidents(query_embedding=[0.1, 0.5, 0.8, 0.2], limit=2)
        
        # 2. INYECCIÓN DEL RESULTADO: Formatear las coincidencias reales para alimentar los prompts de los agentes
        # Mapeo funcional lineal para estructurar la cadena del contexto histórico sin if/else
        matches_str = " | ".join(f"[ID: {m.get('incident_id')}, Desc: {m.get('alert_description')}]" for m in query_results)
        self._historical_rag_context = f"Antecedentes Históricos Detectados en LanceDB: {matches_str}"
        
        # 3. PERSISTENCIA EN FRÍO: Registrar el incidente actual en disco
        self.vector_repo.insert_incident_vector(
            incident_id=thread_id,
            description=raw_description,
            embedding=[0.1, 0.5, 0.8, 0.2],
            acciones=["INGESTA_INICIAL"]
        )

    def __getitem__(self, key: str) -> Any: return self._internal_state[key]
    def __setitem__(self, key: str, value: Any) -> None: self._internal_state[key] = value
    def get(self, key: str, default: Any = None) -> Any: return self._internal_state.get(key, default)
    def keys(self): return self._internal_state.keys()
    def items(self): return self._internal_state.items()
    def values(self): return self._internal_state.values()
    def dict(self) -> Dict[str, Any]: return self._internal_state
    def model_dump(self) -> Dict[str, Any]: return self._internal_state

    async def process_incident_lifecycle(self, workers: List[Any], incident_context: Any) -> Dict[str, Any]:
        logger.info("[Background-Worker] Despachando Saga Para Hilo de Control... ")
        active_workers = workers or self.workers
        
        # Combinar de forma atómica la telemetría actual con el resultado del query de LanceDB
        enriched_context = f"{incident_context} \n {self._historical_rag_context}"
        
        tasks = [
            worker.execute_reasoning(self.cortex, enriched_context)
            for worker in active_workers
        ]
        raw_responses: List[str] = await asyncio.gather(*tasks)
        debate_summary = self._consolidate_debate_metrics(raw_responses)
        requires_mitigation = (debate_summary["max_risk"] >= self.risk_threshold) or (debate_summary["bypass"])
        
        if asyncio.iscoroutinefunction(self.governance_pipeline[requires_mitigation]):
            await self.governance_pipeline[requires_mitigation](debate_summary["acciones_consolidadas"])
        else:
            self.governance_pipeline[requires_mitigation]()
        return debate_summary

    def _consolidate_debate_metrics(self, responses: List[str]) -> Dict[str, Any]:
        max_risk_score = 0
        actions = []
        bypass_detected = False
        for resp in responses:
            try:
                data = json.loads(resp)
                veredicto = data.get("veredicto", "")
                bypass_detected |= (veredicto == "MITIGACION_SIMULADA_POR_LATENCIA")
                risk_increment = {"MITIGACION_SIMULADA_POR_LATENCIA": 100}.get(veredicto, 50)
                max_risk_score = max(max_risk_score, risk_increment)
                self._latest_raw_infra_payload = data.get("infraestructura_mutacion", {})
                raw_actions = data.get("acciones_sugeridas", [])
                for act in raw_actions:
                    normalized_action = "ACTIVAR_AISLAMIENTO_LOCAL" if "aislamiento" in act.lower() else "Bypass"
                    actions.append(normalized_action)
            except (json.JSONDecodeError, TypeError):
                bypass_detected = True
        logger.success("[MoA-Engine] Debate unificado consolidado exitosamente.")
        return {
            "max_risk": max_risk_score,
            "acciones_consolidadas": list(set(actions)) if actions else ["Bypass"],
            "bypass": bypass_detected
        }

    async def _execute_automated_mitigation(self, acciones: List[str]) -> None:
        logger.info("[Governance-Bypass] Riesgo elevado detectado. Evaluando comandos de mutación física...")
        for accion in acciones:
            command_handler = self.mutation_registry.get(accion, PulumiBypassCommand())
            mutation_success = await command_handler.execute_async(
                stack_name=self.stack_name, mode=self.mode, backend_url=self.backend_url, mutation_data=self._latest_raw_infra_payload
            )
            logger.info(f"[Mutation-Status] Comando '{accion}' completado con éxito: {mutation_success}")

    def _skip_mitigation(self) -> None:
        logger.info("[Governance-Safe] Telemetría stable. No se altera la infraestructura.")

def compile_supervisor_workflow(*args, **kwargs) -> AsyncAgentSupervisor:
    return AsyncAgentSupervisor(*args, **kwargs)