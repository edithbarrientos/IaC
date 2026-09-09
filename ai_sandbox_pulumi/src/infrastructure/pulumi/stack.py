"""Módulo de Automatización e Inyección Multi-Cloud de AIOps.

Este componente implementa la fachada programática de Pulumi Automation API con
capacidades avanzadas de autodetección del entorno físico perimetral en cascada.
Elimina bloques condicionales if/else mediante un Mapeo de Despacho Polimórfico.

Información del Módulo:
    * Autor: Alejandro Marín 💻
    * Año: 2026 🚀
    * Estado: Proof of Concept (PoC)
    * Licencia: MIT / Enterprise Restricted Guardrails
    * Patrones de Diseño: Abstract Factory, Facade, Registry Pattern, Dispatch Map
"""

import asyncio
import sys
from typing import Any, Callable, Dict, Optional

import httpx
from loguru import logger
from pulumi import automation as auto
from pydantic_settings import BaseSettings, SettingsConfigDict

# Removemos el manejador por defecto para evitar duplicidad de trazas
logger.remove()

# Formato de producción scannable con iconos funcionales inyectados
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level.icon} {level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# Añadimos el nuevo formateador mapeando los iconos a los niveles de Loguru
logger.add(
    sys.stderr,
    format=LOG_FORMAT,
    level="INFO",
    colorize=True
)

# Personalización estricta de iconos por nivel de gravedad (Visual Anchors)
logger.level("TRACE", icon="🔍")
logger.level("DEBUG", icon="⚙️")
logger.level("INFO", icon="ℹ️")
logger.level("SUCCESS", icon="✅")
logger.level("WARNING", icon="⚠️")
logger.level("ERROR", icon="🚨")
logger.level("CRITICAL", icon="🔥")


class CloudSettings(BaseSettings):
    """Mapea y autodetecta las variables del entorno físico de ejecución.

    Attributes:
        cloud_provider (Optional[str]): El proveedor configurado explícitamente.
        cloud_region (str): La región geográfica destino para los recursos.
        environment (str): El identificador del entorno operativo del stack.
        project_name (str): El nombre del proyecto registrado en Pulumi.
    """
    
    cloud_provider: Optional[str] = None  
    cloud_region: str = "us-central1"
    environment: str = "poc-sandbox"
    project_name: str = "ai-sandbox-pulumi"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )


class PulumiAutomationFacade:
    """Fachada industrial encargada de orquestar Pulumi y autodetectar la nube viva.

    [PATTERN: FACADE]
    Encapsula Pulumi Automation API proveyendo un punto único de contacto
    asíncrono para mutaciones y despliegues de parches de red de caja negra.
    """

    def __init__(self) -> None:
        """Inicializa la fachada resolviendo la nube mediante prioridades en cascada."""
        self.settings: CloudSettings = CloudSettings()
        
        # [PATTERN: REGISTRY / DISPATCH MAP]
        # Registro polimórfico de carga perezosa para eliminar bloques if/else dinámicamente
        self._topology_registry: Dict[str, Callable[[], Dict[str, Any]]] = {
            "google": self._load_gcp_topology,
            "azure": self._load_azure_topology,
            "aws": self._load_aws_topology
        }
        
        self.final_provider: str = self._resolve_cloud_provider()
        self.stack_name: str = f"{self.settings.environment}-{self.final_provider}"

    def _resolve_cloud_provider(self) -> str:
        """Resuelve el proveedor en la nube utilizando prioridades en cascada.

        [PATTERN: CHAIN OF RESPONSIBILITY]
        Aplica un flujo zero-trust: evalúa la configuración explícita, o interroga
        a los Servidores de Metadatos locales para identificar la nube.

        Returns:
            str: El identificador en minúsculas del proveedor [google | aws | azure].
        """
        if self.settings.cloud_provider:
            logger.info(
                f"Control explícito detectado. Proveedor: "
                f"{self.settings.cloud_provider.upper()}"
            )
            return self.settings.cloud_provider.lower()

        # Autodetección nativa en Google Cloud Platform (GCP)
        try:
            response = httpx.get(
                "http://google.internal", 
                headers={"Metadata-Flavor": "Google"}, 
                timeout=0.3
            )
            if response.status_code == 200:
                logger.success("Entorno nativo de GOOGLE CLOUD (GCP) identificado.")
                return "google"
        except httpx.RequestError:
            logger.trace("Servidor de metadatos de Google Cloud no disponible.")

        # Autodetección nativa en Amazon Web Services (AWS)
        try:
            response = httpx.get("http://169.254.169", timeout=0.3)
            if response.status_code == 200:
                logger.success("Entorno nativo de AMAZON WEB SERVICES (AWS) identificado.")
                return "aws"
        except httpx.RequestError:
            logger.trace("Servidor de metadatos de AWS (IMDS) no disponible.")

        # Fallback seguro para desarrollo local
        logger.warning(
            "No se localizó ninguna nube viva. Activando Fallback de desarrollo: GOOGLE"
        )
        return "google"

    # ==============================================================================
    # SUB-MÓDULOS DE CARGA LAZY DEL REGISTRO (POLIMORFISMO DE ESTRATEGIA)
    # ==============================================================================
    def _load_gcp_topology(self) -> Dict[str, Any]:
        """Carga y retorna de forma perezosa el programa de GCP."""
        from src.infrastructure.pulumi.gcp_topology import google_sandbox_program
        return google_sandbox_program()

    def _load_azure_topology(self) -> Dict[str, Any]:
        """Carga y retorna de forma perezosa el programa de Azure."""
        from src.infrastructure.pulumi.azure_topology import azure_sandbox_program
        return azure_sandbox_program()

    def _load_aws_topology(self) -> Dict[str, Any]:
        """Gestiona el lanzamiento planificado del adaptador de AWS."""
        logger.error("Se solicitó el adaptador de AWS pero no se ha consolidado.")
        raise NotImplementedError("Adaptador de AWS planeado para sprint posterior.")

    def _get_inline_program(self) -> Callable[[], Dict[str, Any]]:
        """Carga la topología física modular resolviendo la llave en el Registro.

        [PATTERN: FACTORY VIA DICTIONARY DISPATCH]
        Busa la estrategia en el diccionario. Si la llave no existe, lanza un
        error controlado inmediatamente, eliminando la necesidad de evaluar if/else.

        Returns:
            Callable[[], Dict[str, Any]]: La función del programa inline de Pulumi.
        """
        provider: str = self.final_provider
        logger.debug(f"Despachando estrategia del Registro para: {provider.upper()}")
        
        # Recupera el método ejecutor del mapa o lanza KeyError controlado
        topology_initializer = self._topology_registry.get(provider)
        
        if not topology_initializer:
            raise ValueError(f"Proveedor no soportado en la PoC: {provider}")
            
        return topology_initializer

    async def deploy_patch(self, patch_metadata: Dict[str, Any]) -> bool:
        """Inyecta y ejecuta la configuración en caliente vía Automation API.

        Args:
            patch_metadata (Dict[str, Any]): Parámetros del parche IaC.

        Returns:
            bool: True si el despliegue converge con éxito; False si falla.
        """
        try:
            program = self._get_inline_program()
            
            logger.info(f"Conectando programáticamente con el Stack: {self.stack_name}")
            stack = auto.create_or_select_stack(
                stack_name=self.stack_name,
                project_name=self.settings.project_name,
                program=program
            )
            
            logger.debug("Inyectando secretos de región y metadatos del parche")
            stack.set_config("cloud:region", auto.ConfigValue(value=self.settings.cloud_region))
            stack.set_config("patch:data", auto.ConfigValue(value=str(patch_metadata)))
            
            logger.info("Iniciando comando 'Up' asíncrono en hilo executor...")
            loop = asyncio.get_running_loop()
            
            await loop.run_in_executor(None, lambda: stack.up(on_output=print))
            
            logger.success(
                f"Despliegue convergente completado con éxito en "
                f"{self.final_provider.upper()}."
            )
            return True
            
        except Exception as e:
            logger.critical(f"Fallo crítico durante la mutación de infraestructura: {str(e)}")
            return False
