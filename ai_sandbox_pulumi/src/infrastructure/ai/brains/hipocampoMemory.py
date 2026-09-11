"""
🧠 MÓDULO COGNITIVO: HIPOCAMPO VECTOR MEMORY CONTROLLER (ULTRA HIGH-PERFORMANCE)
========================================================================================
Coordinador de embeddings optimizado mediante el Patrón Connection Pool Persistence
y Sockets HTTP Keep-Alive persistentes para erradicar micro-latencias de red.
"""

import os
import time
from typing import Any, Dict, List, Tuple

import httpx
from loguru import logger

from src.infrastructure.persistence.vector_repo import IncidentVectorRepository


class HipocampoMemoryController:
    """Controlador cerebral encargado del almacenamiento y recuperación semántica."""

    def __init__(self) -> None:
        self.mode = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
        self.repo = IncidentVectorRepository()
        self.url = "http://localhost:11434/api/embeddings"
        
        # 🚀 REUTILIZACIÓN DE CONSUMO: Sockets Keep-Alive de bajo nivel en RAM
        # Esto elimina el sobrecosto de crear y destruir clientes HTTP en cada llamada.
        self._http_client = httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=200),
            timeout=httpx.Timeout(30.0),
            trust_env=False
        )

    def _generate_synthetic_embedding(self) -> List[float]:
        """Genera un vector base flotante de 768 dimensiones para el Sandbox."""
        return [0.1] * 768

    async def _compute_embedding_profiled(self, text: str) -> Tuple[List[float], float]:
        """Calcula el embedding usando el pool persistente y caliente de sockets."""
        if self.mode == "simulado":
            return self._generate_synthetic_embedding(), 0.0
            
        inicio = time.perf_counter()
        try:
            # Consumo directo sobre el canal abierto
            response = await self._http_client.post(
                self.url,
                json={
                    "model": "nomic-embed-text",
                    "prompt": text,
                    "options": {
                        "keep_alive": "12h",
                        "num_thread": 4
                    }
                }
            )
            latencia_ms = (time.perf_counter() - inicio) * 1000
            vector = response.json()["embedding"]
            return vector, latencia_ms
        except Exception as e:
            logger.error(f"💥 [HIPOCAMPO-Failure] Error en HTTP Ollama: {str(e)}")
            return self._generate_synthetic_embedding(), 0.0

    async def save_incident_memory_profiled(
        self, incident_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Indexa la memoria utilizando el pool de conexiones calientes."""
        raw_logs = incident_data.get("raw_logs", "")
        vector, ollama_ms = await self._compute_embedding_profiled(raw_logs)
        
        inicio_io = time.perf_counter()
        await self.repo.upsert_incident_vector(incident_data, vector)
        lancedb_ms = (time.perf_counter() - inicio_io) * 1000
        
        return {"ollama_ms": ollama_ms, "lancedb_ms": lancedb_ms}

    async def recall_similar_incidents_profiled(
        self, raw_logs: str, limit: int = 2
    ) -> Dict[str, float]:
        """Consulta la base de datos a través del canal persistente de red."""
        vector, ollama_ms = await self._compute_embedding_profiled(raw_logs)
        
        inicio_io = time.perf_counter()
        await self.repo.query_similar_incidents(vector, limit)
        lancedb_ms = (time.perf_counter() - inicio_io) * 1000
        
        return {"ollama_ms": ollama_ms, "lancedb_ms": lancedb_ms}

    async def shutdown(self) -> None:
        """Drena y vacía de forma segura el pool de conexiones al terminar."""
        await self._http_client.aclose()
