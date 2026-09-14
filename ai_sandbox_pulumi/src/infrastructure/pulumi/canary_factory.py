"""
⚡ FACTORÍA IAC: SHADOW CANARY ROUTING ENGINE (APACHE APISIX + PULUMI)
========================================================================================
Orquesta la creación de rutas dinámicas y duplicación de tráfico (Traffic Mirroring).
Mapea el tráfico perimetral duplicando un porcentaje hacia la subred del canario.
CERO HARDCODE: Consume los blueprints y settings del ProjectConfigurationRegistry.
========================================================================================
"""

from typing import Optional, Dict, Any
import pulumi
from pulumi_kubernetes.apiextensions import CustomResource
from src.core.config import ProjectConfigurationRegistry

class ApacheApisixCanaryFactory:
    def __init__(self, stage: str = "production") -> None:
        """Inicializa la factoría extrayendo los defaults paramétricos del TOML."""
        self.stage = stage
        self.infra_settings = ProjectConfigurationRegistry.get_infra_defaults()
        self.iac_settings = ProjectConfigurationRegistry.get_tools_settings()
        
        # Resolución paramétrica (Cero Hardcode)
        self.namespace = self.infra_settings.get("namespace", "ai-ops-routing")
        self.gateway_domain = self.infra_settings.get("gateway_domain", "ai-ops.platform.local")

    def create_shadow_canary_route(
        self, 
        route_name: str, 
        prod_service_name: str, 
        canary_service_name: str, 
        mirror_sample_rate: float = 0.10
    ) -> CustomResource:
        """
        Generates an ApisixRoute Custom Resource with an embedded proxy-mirror plugin.
        Mirrors a designated percentage (sample rate) of production traffic to the canary pod.
        """
        if not (0.0 <= mirror_sample_rate <= 1.0):
            raise ValueError(f"El ratio de espejo (mirror_sample_rate) debe estar entre 0.0 y 1.0. Recibido: {mirror_sample_rate}")

        # Nombre único del recurso para el grafo de estado de Pulumi
        resource_id = f"apisix-shadow-canary-{route_name}-{self.stage}"
        
        # Estructuración declarativa del CRD oficial de Apache APISIX v2 (ApisixRoute)
        canary_route = CustomResource(
            resource_id,
            api_version="apisix.apache.org/v2",
            kind="ApisixRoute",
            metadata={
                "name": f"shadow-canary-{route_name}",
                "namespace": self.namespace,
                "labels": {
                    "platform.infrastructure/layer": "perimeter-gateway",
                    "ai-ops.saga/managed-by": "AsyncAgentSupervisor"
                }
            },
            spec={
                "http": [
                    {
                        "name": f"route-{route_name}-mirroring",
                        "match": {
                            "paths": [f"/api/v1/workload/{route_name}*"],
                            "hosts": [self.gateway_domain],
                            "methods": ["GET", "POST", "PUT", "PATCH"]
                        },
                        # Backend principal de producción (Caja Gris Agnóstica)
                        "backends": [
                            {
                                "serviceName": prod_service_name,
                                "servicePort": 8000,
                                "weight": 100
                            }
                        ],
                        # 🔒 BLINDAJE EN ESPEJO: Inyección dinámica del plugin proxy-mirror
                        "plugins": [
                            {
                                "name": "proxy-mirror",
                                "enable": True,
                                "config": {
                                    "host": f"http://{canary_service_name}.{self.namespace}.svc.cluster.local:8000",
                                    "sample_ratio": mirror_sample_rate
                                }
                            }
                        ]
                    }
                ]
            }
        )
        
        # Exportamos el ID y metadatos de la ruta para que la SAGA los monitoree en RAM
        pulumi.export(f"canary_route_name_{route_name}", canary_route.metadata["name"])
        pulumi.export(f"canary_mirror_ratio_{route_name}", mirror_sample_rate)
        
        return canary_route
