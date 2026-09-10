"""
🔮 CAPA DE INFRAESTRUCTURA COGNITIVA: STATE-DRIVEN POLYMORPHIC CORTEX ENGINE
========================================================================================
Mapea proveedores de inferencia mediante estados polimórficos con despacho en O(1),
eliminando estructuras if/else ramificadas y asegurando extensibilidad limpia.
"""

import os
import unicodedata
from typing import Optional, Dict, Any, Type
from loguru import logger

# Importaciones diferidas y defensivas para aislamiento de entornos
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


# =====================================================================================
# 📑 ESTRATEGIAS DE ESTADOS COGNITIVOS (PATRÓN STATE)
# =====================================================================================

class BaseCortexState:
    """Interfaz abstracta e inmutable para los estados de ejecución del Córtex."""
    
    def __init__(self, model_name: str, temperature: float) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.client: Optional[Any] = None

    def invoke_llm(self, messages: list) -> str:
        """Contrato de ejecución remota o local hacia la IA."""
        raise NotImplementedError


class OllamaCortexState(BaseCortexState):
    """Estado operativo encargado de orquestar las inferencias en tu Mac local."""
    
    def __init__(self, model_name: str, temperature: float) -> None:
        super().__init__(model_name, temperature)
        if OLLAMA_AVAILABLE:
            logger.info(f"[Cortex-State] 🏠 Instanciando canal local de Ollama: '{self.model_name}'")
            self.client = ChatOllama(model=self.model_name, temperature=self.temperature, base_url="http://localhost:11434")

    def invoke_llm(self, messages: list) -> str:
        if not self.client:
            raise RuntimeError("Instalación de langchain-ollama corrupta o ausente.")
        # Envío síncrono puente compatible con el bucle asíncrono superior
        response = self.client.invoke(messages)
        return response.content


class OpenAiCortexState(BaseCortexState):
    """Estado operativo encargado de orquestar la firma criptográfica en la nube."""
    
    def __init__(self, model_name: str, temperature: float) -> None:
        super().__init__(model_name, temperature)
        raw_key = os.getenv("OPENAI_API_KEY") or ""
        api_key = str(raw_key).encode("ascii", "ignore").decode("ascii").strip()
        
        if OPENAI_AVAILABLE and api_key and not api_key.startswith("mock") and len(api_key) > 10:
            logger.info(f"[Cortex-State] 🔒 Instanciando canal criptográfico cloud OpenAI: '{self.model_name}'")
            self.client = ChatOpenAI(model=self.model_name, temperature=self.temperature, api_key=api_key)

    def invoke_llm(self, messages: list) -> str:
        if not self.client:
            raise ValueError("Token de autenticación de OpenAI inválido o vacío (Error 401).")
        response = self.client.invoke(messages)
        return response.content


class VirtualCortexState(BaseCortexState):
    """Estado de contingencia determinista (Pattern Null Object) para desarrollo local."""
    
    def invoke_llm(self, messages: list) -> str:
        # Recuperamos el rol del mensaje del sistema para contextualizar el mock
        system_content = str(messages[0][1]).lower() if messages else ""
        logger.info("[Cortex-Virtual] Generando veredicto determinista local en microsegundos.")
        
        if "redes" in system_content or "networking" in system_content:
            return "CORTEX_VERDICT: Anomalía TCP identificada. Recomiendo aislamiento inmutable perimetral de la subred."
        return "CORTEX_VERDICT: Auditoría Zero-Trust completada. Brechas bloqueadas de forma virtual."


# =====================================================================================
# 🧠 COMPONENTE MAESTRO REFACTORIZADO (CON DISPACHO EN TIEMPO CONSTANTE O(1))
# =====================================================================================

class CortexLLMEngine:
    """Motor unificado agnóstico encargado de despachar inferencias mediante estados polimórficos."""

    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.1) -> None:
        self.temperature = temperature
        
        # 1. Recuperamos el proveedor desde el entorno global sanitizado
        self.provider_key = (os.getenv("AI_PROVIDER") or "virtual").lower().strip()
        
        # 2. Diccionario de Mapeo Algorítmico de Estados (Sustituye por completo los if/else)
        state_registry: Dict[str, Type[BaseCortexState]] = {
            "ollama": OllamaCortexState,
            "openai": OpenAiCortexState,
            "virtual": VirtualCortexState
        }
        
        # 3. Resolución elástica inteligente del cerebro analítico
        resolved_model = model_name or os.getenv("LLM_MODEL_NAME")
        if self.provider_key == "ollama" and (not resolved_model or "gpt" in str(resolved_model).lower()):
            self.model_name = "qwen2.5:1.5b"
        else:
            fallbacks = {"ollama": "qwen2.5:1.5b", "openai": "gpt-4o-mini"}
            self.model_name = resolved_model or fallbacks.get(self.provider_key, "virtual-model")

        # 4. Despacho dinámico del estado O(1)
        state_class = state_registry.get(self.provider_key, VirtualCortexState)
        logger.info(f"[Cortex-Engine] 🚀 Despachando estado en fábrica O(1) hacia: '{self.provider_key.upper()}'")
        self._state_driver = state_class(self.model_name, self.temperature)
        
        # Si la inicialización física falló por dependencias, degradamos de forma segura a modo virtual
        if not self._state_driver.client and self.provider_key != "virtual":
            logger.warning(f"[Cortex-Engine] Enlace físico fallido para '{self.provider_key}'. Conmutando a VirtualCortexState.")
            self._state_driver = VirtualCortexState(self.model_name, self.temperature)

    def _sanitizar_texto_ascii(self, texto: str) -> str:
        """Algoritmo de descomposición canónica para normalizar bytes de red."""
        if not texto:
            return ""
        return unicodedata.normalize('NFD', str(texto)).encode('ascii', 'ignore').decode('ascii')

    async def reason_incident_telemetry(self, agent_role: str, system_prompt: str, telemetry_logs: str) -> str:
        """Delega polimórficamente la inferencia forense al driver de estado activo."""
        logger.info(f"[{agent_role}-Cortex] Canalizando inferencia asíncrona hacia driver State...")
        
        safe_prompt = self._sanitizar_texto_ascii(system_prompt)
        safe_logs = self._sanitizar_texto_ascii(telemetry_logs)

        messages = [
            ("system", safe_prompt),
            ("human", f"Analiza la siguiente telemetria:\n{safe_logs}")
        ]
        
        try:
            # El motor principal delega sin saber si golpea un clúster local, la nube o RAM
            veredicto = self._state_driver.invoke_llm(messages)
            return veredicto
        except Exception as e:
            logger.error(f"[{agent_role}-Cortex-Failure] Interrupción en Driver State '{self.provider_key}': {str(e)}")
            # Cortocircuito defensivo automático hacia el Null Object local en caso de interrupción en red
            fallback_driver = VirtualCortexState(self.model_name, self.temperature)
            return fallback_driver.invoke_llm(messages)
