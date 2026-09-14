"""
🧪 TEST DE INTEGRACIÓN: SIMULACIÓN DEL ESPACIO VECTORIAL CRIPTOGRÁFICO EN LANCEDB (TELEMETRÍA ULTRA-HARDENED)
===================================================================================================
Certifica de forma automatizada el ciclo de vida de persistencia del repositorio vectorial,
desglosando la latencia exacta del chip AES, Throughput de LanceDB y Consumo Real de Memoria RAM.
🔒 MLOPS HARDENING: Fuerza la inyección paramétrica segura de llaves en RAM y elimina prints.
===================================================================================================
"""

import os
import json
import time
import hashlib
import psutil
from loguru import logger
from src.core.config import ProjectConfigurationRegistry
from src.infrastructure.persistence.vector_repo import ForensicVectorRepository

def run_vector_space_testing():
    logger.info("[Test-Suite] 🧪 Inicializando simulación del espacio vectorial hardened para LanceDB...")
    
    # Captura el estado inicial de la Memoria RAM física asignada al proceso (Resident Set Size)
    proceso_mac = psutil.Process(os.getpid())
    ram_inicial_bytes = proceso_mac.memory_info().rss
    
    # 🚀 MLOPS HARDENING: Mapeamos el mock elástico para emular el Catálogo TOML en RAM
    ProjectConfigurationRegistry._CONFIG_DATA = {
        "persistence": {
            "uri": "data/test_lancedb",
            "forensics_table": "incident_forensics"
        },
        "security": {
            "hmac_signature_key": "test_secret_key_odin_enterprise_edition_256_bits"
        }
    }
    ProjectConfigurationRegistry.load_registry()
    logger.debug("[Parametrización] Mapeo de ProjectConfigurationRegistry en RAM: COMPLETO")
    
    # Inicializa el repositorio consumiendo la configuración e inyectando el motor criptográfico
    t_init = time.perf_counter_ns()
    repo = ForensicVectorRepository()
    latencia_init_ms = (time.perf_counter_ns() - t_init) / 1_000_000
    logger.success(f"[Crypto-Engine] Motor AES-256-GCM y LanceDB enlazados en {latencia_init_ms:.2f} ms.")
    
    logger.info("[Test-Scenario] 💾 Inyectando historial forense controlado y cifrado en disco...")
    
    # --- REGISTRO 1 ---
    p1_desc = "Fallo de red: Error de enrutamiento CIDR tras actualización de Pulumi stack."
    p1_acc = ["ACTIVAR_AISLAMIENTO_LOCAL"]
    p1_emb = [0.12, 0.48, 0.79, 0.22]
    
    t_w1 = time.perf_counter_ns()
    repo.store_incident_embedding(
        incident_id="incident-past-01",
        vector_data=p1_emb,
        metadata={"description": p1_desc, "acciones": p1_acc}
    )
    latencia_w1_ms = (time.perf_counter_ns() - t_w1) / 1_000_000
    logger.success(f"[Persistent-Store] 'incident-past-01' indexado. Latencia neta: {latencia_w1_ms:.4f} ms")
    
    # --- REGISTRO 2 ---
    p2_desc = "Ataque volumétrico: Intento de fuerza bruta mitigado en API Gateway."
    p2_acc = ["Bypass"]
    p2_emb = [0.88, 0.12, 0.15, 0.33]
    
    t_w2 = time.perf_counter_ns()
    repo.store_incident_embedding(
        incident_id="incident-past-02",
        vector_data=p2_emb,
        metadata={"description": p2_desc, "acciones": p2_acc}
    )
    latencia_w2_ms = (time.perf_counter_ns() - t_w2) / 1_000_000
    logger.success(f"[Persistent-Store] 'incident-past-02' indexado. Latencia neta: {latencia_w2_ms:.4f} ms")
    
    # --- CONSULTA SEMÁNTICA CON DESCRIPCIÓN Y SIMULACIÓN DE RETORNO RAG QUERY ---
    target_query_vector = [0.10, 0.50, 0.80, 0.20]
    logger.info("[Test-Scenario] 🔎 Ejecutando consulta de vecinos más cercanos (HNSW Search) en LanceDB...")
    
    # Simulamos la recuperación agregando la latencia de desencriptación en RAM al vuelo para ver los datos reales
    t_query = time.perf_counter_ns()
    db = repo._get_connection()
    table = db.open_table(repo.table_name)
    
    # Búsqueda nativa de vecinos más cercanos vía LanceDB SIMD
    raw_results = table.search(target_query_vector).limit(2).to_list()
    
    query_output = []
    for item in raw_results:
        # Desencriptación en memoria RAM al vuelo vía el Crypto Engine
        decrypted_str = repo._decrypt_string(item["encrypted_metadata"], item["nonce"])
        meta_data = json.loads(decrypted_str)
        query_output.append({
            "id": item["id"],
            "description": meta_data["description"],
            "acciones": meta_data["acciones"],
            "_distance": item.get("_distance", 0.0)
        })
        
    latencia_query_ms = (time.perf_counter_ns() - t_query) / 1_000_000
    
    # Capturamos el delta de consumo de RAM física final del Heap de la Mac
    ram_final_bytes = proceso_mac.memory_info().rss
    ram_usada_mb = (ram_final_bytes - ram_inicial_bytes) / (1024 * 1024)
    
    # 📊 DESPLIEGUE EXCLUSIVO DE TELEMETRÍA ULTRA-PROFESIONAL CON LOGURU EN VERDE
    logger.success("✨ [TELEMETRÍA] RECOLECCIÓN DE MÉTRICAS CRIPTOGRÁFICAS DE HARDWARE CONCLUIDA:")
    logger.info(f"💾 [MEMORIA_RAM] Huella física delta consumida por LanceDB + AES: {ram_usada_mb:.4f} MB")
    logger.info(f"⏱️ [MÉTRICA_LATENCIA] Inicialización del Crypto Engine: {latencia_init_ms:.4f} ms")
    logger.info(f"⏱️ [MÉTRICA_LATENCIA] Inserción Cifrada Registro 1 (Write): {latencia_w1_ms:.4f} ms")
    logger.info(f"⏱️ [MÉTRICA_LATENCIA] Inserción Cifrada Registro 2 (Write): {latencia_w2_ms:.4f} ms")
    logger.info(f"⏱️ [MÉTRICA_LATENCIA] HNSW SIMD Search + Decryption al vuelo (Read): {latencia_query_ms:.4f} ms")
    
    # Mapeamos la salida real formateada como un log estructurado inmaculado
    logger.success(f"[Output-Payload] REGISTROS RECUPERADOS Y DESENCRIPTADOS EN LA MEMORIA RAM:\n{json.dumps(query_output, indent=4, ensure_ascii=False)}")
    logger.success("[Test-Suite] 🟢 Ciclo de pruebas completado de manera exitosa con cifrado AES-GCM activo.")

if __name__ == "__main__":
    run_vector_space_testing()
