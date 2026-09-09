"""
========================================================================================
🌌 PAQUETE COGNITIVO: INICIALIZADOR DE INSTANCIAS DE AGENTES COMPARTIDAS EN MEMORIA
========================================================================================
"""
from src.infrastructure.ai.supervisor import AsyncAgentSupervisor, compile_supervisor_workflow
from src.infrastructure.ai.workers import NetworkSpecialistWorker, SecurityZeroTrustWorker
from src.main_and_config import load_master_config_safely

# 1. Carga inicial unificada de la configuración corporativa para evitar duplicación de E/S
_MASTER_CONFIG = load_master_config_safely()

# 2. Inicialización estática del pool de trabajadores globales del enjambre MoA
_POOL_DE_WORKERS = [
    NetworkSpecialistWorker(agent_id="prod-worker-networking"),
    SecurityZeroTrustWorker(agent_id="prod-worker-zerotrust")
]

# 3. PATRÓN SINGLETON DE SAGA: Instancia compartida unificada inmune a colisiones de hilos
# Garantiza que main.py y use_cases operen exactamente sobre el mismo espacio de memoria en RAM
SUPERVISOR_GLOBAL = AsyncAgentSupervisor(
    workers=_POOL_DE_WORKERS,
    memory_repo=None,
    governance_engine=None,
    config=_MASTER_CONFIG
)

# Exportación explícita de símbolos del módulo (__all__) para un mapeo limpio O(1)
__all__ = [
    "SUPERVISOR_GLOBAL",
    "AsyncAgentSupervisor",
    "compile_supervisor_workflow"
]
