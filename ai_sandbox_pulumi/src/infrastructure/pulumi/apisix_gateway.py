"""Planta de Infraestructura como Código (IaC) - Orquestación de Apache APISIX.

Este módulo utiliza Pulumi para desplegar el API Gateway empresarial Apache APISIX
dentro de un clúster de Kubernetes, abstrayendo credenciales y configuraciones
mediante inyección dinámica de parámetros por entorno.
"""

import pulumi
import pulumi_kubernetes as k8s

# =========================================================================
# --- CAPA DE CONFIGURACIÓN Y PARAMETRIZACIÓN DINÁMICA ---
# =========================================================================

# Inicializamos el gestor de configuración del stack de Pulumi
config = pulumi.Config()

# Parámetros Globales de Infraestructura (Con fallback seguro para desarrollo)
environment = config.get("environment") or "sandbox"
apisix_version = config.get("apisix_chart_version") or "2.4.0"
etcd_replicas = config.get_int("etcd_replica_count") or 1
service_type = config.get("service_type") or "LoadBalancer"

# 🔒 CONTROL DE SECRETOS: Obtenemos el token de forma encriptada
# Si no existe en el archivo de configuración del stack, levantamos una excepción defensiva
apisix_admin_token = config.require_secret("apisix_admin_token")

pulumi.log.info(f"🚀 [Pulumi-IaC] Iniciando orquestación de red. Entorno: {environment.upper()}")

# =========================================================================
# --- CREACIÓN DEL NAMESPACE AISLADO (CONTROL PLANE) ---
# =========================================================================

gateway_namespace = k8s.core.v1.Namespace(
    "aiops-gateway-namespace",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name=f"aiops-control-plane-{environment}",
        labels={
            "architecture": "clean-architecture", 
            "tier": "gateway",
            "environment": environment
        }
    )
)

# =========================================================================
# --- DESPLIEGUE CONFIGURABLE DE APACHE APISIX (HELM CHART) ---
# =========================================================================

apisix_release = k8s.helm.v3.Release(
    "apache-apisix-gateway",
    k8s.helm.v3.ReleaseArgs(
        namespace=gateway_namespace.metadata.name,
        chart="apisix",
        repository_opts=k8s.helm.v3.RepositoryOptsArgs(
            repo="https://apiseven.com"
        ),
        version=apisix_version,
        values={
            "gateway": {
                "type": service_type,
                "externalTrafficPolicy": "Local"
            },
            "admin": {
                "allow": {
                    "ip": ["0.0.0.0/0"] # Restringible dinámicamente mediante CIDRs de red
                },
                # Mapeamos el secreto en RAM para que Helm lo inyecte sin exponerlo en los logs
                "credentials": {
                    "admin": apisix_admin_token
                }
            },
            "etcd": {
                "replicaCount": etcd_replicas
            }
        }
    ),
    pulumi.ResourceOptions(depends_on=[gateway_namespace])
)

# =========================================================================
# --- EXPORTACIÓN DE TELEMETRÍA (OUTPUTS) ---
# =========================================================================

gateway_service = k8s.core.v1.Service.get(
    "apisix-gateway-public-service",
    pulumi.Output.concat(gateway_namespace.metadata.name, "/apache-apisix-gateway"),
    pulumi.ResourceOptions(depends_on=[apisix_release])
)

# Exportamos las variables de salida para que puedan ser consumidas por otros hilos de la infraestructura
pulumi.export("gateway_namespace", gateway_namespace.metadata.name)
pulumi.export("apisix_admin_token", apisix_admin_token)
pulumi.export("gateway_public_dns", gateway_service.status.load_balancer.ingress.hostname)
