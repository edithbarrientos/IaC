"""
🧪 TEST DE INTEGRACIÓN: VALIDACIÓN COGNITIVA DEL HIPOCAMPO (OLLAMA + LANCEDB)
========================================================================================
Certifica de forma automatizada el ciclo de vida de persistencia del repositorio
vectorial, midiendo la latencia real de la inferencia de embeddings con Ollama.
"""

import os
import time
import pytest
from loguru import logger
from src.infrastructure.ai.brains.hipocampoMemory import HipocampoMemoryController

@pytest.mark.asyncio
async def test_ciclo_vida_repositorio_vectorial():
    """Valida la consistencia de los inserts y queries usando embeddings reales."""
    logger.info("🧪 [TEST-SUITE] Inicializando validador de memoria semántica real...")
    
    # Instanciamos el controlador cerebral del Hipocampo
    hipocampo = HipocampoMemoryController()
    
    mock_incident = {
        "incident_id": "incident-pytest-real-embeddings-777",
        "cloud_provider": "aws",
        "raw_logs": "[Handshake-Failure] TLS version mismatch on perimetral gateway.",
        "security_risk_score": 95,
        "brain_rationale": "CORTEX_VERDICT: Aislamiento perimetral exitoso."
    }
    
    # ⏱️ CRONÓMETRO COGNITIVO FASE 1: Inserción con Generación de Embedding Real
    inicio_insert = time.perf_counter()
    exito_insert = await hipocampo.save_incident_memory(mock_incident)
    fin_insert = time.perf_counter()
    latencia_insert_ms = (fin_insert - inicio_insert) * 1000
    
    assert exito_insert is True, "La persistencia de memoria real colapsó."
    
    # ⏱️ CRONÓMETRO COGNITIVO FASE 2: Búsqueda Semántica Real con Ollama
    logger.info("🧪 [TEST-SUITE] Disparando query vectorial con embedding dinámico...")
    
    inicio_query = time.perf_counter()
    resultados = await hipocampo.recall_similar_incidents(mock_incident["raw_logs"], limit=1)
    fin_query = time.perf_counter()
    latencia_query_ms = (fin_query - inicio_query) * 1000
    
    assert len(resultados) > 0, "La consulta vectorial semántica retornó un conjunto vacío."
    
    # 📊 REGISTRO DE TELEMETRÍA Y MÉTRICAS REALES DE IA
    logger.success("✨ [TEST-SUITE] Ciclo de vida cognitivo evaluado con éxito rotundo.")
    logger.info(f"⏱️ [MÉTRICA_IA] Tiempo Ingesta + Embedding Real: {latencia_insert_ms:.4f} ms")
    logger.info(f"⏱️ [MÉTRICA_IA] Tiempo Query Semántica Real: {latencia_query_ms:.4f} ms")
    logger.info(f"⏱️ [MÉTRICA_IA] Latencia Total del Córtex: {(latencia_insert_ms + latencia_query_ms):.4f} ms")
    logger.info(f"📝 [QUERY_RESULTADO] Datos recuperados de LanceDB: {resultados}")
