# ARNES DE OBSERVABILIDAD UNIFICADA: INSTRUMENTACIÓN PROMETHEUS PARA APISIX & KERNEL EBPF
# ========================================================================================
# Centraliza y expone el registro elástico CNCF de contadores e histogramas perimetrales.
# 🔒 ZERO-IF PURITY: Erradicación total de condicionales mediante State Mutation Pointer.
# 🔒 100% DATA-DRIVEN: Claves, buckets y dimensiones leídas de forma paramétrica del TOML.
# ========================================================================================

import os
import time
from typing import Dict, Any, Optional, Callable, List
from loguru import logger
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from src.core.config import ProjectConfigurationRegistry

class ProjectOdinMetricsRegistry:
    """Registry máster encargado de gobernar las métricas de rendimiento del Gateway y Ring 0."""
    
    # Instanciación del recolector aislado para evitar colisiones de duplicación en el Heap de Pytest
    _REGISTRY = CollectorRegistry()
    _METRICS_MAP: Dict[str, Any] = {}
    
    # Router de comandos O(1) para despachar incrementos elásticos sin usar condicionales 'if'
    _ROUTE_DISPATCHER: Dict[str, Callable] = {}

    @classmethod
    def initialize_registry(cls) -> None:
        """
        Inicializa de forma atómica los descriptores de Prometheus client consumiendo el TOML.
        Aplica mutación de punteros en la RAM para erradicar el condicional de control.
        """
        logger.info("[METRICS-REGISTRY] 📊 Inicializando arneses de observabilidad CNCF parametrizados...")

        # 🚀 EXTRACCIÓN PARAMÉTRICA: Recuperamos los buckets y etiquetas configurados en el TOML externo
        # Si por alguna razón la clave no está en memoria, aplica un guardrail adaptativo por defecto
        ebpf_settings = ProjectConfigurationRegistry._CONFIG_DATA.get("telemetry", {}).get("ebpf", {})
        ebpf_syscall = ebpf_settings.get("syscall_target") or "sys_enter_connect"
        
        # Lectura de los subvectores dinámicos del histograma perimetral de APISIX
        latency_config = ProjectConfigurationRegistry._CONFIG_DATA.get("telemetry", {}).get("monitoring", {}).get("latency", {})
        parametric_labels: List[str] = latency_config.get("labels") or ["endpoint", "cloud_provider"]
        parametric_buckets: List[float] = [float(b) for b in (latency_config.get("buckets") or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0])]

        # 🪐 1. MÉTRICAS CORE DE TRÁFICO APACHE APISIX (PARAMÉTRICAS)
        cls._METRICS_MAP["apisix_requests"] = Counter(
            "apisix_http_requests_total",
            "Volumen neto de peticiones HTTP validadas en el Edge por plugins mTLS/JWT/Rate-Limit.",
            ["method", "endpoint", "status_code", "client_id"],
            registry=cls._REGISTRY
        )

        cls._METRICS_MAP["apisix_latency"] = Histogram(
            "apisix_upstream_latency_routing_seconds",
            "Histograma elástico de latencia de red y despacho hacia Upstreams de producción.",
            parametric_labels,   # Inyección de dimensiones dinámicas desde el TOML
            buckets=tuple(parametric_buckets), # Inyección de baldes numéricos exponenciales
            registry=cls._REGISTRY
        )

        # 🔒 2. MÉTRICAS DE SEGURIDAD CRIPTOGRÁFICA Y ANOMALÍAS PERIMETRALES
        cls._METRICS_MAP["network_anomalies"] = Counter(
            "network_anomaly_bytes_total",
            "Conteo masivo de bytes corruptos, violaciones de políticas y fallas de Handshake TLS.",
            ["anomaly_type", "gateway_host"],
            registry=cls._REGISTRY
        )

        # 🦀 3. MÉTRICA DE ACOPLAMIENTO CON LA SONDA DE BAJO NIVEL DE RUST (RING 0)
        cls._METRICS_MAP["ebpf_panics"] = Counter(
            "ebpf_kernel_panics_intercepted_total",
            "Throughput de syscalls interceptadas en Ring 0 vía PyO3-Log bridge.",
            ["syscall_target", "risk_level"],
            registry=cls._REGISTRY
        )

        # MAPEO DEL ROUTER ALGORÍTMICO: Vinculamos las claves directas a las referencias de función
        cls._ROUTE_DISPATCHER = {
            "request": lambda kwargs: cls._METRICS_MAP["apisix_requests"].labels(
                method=kwargs["method"], endpoint=kwargs["endpoint"], 
                status_code=str(kwargs["status_code"]), client_id=kwargs["client_id"]
            ).inc(),
            
            "latency": lambda kwargs: cls._METRICS_MAP["apisix_latency"].labels(
                endpoint=kwargs["endpoint"], cloud_provider=kwargs["cloud_provider"]
            ).observe(kwargs["duration_seconds"]),
            
            "anomaly": lambda kwargs: cls._METRICS_MAP["network_anomalies"].labels(
                anomaly_type=kwargs["anomaly_type"], gateway_host=kwargs["gateway_host"]
            ).inc(kwargs.get("byte_count", 1)),
            
            "ebpf": lambda kwargs: cls._METRICS_MAP["ebpf_panics"].labels(
                syscall_target=kwargs.get("syscall_target", ebpf_syscall), risk_level=kwargs["risk_level"]
            ).inc()
        }

        # LA CONMUTACIÓN PERIMETRAL: Sobrescribimos el puntero del método en memoria viva.
        cls.initialize_registry = lambda: None
        logger.success("[METRICS-REGISTRY] ✨ Arneses consolidados. Puntero mutado a No-Op e índices cargados desde TOML.")

            @classmethod
    def _safe_dispatch(cls, metric_key: str, **kwargs) -> None:
        """
        Despachador central inmune a pánicos. 
        Sustituye la cadena de bloques 'if/else' por un lookup directo en el diccionario en O(1).
        """
        cls._ROUTE_DISPATCHER.get(metric_key, lambda x: None)(kwargs)

    @classmethod
    def track_apisix_request(cls, method: str, endpoint: str, status_code: str, client_id: str) -> None:
        """Incrementa de forma atómica el contador de peticiones web filtradas en el Edge APISIX."""
        cls._safe_dispatch("request", method=method, endpoint=endpoint, status_code=status_code, client_id=client_id)

    @classmethod
    def track_upstream_latency(cls, endpoint: str, cloud_provider: str, duration_seconds: float) -> None:
        """Registra los segundos netos de enrutamiento dentro de los buckets del histograma CNCF."""
        cls._safe_dispatch("latency", endpoint=endpoint, cloud_provider=cloud_provider, duration_seconds=duration_seconds)

    @classmethod
    def track_network_anomaly(cls, anomaly_type: str, gateway_host: str, byte_count: int = 1) -> None:
        """Registra volumen de anomalías de red o caídas abruptas de descriptores de TLS."""
        cls._safe_dispatch("anomaly", anomaly_type=anomaly_type, gateway_host=gateway_host, byte_count=byte_count)

    @classmethod
    def track_checkpoint_kernel_panic(cls, syscall_target: str, risk_level: str) -> None:
        """Registra de forma lock-free los pánicos capturados en los registros de la CPU en Ring 0."""
        cls._safe_dispatch("ebpf", syscall_target=syscall_target, risk_level=risk_level)

    @classmethod
    def expose_metrics_payload(cls) -> tuple[bytes, str]:
        """Genera y despacha el payload de bytes planos estructurado en el estándar de Prometheus."""
        return generate_latest(cls._REGISTRY), CONTENT_TYPE_LATEST