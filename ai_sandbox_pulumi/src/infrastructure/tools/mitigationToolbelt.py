"""
⚙️ MÓDULO DE INFRAESTRUCTURA: HIGH-PERFORMANCE MITIGATION TOOLBELT (DRIVEN STRATEGY)
========================================================================================
Empaqueta comandos perimetrales mediante inyección de drivers polimórficos en O(1),
eliminando estructuras condicionales y optimizando el throughput de la CPU en la Mac.
"""

import os
import asyncio
from typing import Dict, Any, List, Type
from loguru import logger

# =====================================================================================
# 🔌 DRIVERS POLIMÓRFICOS DE EJECUCIÓN (ELIMINACIÓN ABSOLUTA DE IFS)
# =====================================================================================

class BaseExecutionDriver:
    """Contrato inmutable para las estrategias de ejecución en el sistema operativo."""
    async def run_command(self, binary: str, args: List[str], log_tag: str) -> bool:
        raise NotImplementedError


class SimulatedExecutionDriver(BaseExecutionDriver):
    """Driver encargado de cortocircuitar las llamadas de red en el Sandbox local."""
    async def run_command(self, binary: str, args: List[str], log_tag: str) -> bool:
        logger.success(f"✨ [{log_tag}-Sandbox] Simulación exitosa -> {binary} {' '.join(args)}")
        await asyncio.sleep(0.05) # Latencia mínima simulada de bus de datos
        return True


class RealProcessExecutionDriver(BaseExecutionDriver):
    """Driver de producción encargado de interactuar con los binarios de la Mac/AWS."""
    async def run_command(self, binary: str, args: List[str], log_tag: str) -> bool:
        full_cmd = [binary] + args
        try:
            # Ejecución no bloqueante multi-core de alto rendimiento
            process = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.success(f"⚙️ [{log_tag}] Comando ejecutado con éxito en la infraestructura física.")
                return True
            else:
                logger.error(f"💥 [{log_tag}-Failure] El subproceso retornó código de error: {stderr.decode('utf-8')}")
                return False
        except FileNotFoundError:
            logger.critical(f"💥 [{log_tag}-Failure] El binario '{binary}' no se encuentra instalado en la máquina.")
            return False


# =====================================================================================
# 🛠️ COMANDOS INMUTABLES PARAMETRIZADOS (PATRÓN COMMAND)
# =====================================================================================

class BaseMitigationTool:
    def __init__(self, driver: BaseExecutionDriver) -> None:
        self.driver = driver

    async def execute_action(self, target_id: str, metadata: Dict[str, Any]) -> bool:
        raise NotImplementedError


class AwsCliAislarInstanciaTool(BaseMitigationTool):
    """Encargado de aislar instancias EC2 modificando sus perfiles perimetrales."""
    async def execute_action(self, target_id: str, metadata: Dict[str, Any]) -> bool:
        sg_isolated = metadata.get("security_group_isolated", "sg-isolated-jail-99")
        logger.info(f"⚙️ [TOOL_AWS] Solicitando contención para la instancia EC2: {target_id}")
        
        # Declaramos los argumentos limpios del binario de AWS
        args = ["ec2", "modify-instance-attribute", "--instance-id", target_id, "--groups", sg_isolated]
        # Delegamos polimórficamente la ejecución al driver asignado sin preguntar el entorno
        return await self.driver.run_command(binary="aws", args=args, log_tag="TOOL_AWS")


class SshBashMitigationTool(BaseMitigationTool):
    """Encargado de inyectar scripts forenses inmutables para recolección de telemetría."""
    async def execute_action(self, target_id: str, metadata: Dict[str, Any]) -> bool:
        ip_host = metadata.get("ip_address", "127.0.0.1")
        logger.info(f"⚙️ [TOOL_SSH] Abriendo canal seguro gRPC/SSH hacia el host: {ip_host}")
        
        bash_script = "sudo netstat -tupn | grep ESTABLISHED > /tmp/forensic_dump.log"
        args = ["-o", "StrictHostKeyChecking=no", f"admin@{ip_host}", bash_script]
        return await self.driver.run_command(binary="ssh", args=args, log_tag="TOOL_SSH")


# =====================================================================================
# 🧠 COMPONENTE MAESTRO: CATÁLOGO REGISTRY DEL TOOLBELT O(1)
# =====================================================================================

class MitigationToolbeltRegistry:
    """Fábrica elástica encargada de inyectar el entorno e inicializar las herramientas."""
    def __init__(self) -> None:
        mode_key = (os.getenv("DEPLOYMENT_MODE") or "simulado").lower().strip()
        
        # Mapa de resolución de drivers en O(1)
        driver_factory: Dict[str, Type[BaseExecutionDriver]] = {
            "simulado": SimulatedExecutionDriver,
            "real": RealProcessExecutionDriver,
            "qa": RealProcessExecutionDriver,
            "produccion": RealProcessExecutionDriver
        }
        
        # Instanciamos el driver inmutable del ambiente
        resolved_driver_class = driver_factory.get(mode_key, SimulatedExecutionDriver)
        logger.info(f"🏭 [FÁBRICA_O1] Inyectando Driver de Mitigación para el entorno: '{mode_key.upper()}'")
        driver_instance = resolved_driver_class()
        
        # Composición limpia libre de ifs condicionales
        self._tools: Dict[str, BaseMitigationTool] = {
            "AWS_ISOLATE_EC2": AwsCliAislarInstanciaTool(driver=driver_instance),
            "SSH_FORENSIC_DUMP": SshBashMitigationTool(driver=driver_instance)
        }
        
    def get_tool(self, tool_key: str) -> BaseMitigationTool:
        return self._tools[tool_key.upper().strip()]

# Instancia global del catálogo
MITIGATION_TOOLBELT = MitigationToolbeltRegistry()
