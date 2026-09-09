"""Módulo de Entidades del Dominio Puro de AIOps.

Este módulo define los esquemas de datos inmutables y autovalidados que rigen
el estado global de las transacciones distribuidas (Saga Pattern) y las bitácoras
de auditoría corporativa. Se encuentra completamente desacoplado de los motores
de infraestructura física y optimizado para PyArrow y Pydantic v2.

Información del Módulo:
    * Autor: Edith Barrientos 💻
    * Año: 2026 🚀
    * Estado: Enterprise Production Ready
    * Licencia: MIT / Enterprise Restricted Guardrails
    * Patrones de Diseño: Value Object, Immutable State Pattern
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IncidentContext(BaseModel):
    """Objeto inmutable de transferencia de estado global de la transacción Saga.

    Esta entidad encapsula el contexto semántico, técnico e histórico de un fallo
    detectado en el clúster observado. Viaja a través del Grafo Agéntico protegiendo
    el flujo contra mutaciones corruptas y garantizando la consistencia atómica.

    Attributes:
        incident_id (str): Identificador único universal UUIDv4 de la transacción.
        raw_logs (str): Trazas de pánico físicas capturadas crudas del microservicio.
        sanitized_logs (Optional[str]): Versión limpia de trazas filtradas de PII.
        proposed_patch (Optional[str]): Manifiesto declarativo IaC diseñado por SRE.
        ai_suggested_metric (Optional[str]): Esquema dinámico de métricas Prometheus.
        security_risk_score (float): Calificación flotante de riesgo bajo OWASP Top 10.
        self_healing_attempts (int): Contador estricto para mitigar bucles infinitos.
        is_approved_by_gov (bool): Bandera de autorización del Policy Interceptor.
        cloud_provider_target (str): Nube destino de reconciliación [google|aws|azure].
    """

    incident_id: str = Field(
        ..., 
        description="UUIDv4 único de la transacción distributiva Saga"
    )
    raw_logs: str = Field(
        ..., 
        description="Trazas de pánico crudas capturadas del microservicio"
    )
    sanitized_logs: Optional[str] = Field(
        None, 
        description="Logs limpios de PII filtrados en el Edge de red"
    )
    proposed_patch: Optional[str] = Field(
        None, 
        description="Código de infraestructura diseñado por el Agente SRE"
    )
    ai_suggested_metric: Optional[str] = Field(
        None, 
        description="Esquema dinámico de métricas Prometheus propuesto en vivo"
    )
    security_risk_score: float = Field(
        0.0, 
        description="Métrica flotante de riesgo bajo estándares OWASP Top 10"
    )
    self_healing_attempts: int = Field(
        0, 
        description="Contador estricto para mitigar bucles de alucinación cognitiva"
    )
    is_approved_by_gov: bool = Field(
        False, 
        description="Bandera de autorización expedida por el Policy Interceptor"
    )
    cloud_provider_target: str = Field(
        default="google", 
        description="Nube destino de reconciliación [google | aws | azure]"
    )


class AuditLogEntry(BaseModel):
    """Registro inmutable de gobernanza corporativa para persistencia NoSQL.

    Mapea de manera estricta los metadatos de las decisiones adoptadas por cada
    worker cognitivo del enjambre para auditoría legal, control de costes y análisis
    cruzado mediante consultas SQL analíticas de DuckDB.

    Attributes:
        audit_entry_id (str): UUIDv4 del registro físico en disco fragmentado (.lance).
        incident_id (str): Identificador único global del incidente correlacionado.
        timestamp (datetime): Marca de tiempo precisa de la confirmación transaccional.
        agent_name (str): Identificador del worker del enjambre [SRE | SecOps | FinOps].
        action_taken (str): Hito transaccional alcanzado durante el auto-healing.
        decision_rationale (str): Traza de pensamiento validada mediante algoritmos MCTS.
        security_risk_score (float): Score perimetral de seguridad auditado en vivo.
        financial_token_cost (int): Cantidad de tokens consumidos traducidos a costos.
    """

    audit_entry_id: str = Field(
        ..., 
        description="UUIDv4 del registro físico de auditoría forense"
    )
    incident_id: str = Field(
        ..., 
        description="ID del incidente correlacionado a nivel relacional lógico"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, 
        description="Marca de tiempo precisa de la confirmación del registro"
    )
    agent_name: str = Field(
        ..., 
        description="Nombre del Worker del enjambre Mixture-of-Agents"
    )
    action_taken: str = Field(
        ..., 
        description="Hito alcanzado o estado actual de la transacción Saga"
    )
    decision_rationale: str = Field(
        ..., 
        description="Cadena de pensamiento u opción validada mediante MCTS"
    )
    security_risk_score: float = Field(
        0.0, 
        description="Score de seguridad auditado bajo guardrails perimetrales"
    )
    financial_token_cost: int = Field(
        0, 
        description="Consumo financiero de tokens de inferencia de LLM"
    )
