import os
import json
from loguru import logger
from src.infrastructure.persistence.vector_repo import IncidentVectorRepository

def run_vector_space_testing():
    logger.info("[Test-Suite] 🧪 Inicializando simulación del espacio vectorial para LanceDB...")
    
    mock_config = {
        "persistence": {
            "lance_db_uri": "data/test_lancedb"
        }
    }
    
    repo = IncidentVectorRepository(config=mock_config)
    
    logger.info("[Test-Scenario] 💾 Inyectando historial forense controlado en disco...")
    repo.insert_incident_vector(
        incident_id="incident-past-01",
        description="Fallo de red: Error de enrutamiento CIDR tras actualización de Pulumi stack.",
        embedding=[0.12, 0.48, 0.79, 0.22],
        acciones=["ACTIVAR_AISLAMIENTO_LOCAL"]
    )
    
    repo.insert_incident_vector(
        incident_id="incident-past-02",
        description="Ataque volumétrico: Intento de fuerza bruta mitigado en API Gateway.",
        embedding=[0.88, 0.12, 0.15, 0.33],
        acciones=["Bypass"]
    )
    
    target_query_vector = [0.10, 0.50, 0.80, 0.20]
    logger.info("[Test-Scenario] 🔎 Ejecutando consulta de correlación de incidentes...")
    
    # CAPTURA DE LA SALIDA: Guardamos los resultados reales que regresa el repositorio
    query_output = repo.search_similar_incidents(query_embedding=target_query_vector, limit=2)
    
    # IMPRESIÓN DEL PAYLOAD DE SALIDA: Volcado JSON estructurado para ver el objeto real
    print("\n" + "="*88)
    print("📦 OBJETO DE SALIDA REAL DEL QUERY (RETORNO DE LANCEDB EN PYTHON):")
    print("="*88)
    print(json.dumps(query_output, indent=4, ensure_ascii=False))
    print("="*88 + "\n")
    
    logger.success("[Test-Suite] 🟢 Ciclo de pruebas completado de manera exitosa.")

if __name__ == "__main__":
    run_vector_space_testing()
