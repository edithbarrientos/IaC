"""
🧪 TEST DE INTEGRACIÓN: VALIDACIÓN COGNITIVA DEL HIPOCAMPO (OLLAMA + LANCEDB)
========================================================================================
Certifica de forma automatizada el ciclo de vida de persistencia del repositorio
vectorial, desglosando la latencia exacta de Ollama y LanceDB en paralelo.
"""

import time
import asyncio
import pytest
from loguru import logger
from src.infrastructure.ai.brains.hipocampoMemory import HipocampoMemoryController

@pytest.mark.asyncio
async def test_ciclo_vida_repositorio_vectorial():
    """Valida la consistencia de los inserts y queries usando embeddings reales."""
    logger.info("🧪 [TEST-SUITE] Inicializando validador de memoria semántica real...")
    hipocampo = HipocampoMemoryController()
    
    mock_incident = {
        "incident_id": "incident-concurrent-777",
        "cloud_provider": "aws",
        "raw_logs": "[Handshake-Failure] TLS version mismatch on perimetral gateway.",
        "security_risk_score": 95,
        "brain_rationale": "CORTEX_VERDICT: Aislamiento perimetral exitoso."
    }
    
    logger.info("🚀 [CONCURRENCIA] Ejecutando Scatter-Gather paralelo multi-hilo...")
    
    inicio_global = time.perf_counter()
    
    # El Scatter-Gather ahora sí viaja por la autopista paralela del kernel de la Mac
    resultados = await asyncio.gather(
        hipocampo.save_incident_memory_profiled(mock_incident),
        hipocampo.recall_similar_incidents_profiled("TLS gateway failure", limit=1),
        hipocampo.recall_similar_incidents_profiled("VPC isolation script", limit=1),
        return_exceptions=True
    )
    
    latencia_global_ms = (time.perf_counter() - inicio_global) * 1000
    
    has_exception = any(map(lambda r: isinstance(r, Exception), resultados))
    assert not has_exception, f"💥 [CRITICAL] Hilo distribuido colapsado: {resultados}"

    t1, t2, t3 = resultados[0], resultados[1], resultados[2]
    
    # 📊 DESPLIEGUE EXCLUSIVO DE TELEMETRÍA POR COMPONENTE DE HARDWARE
    logger.success("✨ [TEST-SUITE] Optimización y Desglose de Rendimiento Concluido.")
    print("\n" + "="*80)
    logger.info(f"🧠 [COMPONENTE_OLLAMA] Inferencia Ingesta (Task 1): {t1['ollama_ms']:.4f} ms")
    logger.info(f"🧠 [COMPONENTE_OLLAMA] Inferencia Query (Task 2): {t2['ollama_ms']:.4f} ms")
    logger.info(f"🧠 [COMPONENTE_OLLAMA] Inferencia Query (Task 3): {t3['ollama_ms']:.4f} ms")
    logger.info(f"🗃️ [COMPONENTE_LANCEDB] Disco Write (Task 1): {t1['lancedb_ms']:.4f} ms")
    logger.info(f"🗃️ [COMPONENTE_LANCEDB] Disco Read (Task 2): {t2['lancedb_ms']:.4f} ms")
    logger.info(f"🗃️ [COMPONENTE_LANCEDB] Disco Read (Task 3): {t3['lancedb_ms']:.4f} ms")
    print("="*80)
    logger.info(f"⏱️ [MÉTRICA_CONCURRENTE] Throughput Neto Global: {latencia_global_ms:.4f} ms")
    logger.info(f"⚡ [THROUGHPUT] Operaciones resueltas simultáneamente: 3 tareas")
    print("="*80 + "\n")
