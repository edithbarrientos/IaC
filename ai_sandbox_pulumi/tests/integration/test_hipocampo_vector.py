"""
🧪 TEST DE INTEGRACIÓN: VALIDACIÓN COGNITIVA DEL HIPOCAMPO (LANCEDB + PYTEST)
========================================================================================
Certifica de forma automatizada el ciclo de vida de persistencia del repositorio
vectorial, asegurando el cumplimiento de inserts y queries de vecinos cercanos.
"""

import os
import time
import pytest
from loguru import logger
from src.infrastructure.persistence.vector_repo import IncidentVectorRepository

@pytest.mark.asyncio
async def test_ciclo_vida_repositorio_vectorial():
    """Valida la consistencia transaccional de los inserts y queries en LanceDB."""
    logger.info("🧪 [TEST-SUITE] Inicializando validador de persistencia del Hipocampo...")
    repo = IncidentVectorRepository()
    
    mock_incident = {
        "incident_id": "incident-pytest-lancedb-888",
        "cloud_provider": "aws",
        "raw_logs": "[Handshake-Failure] TLS version mismatch on perimetral.",
        "security_risk_score": 92,
        "brain_rationale": "CORTEX_VERDICT: Mitigación preventiva aislando las llaves SSH."
    }
    
    mock_embedding = [0.25] * 384
    
    # ⏱️ METRICA 1: Cronómetro para la Fase de Inserción (Upsert)
    inicio_insert = time.perf_counter()
    exito_insert = await repo.upsert_incident_vector(mock_incident, mock_embedding)
    fin_insert = time.perf_counter()
    latencia_insert_ms = (fin_insert - inicio_insert) * 1000
    
    assert exito_insert is True, "La inserción vectorial colapsó de forma inesperada."
    
    # ⏱️ METRICA 2: Cronómetro para la Fase de Consulta (Query Heurística O(1))
    logger.info("🧪 [TEST-SUITE] Disparando query semántica hacia los archivos .lance...")
    
    inicio_query = time.perf_counter()
    resultados = await repo.query_similar_incidents(mock_embedding, limit=1)
    fin_query = time.perf_counter()
    latencia_query_ms = (fin_query - inicio_query) * 1000
    
    assert len(resultados) > 0, "La consulta vectorial retornó un conjunto vacío."
    
    # 📊 DESPLIEGUE OFICIAL DE MÉTRICAS Forenses en la Pantalla Principal
    logger.success("✨ [TEST-SUITE] Ciclo de vida vectorial evaluado de forma exitosa.")
    logger.info(f"⏱️ [MÉTRICA_LATENCIA] Fase 1 (Upsert Vectorial): {latencia_insert_ms:.4f} ms")
    logger.info(f"⏱️ [MÉTRICA_LATENCIA] Fase 2 (Query Semántica O1): {latencia_query_ms:.4f} ms")
    logger.info(f"⏱️ [MÉTRICA_LATENCIA] Throughput Global de Cómputo: {(latencia_insert_ms + latencia_query_ms):.4f} ms")
    logger.info(f"📝 [QUERY_RESULTADO] Datos recuperados del clúster: {resultados}")
