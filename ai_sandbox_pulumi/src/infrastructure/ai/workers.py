"""
👥 MÓDULO DE AGENTES ESPECIALISTAS COGNITIVOS (TEMPORAL DISTRIBUTED ACTIVITIES)
========================================================================================
Cada worker expone sus capacidades analíticas como actividades distribuidas. Detecta
de forma elástica si está en modo 'simulado' para cortocircuitar la inferencia de Ollama.
"""

import os
from temporalio import activity
from loguru import logger

# =========================================================================
# --- ACTIVIDAD DISTRIBUIDA 1: ANÁLISIS DE REDES ---
# =========================================================================

@activity.defn(name="execute_network_worker_activity")
async def execute_network_worker_activity(incident_logs: str) -> dict:
    """Actividad distribuida inmutable encargada del aislamiento forense de red."""
    mode = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
    logger.info(f"[Temporal-Activity] Agente de Red despertando en el clúster. Modo: {mode.upper()}")

    # 🚨 CORTOCIRCUITO TOTAL EN MODO SIMULADO: Evita tocar la red o colgarse esperando a Ollama
    if mode == "simulado":
        logger.info("[Worker-Net-Sandbox] Simulando análisis de red en microsegundos para desarrollo local...")
        return {
            "agent_id": "temporal-worker-networking-01",
            "security_risk_score": 65,
            "brain_rationale": "CORTEX_VERDICT: Sandbox de Red mitigado exitosamente de forma virtual en Temporal."
        }

    # --- FLUJO REAL DE PRODUCCIÓN / QA (GOLPEA A OLLAMA LOCAL) ---
    from src.infrastructure.ai.brains.cortexLlm import CortexLLMEngine
    cortex = CortexLLMEngine(temperature=0.1)
    system_prompt = "Eres un specialist de redes corporativas en AWS."
    veredicto = await cortex.reason_incident_telemetry("NetworkSpecialistWorker", system_prompt, incident_logs)
    
    return {
        "agent_id": "temporal-worker-networking-01",
        "security_risk_score": 65,
        "brain_rationale": veredicto
    }


# =========================================================================
# --- ACTIVIDAD DISTRIBUIDA 2: AUDITORÍA ZERO-TRUST ---
# =========================================================================

@activity.defn(name="execute_security_worker_activity")
async def execute_security_worker_activity(incident_logs: str) -> dict:
    """Actividad distribuida inmutable encargada del cumplimiento Zero-Trust."""
    mode = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
    logger.info(f"[Temporal-Activity] Agente de Seguridad despertando en el clúster. Modo: {mode.upper()}")

    # 🚨 CORTOCIRCUITO TOTAL EN MODO SIMULADO: Evita tocar la red o colgarse esperando a Ollama
    if mode == "simulado":
        logger.info("[Worker-Sec-Sandbox] Simulando auditoría Zero-Trust en microsegundos para desarrollo local...")
        return {
            "agent_id": "temporal-worker-zerotrust-01",
            "security_risk_score": 55,
            "brain_rationale": "CORTEX_VERDICT: Sandbox Zero-Trust auditado exitosamente de forma virtual en Temporal."
        }

    # --- FLUJO REAL DE PRODUCCIÓN / QA (GOLPEA A OLLAMA LOCAL) ---
    from src.infrastructure.ai.brains.cortexLlm import CortexLLMEngine
    cortex = CortexLLMEngine(temperature=0.1)
    system_prompt = "Eres un auditor de seguridad Zero Trust."
    veredicto = await cortex.reason_incident_telemetry("SecurityZeroTrustWorker", system_prompt, incident_logs)
    
    return {
        "agent_id": "temporal-worker-zerotrust-01",
        "security_risk_score": 55,
        "brain_rationale": veredicto
    }
