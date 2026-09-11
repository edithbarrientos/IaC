"""
⚙️ CAPA DE AUTOMATIZACIÓN DE INFRAESTRUCTURA: DATA-DRIVEN CLOUD PROVIDER FACTORY
========================================================================================
Calcula de forma dinámica y agnóstica los planos declarativos complejos de Pulumi.
Erradica condicionales duros y externaliza la configuración hacia la capa cognitiva.
========================================================================================
"""

from typing import Dict, Any, Optional
from loguru import logger

class BaseCloudAdapter:
    """Interfaz abstracta para los adaptadores de aprovisionamiento de nube."""
    
    def generate_cluster_blueprint(self, cluster_name: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calcula el plano declarativo compatible con el motor de Pulumi."""
        raise NotImplementedError


class AWSCloudAdapter(BaseCloudAdapter):
    """
    Adaptador especializado en la topología avanzada de Amazon Web Services (AWS).
    Construye dinámicamente un esquema EKS empresarial parametrizado en Runtime.
    """

    def generate_cluster_blueprint(self, cluster_name: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"[AWS-Factory] Generando arquitectura EKS Enterprise parametrizada para: '{cluster_name}'")
        
        # 1. Extracción elástica con valores por omisión corporativos (Fallback de Producción)
        params = custom_params or {}
        cidr_block = params.get("cidr_block", "10.0.0.0/16")
        az_count = params.get("az_count", 3)
        instance_type = params.get("instance_type", "m5.large")
        desired_capacity = params.get("desired_capacity", 3)
        min_size = params.get("min_size", 3)
        max_size = params.get("max_size", 10)
        allowed_cidrs = params.get("allowed_cidrs", ["192.168.1.0/24", "10.50.0.0/16"])
        
        # 2. Construcción dinámica del grafo de dependencias cruzadas de Pulumi
        return {
            "name": cluster_name,
            "runtime": "yaml",
            "description": f"Cluster AWS EKS de nivel empresarial con VPC dedicada, OIDC y KMS para {cluster_name}",
            "resources": {
                f"{cluster_name}-kms-key": {
                    "type": "aws:kms:Key",
                    "properties": {
                        "description": f"Llave KMS para cifrar secretos de Kubernetes etcd en {cluster_name}",
                        "deletionWindowInDays": 7
                    }
                },
                f"{cluster_name}-vpc": {
                    "type": "awsx:ec2:Vpc",
                    "properties": {
                        "cidrBlock": cidr_block,
                        "numberOfAvailabilityZones": az_count,
                        "subnetSpecs": [
                            {"type": "Public", "cidrMask": 24},
                            {"type": "Private", "cidrMask": 22}
                        ]
                    }
                },
                f"{cluster_name}-eks": {
                    "type": "eks:Cluster",
                    "properties": {
                        "vpcId": f"${{{cluster_name}-vpc.vpcId}}",
                        "privateSubnetIds": f"${{{cluster_name}-vpc.privateSubnetIds}}",
                        "publicSubnetIds": f"${{{cluster_name}-vpc.publicSubnetIds}}",
                        "endpointPrivateAccess": True,
                        "endpointPublicAccess": True,
                        "publicAccessCidrs": allowed_cidrs,
                        "createOidcProvider": True,
                        "encryptionProviders": [
                            {
                                "keyArn": f"${{{cluster_name}-kms-key.arn}}",
                                "resources": ["secrets"]
                            }
                        ],
                        "managedNodeGroups": [
                            {
                                "name": f"{cluster_name}-apps-pool",
                                "instanceType": instance_type,
                                "desiredCapacity": desired_capacity,
                                "minSize": min_size,
                                "maxSize": max_size,
                                "labels": {"environment": "production", "tier": "application"}
                            }
                        ],
                        "enabledClusterLogTypes": ["api", "audit", "authenticator", "controllerManager", "scheduler"]
                    }
                }
            },
            "outputs": {
                "clusterName": f"${{{cluster_name}-eks.eksCluster.name}}",
                "kubeconfig": f"${{{cluster_name}-eks.kubeconfig}}",
                "oidcProviderUrl": f"${{{cluster_name}-eks.core.oidcProvider.url}}"
            }
        }


class GCPCloudAdapter(BaseCloudAdapter):
    """Adaptador elástico de contingencia para Google Cloud Platform (GCP)."""
    def generate_cluster_blueprint(self, cluster_name: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"[GCP-Factory] Calculando topología para GKE: '{cluster_name}'")
        return {"name": cluster_name, "runtime": "yaml", "resources": {f"{cluster_name}-gke": {"type": "gcp:container/cluster:Cluster"}}}


class AzureCloudAdapter(BaseCloudAdapter):
    """Adaptador elástico de contingencia para Microsoft Azure (AKS)."""
    def generate_cluster_blueprint(self, cluster_name: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"[Azure-Factory] Calculando topología para AKS: '{cluster_name}'")
        return {"name": cluster_name, "runtime": "yaml", "resources": {f"{cluster_name}-aks": {"type": "azure-native:containerservice:ManagedCluster"}}}


class CloudProviderFactory:
    """Fábrica Maestra encargada de orquestar y despachar los planos de infraestructura sin condicionales."""

    _ADAPTER_REGISTRY: Dict[str, Any] = {
        "aws": AWSCloudAdapter,
        "gcp": GCPCloudAdapter,
        "google": GCPCloudAdapter,
        "azure": AzureCloudAdapter,
        "microsoft": AzureCloudAdapter
    }

    @classmethod
    def create_network_topology(cls, provider: str, cluster_name: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Punto de entrada universal corporativo parametrizado.
        Resuelve el adaptador y calcula la topología compleja en tiempo constante O(1).
        """
        sanitized_provider = str(provider).lower().strip()
        adapter_class = cls._ADAPTER_REGISTRY.get(sanitized_provider, AWSCloudAdapter)
        return adapter_class().generate_cluster_blueprint(cluster_name=cluster_name, custom_params=custom_params)
