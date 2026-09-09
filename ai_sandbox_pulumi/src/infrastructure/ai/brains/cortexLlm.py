import json
import httpx
from typing import Dict, Any, Callable
from loguru import logger

class CircuitBreakerOpenException(Exception):
    """Excepción lanzada cuando el Circuit Breaker bloquea peticiones físicas."""
    pass

class CortexLlm:
    def __init__(self, config: Dict[str, Any] = None):
        logger.info("[Cortex-Engine] 🚀 Buscando inicializador en Fábrica O(1) para: 'OLLAMA'")
        
        # Extracción lineal de configuración mediante diccionarios inmutables (Evita if/else)
        conf = config or {}
        ai_conf = conf.get("ai", {})
        ollama_conf = ai_conf.get("ollama", {})
        
        self.host: str = ollama_conf.get("host", "http://localhost:11434")
        self.model: str = ollama_conf.get("model", "qwen2.5:1.5b")
        
        # Estado del Circuit Breaker
        self.failure_count: int = 0
        self.failure_threshold: int = 2  # Umbral máximo de fallos antes de abrir el circuito
        
        self._build_ollama_strategy()
        self._register_execution_modes()

    def _build_ollama_strategy(self) -> None:
        logger.info(f"[Cortex-Ollama] 🏠 Conectando al clúster local de Ollama: {self.model}")
        
        self.timeout_config = httpx.Timeout(12.0, connect=3.0)
        self.async_client = httpx.AsyncClient(
            base_url=self.host,
            timeout=self.timeout_config,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50)
        )

    def _register_execution_modes(self) -> None:
        """Registro dinámico de estrategias de ejecución para eliminar flujos if/else."""
        self.execution_pipeline: Dict[bool, Callable] = {
            True: self._execute_physical_inference,  # Circuito Cerrado: Intenta llamada real
            False: self._execute_circuit_fallback     # Circuito Abierto: Desvío inmediato a contingencia
        }

    async def reason_incident_telemetry(self, agent_role: str, system_prompt: str, telemetry_logs: str) -> str:
        """
        Firma de inferencia asíncrona de alta disponibilidad.
        Determina algorítmicamente el flujo basándose en la salud del Circuit Breaker.
        """
        # Evaluación booleana del estado del circuito (True = Saludable / False = Abierto por errores)
        circuit_healthy: bool = self.failure_count < self.failure_threshold
        
        # Ejecución polimórfica sin estructuras de control if/else
        return await self.execution_pipeline[circuit_healthy](agent_role, system_prompt, telemetry_logs)

    async def _execute_physical_inference(self, agent_role: str, system_prompt: str, telemetry_logs: str) -> str:
        logger.info(f"[{agent_role}-Cortex] Despachando inferencia asíncrona hacia motor: 'OLLAMA'")
        
        structured_prompt = (
            f"System: {system_prompt}\n"
            f"Logs: {telemetry_logs}\n"
            f"Requisito: Devuelve un objeto JSON con las claves 'veredicto' y 'acciones_sugeridas'."
        )
        
        payload = {
            "model": self.model,
            "prompt": structured_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0,
                "num_predict": 160
            }
        }
        
        try:
            response = await self.async_client.post("/api/generate", json=payload)
            
            # Validación algorítmica de estado de error (404, 500, etc.)
            assert response.status_code == 200, f"HTTP Error {response.status_code}"
            
            raw_response = response.json().get("response", "").strip()
            json.loads(raw_response)  # Validar estructura estricta del JSON
            
            # Éxito: Reseteo lineal del contador de fallos
            self.failure_count = 0
            return raw_response
            
        except (httpx.TimeoutException, httpx.HTTPError, AssertionError, json.JSONDecodeError) as e:
            logger.warning(f"[{agent_role}-Cortex-Anomalía] Fallo físico registrado: {str(e)}")
            self.failure_count += 1  # Incremento atómico del estado de fallo
            return self._generate_fallback_mock_insight(agent_role)

    async def _execute_circuit_fallback(self, agent_role: str, system_prompt: str, telemetry_logs: str) -> str:
        logger.error(f"[{agent_role}-Cortex-CircuitBreaker] 🚨 CIRCUITO ABIERTO. Saltando llamada física por inestabilidad.")
        return self._generate_fallback_mock_insight(agent_role)

    def _generate_fallback_mock_insight(self, agent_role: str) -> str:
        logger.info(f"[{agent_role}-Cortex-Virtual] Computando inferencia local de contingencia en microsegundos.")
        contingency_payload = {
            "veredicto": "MITIGACION_SIMULADA_POR_LATENCIA",
            "acciones_sugeridas": [
                "Activar aislamiento local preventivo", 
                "Bypass de gobernanza por protección de hilos de control"
            ]
        }
        return json.dumps(contingency_payload)

    async def close(self) -> None:
        await self.async_client.aclose()
        logger.info("[Cortex-Ollama] Pool global de conexiones destruido de forma segura.")
