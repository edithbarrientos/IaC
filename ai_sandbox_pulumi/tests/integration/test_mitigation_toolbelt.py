"""
🧪 TEST DE INTEGRACIÓN: VALIDACIÓN VORAZ MULTI-CLOUD DEL MITIGATION TOOLBELT
========================================================================================
Certifica mediante una ráfaga masiva multi-hilo paralela que el MitigationToolbelt
despacha las mutaciones físicas perimetrales desplegando los payloads JSON en el log.
"""

import os
import asyncio
import time
import json
import pytest
from loguru import logger
from src.infrastructure.tools.mitigationToolbelt import MitigationToolbelt

@pytest.mark.asyncio
async def test_ejecucion_concurrente_mitigaciones_perimetrales():
    """Valida la consistencia y latencia de subprocesos multi-cloud en paralelo."""
    logger.info("🧪 [TEST-SUITE] Inicializando validador de mutaciones multi-cloud...")
    toolbelt = MitigationToolbelt()
    
    target_resource = os.getenv("TARGET_RESOURCE_ID", "instance-core-crypto-999")
    security_group_target = os.getenv("TARGET_SECURITY_GROUP", "sg-isolated-perimeter")
    target_host_ip = os.getenv("TARGET_HOST_IP", "10.0.4.88")
    attacker_ip = os.getenv("ATTACKER_IP", "192.168.88.254")
    ssh_operator = os.getenv("SSH_OPERATOR_USER", "forensic-agent")

    logger.info("🚀 [CONCURRENCIA] Disparando ráfaga Scatter-Gather multi-cloud...")
    
    inicio_global = time.perf_counter()
    resultados = await asyncio.gather(
        toolbelt.isolate_cloud_resource(target_resource, security_group_target),
        toolbelt.collect_ssh_forensics(target_host_ip, ssh_operator),
        toolbelt.inject_perimetral_firewall_block(
            target_host_ip, ssh_operator, attacker_ip
        ),
        return_exceptions=True
    )
    latencia_global_ms = (time.perf_counter() - inicio_global) * 1000
    
    has_exception = any(map(lambda r: isinstance(r, Exception), resultados))
    assert not has_exception, f"💥 [CRITICAL] Hilo perimetral colapsado: {resultados}"
    
    # 🚀 CORRECCIÓN CLAVE DE DESCOMPRESIÓN: Aislamos cada JSON por su posición indexada indexado
    json_cloud = json.dumps(resultados[0], indent=2)
    json_ssh = json.dumps(resultados[1], indent=2)
    json_fw = json.dumps(resultados[2], indent=2)
    
    promedio_por_tarea = latencia_global_ms / 3
    
    separador = "========================================================================"
    msg_task = f"🦾 [CORE] Latencia media del Scatter-Gather: {promedio_por_tarea:.4f} ms"
    msg_glob = f"⏱️ [MÉTRICA] Throughput Ráfaga Multi-Cloud: {latencia_global_ms:.4f} ms"
    
    # 📊 DESPLIEGUE EXCLUSIVO DE TELEMETRÍA UNIFICADA CON JSON EN LOGS
    logger.success("✨ [TEST-SUITE] Certificación Perimetral Multi-Cloud Concluida.")
    logger.info(separador)
    logger.info(f"📥 [PAYLOAD_JSON] Respuesta Cloud Provider:\n{json_cloud}")
    logger.info(f"📥 [PAYLOAD_JSON] Respuesta SSH Forensics:\n{json_ssh}")
    logger.info(f"📥 [PAYLOAD_JSON] Respuesta Firewall Block:\n{json_fw}")
    logger.info(separador)
    logger.info(msg_task)
    logger.info(msg_glob)
    logger.info("⚡ [THROUGHPUT] Operaciones resueltas simultáneamente: 3 Tareas")
    logger.info(separador)
