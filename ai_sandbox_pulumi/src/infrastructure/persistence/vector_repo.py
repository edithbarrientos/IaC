"""
🗄️ ADAPTADOR PERIMETRAL: REPOSITORIO VECTORIAL LANCEDB (ZERO-HARDCODE)
========================================================================================
Maneja el almacenamiento de embeddings analíticos y correlación forense de incidentes.
CERO HARDCODE: El nombre de la tabla y la URI se inyectan dinámicamente desde el TOML.
========================================================================================
"""

import lancedb
from loguru import logger
from src.core.config import ProjectConfigurationRegistry

class ForensicVectorRepository:
    def __init__(self) -> None:
        # Extrae las URIs y tablas parametrizadas
        settings = ProjectConfigurationRegistry.get_persistence_settings()
        self.db_uri = settings["uri"]
        self.table_name = settings["forensics_table"]
        self._db_connection = None

    def _get_connection(self):
        if not self._db_connection:
            self._db_connection = lancedb.connect(self.db_uri)
        return self._db_connection

    def store_incident_embedding(self, incident_id: str, vector_data: list, metadata: dict):
        """Almacena un vector forense de forma parametrizada bajo el control del TOML."""
        db = self._get_connection()
        logger.info(f"📊 [VECTOR-REPO] Escribiendo embedding en la tabla unificada: '{self.table_name}'")
        
        payload = [{
            "id": incident_id,
            "vector": vector_data,
            "metadata": json.dumps(metadata) if isinstance(metadata, dict) else str(metadata)
        }]
        
        try:
            if self.table_name in db.table_names():
                table = db.open_table(self.table_name)
                table.add(payload)
            else:
                db.create_table(self.table_name, data=payload)
            logger.success("[VECTOR-REPO] Vector indexado exitosamente.")
        except Exception as e:
            logger.error(f"[VECTOR-REPO-Failure] Colapso en persistencia elástica: {str(e)}")
