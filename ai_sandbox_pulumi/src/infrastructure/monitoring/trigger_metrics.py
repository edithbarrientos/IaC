"""
🚀 SCRIPT DISPARADOR ELÁSTICO DE TRÁFICO: EMULACIÓN DE CARGA MLOps EN INFRAESTRUCTURA
========================================================================================
Inyecta ráfagas de datos concurrentes directo al Singleton en memoria del proceso.
Garantiza la aparición inmediata de números y baldes en tu endpoint OpenMetrics.
========================================================================================
"""

import time
import asyncio
from loguru import logger
from src.infrastructure.monitoring.metrics import ProjectOdinMetricsRegistry

async def simulate_production_traffic():
    """Genera una carga asíncrona controlada simulando telemetría real del Edge y Kernel."""
    logger.info("📡 [METRICS-TRIGGER] Inicializando inyector elástico de tráfico perimetral...")
    
    # Aseguramos que las métricas lean tu config.toml paramétrico antes de arrancar
    ProjectOdinMetricsRegistry.initialize_registry()
    
    # Simulación de una tormenta elástica de 5 peticiones exitosas validadas por mTLS en APISIX
    logger.info("🔄 Simulando ráfaga concurrente en el Edge de Apache APISIX Gateway...")
    for _ in range(5):
        ProjectOdinMetricsRegistry.track_apisix_request(
            method="GET", 
            endpoint="/api/v1/forensics/RAG", 
            status_code="200", 
            client_id="odin-cortex-v1"
        )
        # Registramos latencias simuladas en segundos dentro de los baldes del histograma
        ProjectOdinMetricsRegistry.track_upstream_latency(
            endpoint="/api/v1/forensics/RAG", 
            cloud_provider="aws", 
            duration_seconds=0.012  # Cae en el balde paramétrico de 0.025s
        )

    # Simulación de anomalías TLS capturadas en el perímetro
    logger.warning("🚨 Simulando captura de anomalía criptográfica por falla de Handshake TLS...")
    ProjectOdinMetricsRegistry.track_network_anomaly(
        anomaly_type="TLS_HANDSHAKE_TIMEOUT", 
        gateway_host="cluster.local", 
        byte_count=512
    )

    # Simulación de pánico en Ring 0 interceptado por la sonda eBPF de Rust enviado vía PyO3
    logger.critical("🦀 Simulando interceptación física de syscall sys_enter_connect en el Kernel space...")
    ProjectOdinMetricsRegistry.track_checkpoint_kernel_panic(
        syscall_target="sys_enter_connect", 
        risk_level="critical"
    )
    
    logger.success("✨ [METRICS-TRIGGER] Ráfaga consolidada en la RAM con éxito.")
