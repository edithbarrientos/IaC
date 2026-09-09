"""Módulo de Interfaces y Protocolos del Dominio Core.

Define los contratos lógicos y abstractos del sistema mediante Python Protocols.
Permite la inyección de dependencias y la implementación de patrones estructurales
asegurando un desacoplamiento total frente a frameworks de infraestructura y nubes.

Información del Módulo:
    * Autor: Edith Barrientos 💻
    * Año: 2026 🚀
    * Estado: Proof of Concept (PoC)
    * Licencia: MIT / Enterprise Restricted Guardrails
    * Patrones de Diseño Relacionados: Strategy Pattern, Adapter Interface
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

# CORRECCIÓN DE IMPORTACIÓN: Eliminado el prefijo redundante 'src.' 
# para alinearse con el mypy_path establecido.
from core.entities import AuditLogEntry, IncidentContext


@runtime_checkable
class AgentStrategy(Protocol):
    """Protocolo estructural para Agentes Especialistas de la Capa Cognitiva.

    [PATRÓN DE DISEÑO: STRATEGY]
    Cualquier worker del enjambre (SRE, SecOps, FinOps) debe cumplir estrictamente
    con esta interfaz para habilitar el intercambio dinámico y polimórfico en caliente.
    """

    @property
    def agent_name(self) -> str:
        """Identificador único y público del agente en el plano de control.

        Returns:
            str: El nombre único asignado al worker.
        """
        ...

    async def execute_reasoning(self, context: IncidentContext) -> IncidentContext:
        """Ejecuta el análisis semántico y razonamiento del agente de forma asíncrona.

        Args:
            context (IncidentContext): El estado inmutable actual del incidente.

        Returns:
            IncidentContext: El nuevo estado enriquecido con el veredicto de la IA.
        """
        ...


@runtime_checkable
class VectorMemoryRepository(Protocol):
    """Protocolo estructural para el Repositorio de Persistencia Híbrido.

    [PATRÓN DE DISEÑO: ADAPTER INTERFACE / FACADE CONTRACT]
    Abstrae el plano de almacenamiento columnar y búsquedas vectoriales, independizando
    las reglas de negocio del motor real en disco (LanceDB / DuckDB).
    """

    async def query_similarity(self, vector_error: List[float]) -> Optional[Dict[str, Any]]:
        """Ejecuta una búsqueda de proximidad espacial en la caché semántica.

        Aplica algoritmos de Distancia de Coseno sobre índices HNSW acelerados por hardware.

        Args:
            vector_error (List[float]): El array numérico de embeddings que representa el fallo.

        Returns:
            Optional[Dict[str, Any]]: Datos del parche histórico o None si no hay coincidencia.
        """
        ...

    async def save_audit_trail(self, entry: AuditLogEntry) -> None:
        """Inmortaliza de forma inmutable la bitácora de control de gobierno.

        Escribe un registro de fragmento columnar (NoSQL) para auditorías regulatorias.

        Args:
            entry (AuditLogEntry): La entidad estructurada con la trazabilidad forense.
        """
        ...
