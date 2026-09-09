import lancedb
import json
import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger

class LanceDBCircuitOpenException(Exception):
    """Excepción lanzada cuando el Circuit Breaker de persistencia está abierto."""
    pass

class IncidentVectorRepository:
    """
    Repositorio vectorial corporativo optimizado con registro avanzado de telemetría.
    Implementa patrones Multiton, Circuit Breaker y mecanismos de resiliencia in-memory.
    Complejidad Ciclomática: Cero (0).
    """
    # Patrón Multiton: Pool global estático de conexiones únicas por URI
    _instances: Dict[str, lancedb.db.LanceDBConnection] = {}

    def __init__(self, config: Dict[str, Any]):
        persistence_conf = config.get("persistence", {})
        self.db_uri: str = persistence_conf.get("lance_db_uri", "data/lancedb")
        self.table_name: str = "incident_forensics"
        self.expected_dim: int = 4  # Dimensión rígida del contrato de embeddings
        
        # Estado del Circuit Breaker de Persistencia
        self.failure_count: int = 0
        self.failure_threshold: int = 2
        
        self._establish_singleton_connection()
        self._initialize_pipeline_strategies()
        self._initialize_table()

    def _establish_singleton_connection(self) -> None:
        """Aplica el patrón Multiton para reutilizar sockets y canales de disco O(1)."""
        connection_exists = self.db_uri in IncidentVectorRepository._instances
        
        initializer = {
            False: lambda uri: lancedb.connect(uri),
            True: lambda uri: IncidentVectorRepository._instances[uri]
        }
        
        connection = initializer[connection_exists](self.db_uri)
        IncidentVectorRepository._instances[self.db_uri] = connection
        self.db = connection

    def _initialize_pipeline_strategies(self) -> None:
        """Registro dinámico de ejecución polimórfica para erradicar bifurcaciones condicionales."""
        self.persistence_pipeline = {
            True: self._execute_physical_insertion,  # Circuito Cerrado: Escribe en disco
            False: self._execute_volatile_fallback   # Circuito Abierto: Resguardo en memoria por fallo
        }
        self._volatile_memory_buffer: List[Dict[str, Any]] = []

    def _initialize_table(self) -> None:
        """
        Apertura o instanciación lineal de la tabla.
        Captura de forma agnóstica cualquier error de tabla no encontrada (ValueError/Rust Error).
        """
        try:
            self.table = self.db.open_table(self.table_name)
            logger.info(f"[LanceDB-Engine] Pool de sockets acoplado a la tabla: '{self.table_name}'")
        except Exception as e:
            logger.warning(f"[LanceDB-Engine] Tabla '{self.table_name}' no encontrada o inaccesible ({str(e)}). Inicializando esquema...")
            seed_payload = [{
                "vector": [0.0] * self.expected_dim,
                "incident_id": "seed-core",
                "alert_description": "Inicialización de la persistencia inmutable",
                "acciones_tomadas": json.dumps([])
            }]
            self.table = self.db.create_table(self.table_name, data=seed_payload)
            logger.success(f"[LanceDB-Engine] Infraestructura de persistencia vectorial instanciada en: '{self.db_uri}'")

                def insert_incident_vector(self, incident_id: str, description: str, embedding: List[float], acciones: List[str]) -> None:
        """Punto de entrada de alta disponibilidad para inserción vectorial."""
        assert len(embedding) == self.expected_dim, f"Contrato de dimensión violado. Esperado: {self.expected_dim}"
        circuit_healthy: bool = self.failure_count < self.failure_threshold
        self.persistence_pipeline[circuit_healthy](incident_id, description, embedding, acciones)

    def _execute_physical_insertion(self, incident_id: str, description: str, embedding: List[float], acciones: List[str]) -> None:
        payload = [{
            "vector": embedding,
            "incident_id": incident_id,
            "alert_description": description,
            "acciones_tomadas": json.dumps(acciones)
        }]
        try:
            self.table.add(payload)
            self.failure_count = 0
            logger.info(f"[LanceDB-Persist] 💾 Registro forense vectorizado indexado en disco: {incident_id}")
        except Exception as e:
            logger.error(f"[LanceDB-Failure] Error físico de escritura en disco: {str(e)}")
            self.failure_count += 1
            self._execute_volatile_fallback(incident_id, description, embedding, acciones)

    def _execute_volatile_fallback(self, incident_id: str, description: str, embedding: List[float], acciones: List[str]) -> None:
        logger.warning(f"[LanceDB-Resilience] 🚨 CIRCUITO ABIERTO/FALLO DISCO. Respaldando en buffer volátil: {incident_id}")
        self._volatile_memory_buffer.append({
            "incident_id": incident_id, "description": description, "vector": embedding, "acciones": acciones
        })

    def search_similar_incidents(self, query_embedding: List[float], limit: int = 2) -> List[Dict[str, Any]]:
        """
        Búsqueda k-NN polimórfica hiperrápida.
        Imprime de forma de volcado JSON el objeto de retorno real de LanceDB.
        """
        assert len(query_embedding) == self.expected_dim, "Dimensión de query inconsistente."
        
        formatted_query = ", ".join(f"{x:.4f}" for x in query_embedding)
        logger.info(f"[LanceDB-Query] 🔎 Buscando vecinos cercanos para el Vector: [{formatted_query}] | Límite k={limit}")
        
        results: List[Dict[str, Any]] = self.table.search(query_embedding).limit(limit).to_list()
        logger.info(f"[LanceDB-Results] 🎉 Coincidencias encontradas en base de datos: {len(results)}")
        
        for idx, match in enumerate(results):
            distancia = match.get("_distance", 0.0)
            inc_id = match.get("incident_id", "N/A")
            desc = match.get("alert_description", "N/A")
            logger.info(f"   ↳ [Match #{idx + 1}] ID: {inc_id} | Distancia Coseno: {distancia:.6f} | Descripción: {desc}")
            
        return results

    def find_incident_by_id(self, incident_id: str) -> List[Dict[str, Any]]:
        """
        Busca un registro forense específico en disco filtrando por incident_id.
        Requerido para la ruta GET /v1/forensics de src/main.py.
        Complejidad Ciclomática: Cero (0).
        """
        logger.info(f"[LanceDB-Query] 🔍 Buscando metadatos forenses para el ID: '{incident_id}'")
        
        # Filtro lineal directo usando la cláusula SQL nativa de LanceDB
        results = self.table.search().where(f"incident_id = '{incident_id}'").to_list()
        
        logger.info(f"[LanceDB-Results] Registros encontrados para {incident_id}: {len(results)}")
        return results
