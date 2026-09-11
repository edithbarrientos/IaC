"""
🧠 MÓDULO COGNITIVO: HIPOCAMPO VECTOR MEMORY CONTROLLER (REAL EMBEDDINGS)
========================================================================================
Coordinador encargado de la generación de embeddings semánticos dinámicos utilizando
Ollama y la persistencia de datos indexados en el repositorio de LanceDB.
"""

import os
from typing import Dict, Any, List
from loguru import logger
from src.infrastructure.persistence.vector_repo import IncidentVectorRepository


class HipocampoMemoryController:
    """Controlador cerebral encargado del almacenamiento y recuperación semántica."""

    def __init__(self) -> None:
        self.mode = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
        self.repo = IncidentVectorRepository()

    def _generate_synthetic_embedding(self) -> List[float]:
        # 🚨 CORRECCIÓN CLAVE: Sincronizado a las 768 dimensiones reales del modelo
        return [0.1] * 768

    async def _compute_embedding(self, text: str) -> List[float]:
        """Calcula el embedding real llamando de forma asíncrona a Ollama."""
        if self.mode == "simulado":
            return self._generate_synthetic_embedding()
            
        try:
            from langchain_ollama import OllamaEmbeddings
            embeddings_engine = OllamaEmbeddings(
                model="nomic-embed-text",
                base_url="http://localhost:11434"
            )
            vector = await embeddings_engine.aembed_query(text)
            return vector
        except Exception as e:
            logger.error(f"💥 [HIPOCAMPO-Failure] Error generando embedding real: {str(e)}")
            return self._generate_synthetic_embedding()

    async def save_incident_memory(self, incident_data: Dict[str, Any]) -> bool:
        """Convierte los logs forenses en un vector y los consolida en LanceDB."""
        incident_id = incident_data.get("incident_id")
        raw_logs = incident_data.get("raw_logs", "")
        
        logger.info(f"🧠 [HIPOCAMPO] Indexando memoria semántica para: {incident_id}")

        vector_calculado = await self._compute_embedding(raw_logs)
        return await self.repo.upsert_incident_vector(incident_data, vector_calculado)

    async def recall_similar_incidents(
        self, raw_logs: str, limit: int = 2
    ) -> List[Dict[str, Any]]:
        """Busca patrones de fallas pasadas basándose en la telemetría actual."""
        logger.info("🧠 [HIPOCAMPO] Escaneando memoria histórica para buscar fallas similares...")

        vector_calculado = await self._compute_embedding(raw_logs)
        return await self.repo.query_similar_incidents(vector_calculado, limit)
