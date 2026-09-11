"""
🗃️ CAPA DE INFRAESTRUCTURA: HIGH-PERFORMANCE LANCEDB VECTOR REPOSITORY
========================================================================================
Manejador de persistencia inmutable de alta velocidad encargado de almacenar y consultar
vectores y logs forenses de incidentes utilizando el motor de almacenamiento local Lance.
"""

import os
from typing import Any, Dict, List, Optional, cast

# PARCHE MYPY: Silenciamos la falta de stubs internos de las librerías nativas
import lancedb  # type: ignore[import-untyped]
import pyarrow as pa  # type: ignore[import-untyped]
from loguru import logger

# =====================================================================================
# 🔌 STRATEGIES DE ALMACENAMIENTO VECTORIAL (ELIMINACIÓN DE IFS)
# =====================================================================================

class BaseStorageStrategy:
    """Contrato base inmutable para el almacenamiento del Hipocampo."""
    async def save_record(self, table_name: str, record: Dict[str, Any]) -> bool:
        raise NotImplementedError

    async def search_vector(
        self, table_name: str, embedding: List[float], limit: int
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError


class InMemorySimulatedStorage(BaseStorageStrategy):
    """Estrategia de Sandbox elástica local para desarrollo veloz sin E/S física."""
    
    async def save_record(self, table_name: str, record: Dict[str, Any]) -> bool:
        logger.success(f"✨ [HIPOCAMPO-Sandbox] Guardado simulado exitoso en tabla: {table_name}")
        return True

    async def search_vector(
        self, table_name: str, embedding: List[float], limit: int
    ) -> List[Dict[str, Any]]:
        logger.success("[HIPOCAMPO-Sandbox] Retornando coincidencia sintética desde memoria.")
        return [{
            "incident_id": "incident-dev-pasado-88",
            "security_risk_score": 85,
            "raw_logs": "Handshake timeout anterior corregido con aislamiento VPC.",
            "_distance": 0.12
        }]


class PhysicalLanceDbStorage(BaseStorageStrategy):
    """Driver de grado industrial encargado de transaccionar los archivos físicos .lance."""
    
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._db: Optional[lancedb.DBConnection] = None

    def _get_connection(self) -> lancedb.DBConnection:
        if self._db is None:
            os.makedirs(self.db_path, exist_ok=True)
            self._db = lancedb.connect(self.db_path)
        return self._db

    def _define_schema(self) -> pa.Schema:
        # 🚨 CORRECCIÓN CLAVE: Sincronizado a las 768 dimensiones reales de nomic-embed-text
        return pa.schema([
            pa.field("vector", pa.list_(pa.float32(), 768)),
            pa.field("incident_id", pa.string()),
            pa.field("cloud_provider", pa.string()),
            pa.field("security_risk_score", pa.int32()),
            pa.field("raw_logs", pa.string()),
            pa.field("brain_rationale", pa.string())
        ])

    async def save_record(self, table_name: str, record: Dict[str, Any]) -> bool:
        try:
            db = self._get_connection()
            schema = self._define_schema()
            if table_name in db.table_names():
                table = db.open_table(table_name)
                table.add([record])
            else:
                db.create_table(table_name, data=[record], schema=schema)
            logger.success("🗃️ [HIPOCAMPO_DB] Registro consolidado en tablas físicas .lance.")
            return True
        except Exception as e:
            logger.error(f"💥 [HIPOCAMPO-Failure] Error de E/S en LanceDB: {str(e)}")
            return False

    async def search_vector(
        self, table_name: str, embedding: List[float], limit: int
    ) -> List[Dict[str, Any]]:
        try:
            db = self._get_connection()
            if table_name not in db.table_names():
                return []
            table = db.open_table(table_name)
            raw_results = table.search(embedding).limit(limit).to_list()
            return cast(List[Dict[str, Any]], raw_results)
        except Exception as e:
            logger.error(
                f"💥 [HIPOCAMPO-Failure] Error escaneando las tablas vectoriales: "
                f"{str(e)}"
            )
            return []


# =====================================================================================
# 🧠 REPOSITORIO MAESTRO CON DESPACHO EN TIEMPO CONSTANTE O(1)
# =====================================================================================

class IncidentVectorRepository:
    """Catálogo orquestador de datos vectoriales parametrizado mediante el Patrón State."""

    def __init__(self, db_path: str = "data/lancedb") -> None:
        mode_key = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
        self.table_name = "incident_forensics"
        
        environment_factory: Dict[str, BaseStorageStrategy] = {
            "simulado": InMemorySimulatedStorage(),
            "real": PhysicalLanceDbStorage(db_path=db_path),
            "qa": PhysicalLanceDbStorage(db_path="data/test_lancedb"),
            "produccion": PhysicalLanceDbStorage(db_path=db_path)
        }
        
        self.storage = environment_factory.get(mode_key, environment_factory["simulado"])
        logger.info(f"🏭 [FÁBRICA_O1] Inyectado Driver de Persistencia para: '{mode_key.upper()}'")

    async def upsert_incident_vector(
        self, incident_data: Dict[str, Any], embedding: List[float]
    ) -> bool:
        record = {
            "vector": embedding,
            "incident_id": str(incident_data.get("incident_id")),
            "cloud_provider": str(incident_data.get("cloud_provider", "aws")),
            "security_risk_score": int(incident_data.get("security_risk_score", 0)),
            "raw_logs": str(incident_data.get("raw_logs", "")),
            "brain_rationale": str(incident_data.get("brain_rationale", ""))
        }
        return await self.storage.save_record(self.table_name, record)

    async def query_similar_incidents(
        self, query_embedding: List[float], limit: int = 2
    ) -> List[Dict[str, Any]]:
        return await self.storage.search_vector(self.table_name, query_embedding, limit)
