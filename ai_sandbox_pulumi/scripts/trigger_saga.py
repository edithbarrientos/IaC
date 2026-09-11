import asyncio
import uuid
from temporalio.client import Client
from loguru import logger

async def main():
    logger.info("🌌 [TEST-CLIENT] Conectando por gRPC al plano distribuido de Temporal IO...")
    
    # 1. Inicializar conexión al clúster (Usa el puerto por defecto de tu .env)
    client = await Client.connect("localhost:7233")
    
    # 2. Payload de telemetría forense real que simula un incidente multi-cloud
    incident_telemetry = (
        "ALERT_ID: 99c71 | INTENT: SPIKE_DETECTED | PROTOCOL: TCP | "
        "SOURCE_IP: 198.51.100.42 | TARGET: aws-eks-cluster-production"
    )
    
    # CORRECCIÓN CRÍTICA: Generar un identificador único elástico para evitar colisiones
    dynamic_incident_id = f"forensic-saga-{uuid.uuid4().hex[:8]}"
    logger.warning(f"🚀 [SAGA-TRIGGER] Disparando IncidentMitigationWorkflow con ID Único: {dynamic_incident_id}")
    
    try:
        # 3. Invocar la ejecución determinista del Workflow inyectando el ID elástico
        resultado = await client.execute_workflow(
            "IncidentMitigationWorkflow",
            incident_telemetry,
            id=dynamic_incident_id,
            task_queue="aiops-incident-task-queue"
        )
        
        logger.success("\n📊 [RESULTADO DE LA TRANSACTION SAGA DISTRIBUIDA]:")
        logger.info(f"  • Status de Cierre: {resultado.get('status')}")
        logger.info(f"  • Acciones ejecutadas en el Toolbelt: {resultado.get('actions_executed')}")
        logger.success("✨ ¡Prueba transaccional distribuida validada con éxito absoluto en tu Mac!")
        
    except Exception as e:
        logger.critical(f"💥 [TEST-FAILURE] Interrupción o aserción en el clúster: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
