from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from loguru import logger

AIOPS_METRICS_REGISTRY = CollectorRegistry()

HTTP_REQUESTS_TOTAL = Counter(
    "aiops_http_requests_total",
    "Total de peticiones HTTP procesadas por el API Gateway.",
    ["endpoint", "status_code"],
    registry=AIOPS_METRICS_REGISTRY
)

SAGA_THREAD_SYNC_LATENCY = Histogram(
    "aiops_saga_thread_sync_seconds",
    "Latencia de sincronización de hilos mediante el ThreadCoordinator.",
    registry=AIOPS_METRICS_REGISTRY
)

OLLAMA_INFERENCE_LATENCY = Histogram(
    "aiops_ollama_inference_seconds",
    "Tiempo de respuesta de la inferencia estructurada de Ollama por Agente.",
    ["agent_role"],
    registry=AIOPS_METRICS_REGISTRY
)

GOVERNANCE_RISK_SCORE = Gauge(
    "aiops_governance_risk_score",
    "Puntuación unificada de riesgo calculada en caliente por el MoA Engine.",
    ["incident_id"],
    registry=AIOPS_METRICS_REGISTRY
)

CORTEX_CIRCUIT_BREAKER_STATUS = Gauge(
    "aiops_cortex_circuit_breaker_status",
    "Estado de salud del Circuit Breaker del LLM (1 = Saludable/Cerrado, 0 = Abierto/Fallback).",
    registry=AIOPS_METRICS_REGISTRY
)

LANCEDB_OPERATION_LATENCY = Histogram(
    "aiops_lancedb_operation_seconds",
    "Tiempo de ejecución de operaciones vectoriales en disco local.",
    ["operation_type"],
    registry=AIOPS_METRICS_REGISTRY
)

PULUMI_MUTATION_SUCCESS_TOTAL = Counter(
    "aiops_pulumi_mutation_success_total",
    "Total de ejecuciones de mutaciones físicas/simuladas de Pulumi.",
    ["stack", "mode", "success"],
    registry=AIOPS_METRICS_REGISTRY
)

logger.success("[Metrics-Engine] Instrumentación avanzada de Prometheus cargada en el namespace O(1).")
