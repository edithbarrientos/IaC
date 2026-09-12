"""
⚙️ CAPA DE AUTOMATIZACIÓN DE INFRAESTRUCTURA: DATA-DRIVEN CLOUD PROVIDER FACTORY
========================================================================================
Calcula de forma dinámica y agnóstica los planos declarativos complejos de Pulumi.
MÁXIMA OPTIMIZACIÓN / ZERO IFS: Despacha adaptadores polimórficos en tiempo constante O(1).
========================================================================================
"""

from typing import Dict, Any
from loguru import logger
from src.core.config import ProjectConfigurationRegistry

class BaseCloudAdapter:
    """Interfaz abstracta para los adaptadores de aprovisionamiento de nube."""
    
    @classmethod
    def generate_cluster_blueprint(cls, cluster_name: str, custom_params: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula el plano declarativo compatible con el motor de Pulumi."""
        raise NotImplementedError


class AWSCloudAdapter(BaseCloudAdapter):
    """
    Adaptador especializado en la topología avanzada de Amazon Web Services (AWS).
    Construye dinámicamente un esquema EKS empresarial parametrizado en Runtime.
    """

    @classmethod
    def generate_cluster_blueprint(cls, cluster_name: str, custom_params: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[AWS-Factory] Generando arquitectura EKS Enterprise parametrizada para: '{cluster_name}'")
        
        v = custom_params["variables"]
        blueprint = ProjectConfigurationRegistry.get_provider_blueprint("aws")
        
        # 🚀 PROTECCIÓN TOTAL EXTRA: Fallback seguro para allowed_cidrs si la mutación lo limpia
        cidrs_seguros = v.get("allowed_cidrs") or ["10.240.0.0/16"]
        
        return {
            "name": cluster_name,
            "runtime": "yaml",
            "description": f"Cluster AWS EKS de nivel empresarial con VPC dedicada, OIDC y KMS para {cluster_name}",
            "resources": {
                f"{cluster_name}-kms-key": {
                    "type": blueprint["kms_type"],
                    "properties": {
                        "description": f"Llave KMS para cifrar secretos de Kubernetes etcd en {cluster_name}",
                        "deletionWindowInDays": int(v.get("kms_deletion_days", 7))
                    }
                },
                f"{cluster_name}-vpc": {
                    "type": blueprint["vpc_type"],
                    "properties": {
                        "cidrBlock": v.get("cidr_block", "10.0.0.0/16"),
                        "numberOfAvailabilityZones": int(v.get("az_count", 3)),
                        "subnetSpecs": [
                            {"type": "Public", "cidrMask": int(v.get("public_subnet_mask", 24))},
                            {"type": "Private", "cidrMask": int(v.get("private_subnet_mask", 22))}
                        ]
                    }
                },
                f"{cluster_name}-eks": {
                    "type": blueprint["cluster_type"],
                    "properties": {
                        "vpcId": f"${{{cluster_name}-vpc.vpcId}}",
                        "privateSubnetIds": f"${{{cluster_name}-vpc.privateSubnetIds}}",
                        "publicSubnetIds": f"${{{cluster_name}-vpc.publicSubnetIds}}",
                        "endpointPrivateAccess": bool(v.get("endpoint_private_access", True)),
                        "endpointPublicAccess": bool(v.get("endpoint_public_access", False)),
                        blueprint["firewall_property"]: cidrs_seguros,
                        "createOidcProvider": True,
                        "encryptionProviders": [
                            {
                                "keyArn": f"${{{cluster_name}-kms-key.arn}}",
                                "resources": blueprint["secrets_encryption_resources"]
                            }
                        ],
                        blueprint["node_group_key"]: [
                            {
                                "name": "enterprise-system-pool",
                                "instanceType": v.get("system_node_instance", "m5.large"),
                                "desiredCapacity": int(v.get("system_node_desired", 3)),
                                "maxSize": int(v.get("system_node_max", 5)),
                                "labels": {"environment": "production", "tier": "system-core"}
                            },
                            {
                                "name": f"{cluster_name}-apps-pool",
                                "instanceType": v.get("apps_node_instance", "m5.large"),
                                "desiredCapacity": int(v.get("apps_node_desired", 3)),
                                "minSize": int(v.get("apps_node_min", 3)),
                                "maxSize": int(v.get("apps_node_max", 10)),
                                "labels": {"environment": "production", "tier": "application"}
                            }
                        ],
                        "enabledClusterLogTypes": v.get("enabled_cluster_log_types", ["api", "audit"])
                    }
                }
            },
            "outputs": {
                "clusterName": f"${{{cluster_name}-eks.eksCluster.name}}",
                "kubeconfig": f"${{{cluster_name}-eks.kubeconfig}}"
            }
        }


class GCPCloudAdapter(BaseCloudAdapter):
    """Adaptador elástico de contingencia para Google Cloud Platform (GCP)."""
    
    @classmethod
    def generate_cluster_blueprint(cls, cluster_name: str, custom_params: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[GCP-Factory] Calculando topología para GKE: '{cluster_name}'")
        v = custom_params["variables"]
        blueprint = ProjectConfigurationRegistry.get_provider_blueprint("gcp")
        
        return {
            "name": cluster_name,
            "runtime": "yaml",
            "resources": {
                f"{cluster_name}-gke": {
                    "type": blueprint["cluster_type"],
                    "properties": {
                        "network": v.get("network_ip_range"),
                        "initialNodeCount": int(v.get("apps_min_nodes", 3)),
                        "nodeConfig": {"machineType": v.get("apps_machine_type")}
                    }
                }
            }
        }


class AzureCloudAdapter(BaseCloudAdapter):
    """Adaptador elástico de contingencia para Microsoft Azure (AKS)."""
    
    @classmethod
    def generate_cluster_blueprint(cls, cluster_name: str, custom_params: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[Azure-Factory] Calculando topología para AKS: '{cluster_name}'")
        v = custom_params["variables"]
        blueprint = ProjectConfigurationRegistry.get_provider_blueprint("azure")
        
        return {
            "name": cluster_name,
            "runtime": "yaml",
            "resources": {
                f"{cluster_name}-aks": {
                    "type": blueprint["cluster_type"],
                    "properties": {
                        "resourceGroupName": v.get("resource_group_name"),
                        "dnsPrefix": f"{cluster_name}-dns",
                        blueprint["node_group_key"]: [
                            {
                                "name": "agentpool",
                                "vmSize": v.get("apps_vm_size"),
                                "count": int(v.get("apps_min_nodes", 5))
                            }
                        ]
                    }
                }
            }
        }


class CloudProviderFactory:
    """Fábrica Maestra encargada de orquestar y despachar los planos de infraestructura sin condicionales."""

    _ADAPTER_REGISTRY: Dict[str, type[BaseCloudAdapter]] = {
        "aws": AWSCloudAdapter,
        "gcp": GCPCloudAdapter,
        "google": GCPCloudAdapter,
        "azure": AzureCloudAdapter,
        "microsoft": AzureCloudAdapter
    }

    @classmethod
    def create_network_topology(cls, provider: str, cluster_name: str, custom_params: Dict[str, Any]) -> Dict[str, Any]:
        """Punto de entrada universal corporativo parametrizado en O(1)."""
        sanitized_provider = str(provider).lower().strip()
        adapter_class = cls._ADAPTER_REGISTRY.get(sanitized_provider, AWSCloudAdapter)
        return adapter_class.generate_cluster_blueprint(cluster_name=cluster_name, custom_params=custom_params)
