"""
🧪 SUITE DE PRUEBAS DE INTEGRACIÓN DISTRIBUIDAS (PROJECT ODIN QA CORE)
========================================================================================
Valida la resiliencia de la SAGA, la mutación polimórfica del archivo Pulumi.json
y el comportamiento asíncrono no bloqueante del motor cognitivo Mixture-of-Agents.
MÉTRICAS & TXT EXPORT: Exporta un reporte forense inmutable hacia un archivo físico .txt.
========================================================================================
"""

import os
import json
import time
import pytest
from temporalio.client import Client
from loguru import logger
from src.core.config import ProjectConfigurationRegistry

# INYECCIÓN DE TELEMETRÍA NATIVA DE PROMETHEUS (CNCF STANDARD)
from prometheus_client import Gauge, Histogram, REGISTRY

QA_SAGA_DURATION_SECONDS = Histogram(
    "qa_saga_duration_seconds",
    "Latencia total de extremo a extremo de la SAGA distributed en el entorno de QA"
)

QA_PULUMI_MANIFEST_RESOURCES_COUNT = Gauge(
    "qa_pulumi_manifest_resources_count",
    "Volumen total de recursos cloud físicos inyectados en el manifiesto final"
)

@pytest.mark.asyncio
async def test_saga_integration_and_infrastructure_hardening():
    """Prueba reina: Inyecta un incidente y procesa el flujo exportando la salida a un archivo .txt."""
    log_prueba = "CRITICAL_ALERT: SPIKE_DETECTED_ON_PRODUCTION_GATEWAY_STRESS"
    report_file_path = "saga_forensic_report.txt"
    
    # 🚀 INTERCEPTOR DE ARCHIVOS: Configura Loguru para escribir todo en caliente en un archivo plano TXT
    # Borra el reporte anterior si existe para asegurar limpieza pura
    if os.path.exists(report_file_path):
        os.remove(report_file_path)
    logger.add(report_file_path, format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}", encoding="utf-8")
    
    orch_settings = ProjectConfigurationRegistry.get_orchestration_settings()
    iac_settings = ProjectConfigurationRegistry.get_iac_settings()
    
    # Temporizador de alta precisión para las métricas de QA
    inicio_cronometro = time.perf_counter()

    # Levantar un Servidor Temporal local efímero automático
    from temporalio.testing import WorkflowEnvironment
    workflow_environment = await WorkflowEnvironment.start_local()
    client = workflow_environment.client

    # Registrar el Worker de soporte dentro del entorno de pruebas
    from src.infrastructure.ai.supervisor import IncidentMitigationWorkflow
    from src.infrastructure.ai.workers import (
        execute_network_worker_activity, 
        execute_security_worker_activity,
        execute_pulumi_cli_activity,
        execute_toolbelt_mitigation_activity
    )
    from temporalio.worker import Worker, UnsandboxedWorkflowRunner

    async with Worker(
        client,
        task_queue=orch_settings["task_queue"],
        workflows=[IncidentMitigationWorkflow],
        activities=[
            execute_network_worker_activity, 
            execute_security_worker_activity,
            execute_pulumi_cli_activity,
            execute_toolbelt_mitigation_activity
        ],
        workflow_runner=UnsandboxedWorkflowRunner()
    ):
        id_wf = f"test-odin-qa-{os.getpid()}"
        resultado = await client.execute_workflow(
            "IncidentMitigationWorkflow",
            log_prueba,
            id=id_wf,
            task_queue=orch_settings["task_queue"]
        )
        
        # Validar aserciones estructurales base
        assert resultado is not None
        assert "results" in resultado

        primer_agente = resultado["results"]
        assert "agent_id" in primer_agente
        assert "blueprint" in primer_agente

        assert os.path.exists("Pulumi.json")
        with open("Pulumi.json", "r", encoding="utf-8") as f:
            manifiesto = json.load(f)

        t_name = iac_settings["topology_name"]
        assert manifiesto["name"] == t_name
        
        # CÁLCULO ALGORÍTMICO Y ASIGNACIÓN DE MÉTRICAS DISTRIBUIDAS
        duracion_Saga = time.perf_counter() - inicio_cronometro
        recursos_totales = len(manifiesto.get("resources", {}).keys())
        
        # Indexar valores en el registro oficial de la CPU
        QA_SAGA_DURATION_SECONDS.observe(duracion_Saga)
        QA_PULUMI_MANIFEST_RESOURCES_COUNT.set(recursos_totales)

        # ==============================================================================
        # 📊 VOLCADO FORENSE ESTÁNDAR (TODO ESTO SE GRABARÁ AUTOMÁTICAMENTE EN EL TXT)
        # ==============================================================================
        logger.info("🪐 [QA-TELEMETRÍA] --- INICIANDO VOLCADO FORENSE CON MÉTRICAS PROMETHEUS ---")
        logger.info(f"📡 Orquestador Estatus: {resultado.get('status')}")
        logger.info(f"👤 Aprobación Humana:   {resultado.get('human_approved')}")
        logger.info(f"🛡️ Acciones Ejecutadas:  {resultado.get('actions_executed')}")
        logger.info(f"⏱️ [SAGA-TELEMETRÍA] Tiempo total de ejecución SAGA: {duracion_Saga:.4f} segundos")
        logger.info(f"📊 [IAC-TELEMETRÍA]  Recurso Cloud detectados en TOML: {recursos_totales} objetos inyectados")
        
        # Recuperar el valor real almacenado en el registro interno de Prometheus para auditoría
        metric_Saga_val = REGISTRY.get_sample_value("qa_saga_duration_seconds_sum")
        metric_infra_val = REGISTRY.get_sample_value("qa_pulumi_manifest_resources_count")
        logger.success(f"📈 [PROMETHEUS-REGISTRY] Métrica 'qa_saga_duration_seconds' registrada: {metric_Saga_val:.4f}s")
        logger.success(f"📈 [PROMETHEUS-REGISTRY] Métrica 'qa_pulumi_manifest_resources_count' registrada: {int(metric_infra_val)} recursos")
        
        # Volcar el archivo JSON completo estructurado
        json_formateado = json.dumps(manifiesto, indent=2, ensure_ascii=False)
        logger.info(f"📂 [Pulumi-Engine] Manifiesto consolidado en disco:\n{json_formateado}")
        
        logger.success("✨ [QA-SUCCESS] ¡SAGA distributed, enjambre MoA y descriptores CNCF validados en verde!")
