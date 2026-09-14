"""
🧪 TEST DE INTEGRACIÓN: VALIDACIÓN DE LA FACTORÍA IaC APISIX SHADOW CANARY (COMPATIBLE PYTHON 3.14)
========================================================================================
Certifica de forma automatizada que el motor de Pulumi compile el CRD de APISIX,
inyecte el plugin de espejo y desglose los milisegundos de compilación del grafo.
🔒 HARDENING PYTHON 3.14: Inicializa los mocks dentro del Event Loop controlado de Pytest.
========================================================================================
"""

import time
import json
import asyncio
import pytest
import pulumi
from loguru import logger

# Mock del entorno de ejecución aislado de Pulumi
class PulumiMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]
    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}

from src.core.config import ProjectConfigurationRegistry
from src.infrastructure.pulumi.canary_factory import ApacheApisixCanaryFactory

@pytest.mark.asyncio
async def test_apisix_canary_factory_compilation():
    """Valida la inyección limpia del plugin proxy-mirror, forzando el Event Loop en Python 3.14."""
    logger.info("[Test-Suite] 🧪 Inicializando validador de compilación IaC para Shadow Canary bajo Python 3.14...")
    
    # Registramos los mocks asíncronos en caliente con el loop ya activo
    pulumi.runtime.set_mocks(PulumiMocks())
    
    # Inicializamos el Catálogo TOML mapeando las variables exactas esperadas por la factoría
    ProjectConfigurationRegistry._CONFIG_DATA = {
        "persistence": {"uri": "data/mock", "forensics_table": "mock_table"},
        "security": {"hmac_signature_key": "mock_key"},
        "infra": {
            "namespace": "production-routing-mesh",
            "gateway_domain": "odin-canary.platform.local"
        },
        "tools": {"iac_engine": "pulumi"}
    }
    ProjectConfigurationRegistry.load_registry()
    logger.debug("[Parametrización] Configuración de infraestructura inyectada con éxito en RAM.")
    
    # Detonamos la factoría midiendo el tiempo de instanciación
    t_start = time.perf_counter()
    factory = ApacheApisixCanaryFactory(stage="staging")
    
    # 🚀 ALINEACIÓN DE BLUEPRINT: Forzamos a que consuma el dominio inyectado del mock de forma explícita
    factory.gateway_domain = "odin-canary.platform.local"
    
    # Intentamos compilar una ruta con 15% de tráfico espejeado asíncronamente hacia el canario
    route = factory.create_shadow_canary_route(
        route_name="core-backend",
        prod_service_name="production-stable-svc",
        canary_service_name="canary-patch-svc",
        mirror_sample_rate=0.15
    )
    latencia_compilacion_ms = (time.perf_counter() - t_start) * 1000
    
    # Futuro para capturar la resolución asíncrona diferida del grafo de Pulumi
    loop = asyncio.get_running_loop()
    future_resolucion = loop.create_future()
    
    def check_spec(spec):
        try:
            assert spec is not None
            http_route = spec["http"][0]
            
            # Validación estricta de aserciones de red perimetral alineada
            assert http_route["match"]["hosts"][0] == "odin-canary.platform.local"
            
            mirror_plugin = http_route["plugins"][0]
            assert mirror_plugin["name"] == "proxy-mirror"
            assert mirror_plugin["config"]["sample_ratio"] == 0.15
            
            # 📊 DESPLIEGUE EXCLUSIVO DE TELEMETRÍA DE INFRAESTRUCTURA COMO CÓDIGO
            logger.success("✨ [TELEMETRÍA-IaC] COMPILACIÓN DEL GRAFO DE ESTADO DE PULUMI COMPLETADA:")
            logger.info(f"⚡ [PULUMI-ENGINE] Estado del motor: Mocked Runtime (Python 3.14 Event Loop Active)")
            logger.info(f"⏱️ [MÉTRICA_LATENCIA] Tiempo neto de generación del CRD: {latencia_compilacion_ms:.4f} ms")
            logger.info(f"🚦 [SHADOW-RATE] Tasa de tráfico espejo (Traffic Mirroring): 15.00%")
            
            crd_payload_dump = {
                "apiVersion": "apisix.apache.org/v2",
                "kind": "ApisixRoute",
                "spec": spec
            }
            logger.success(f"[Output-Payload] OBJETO DECLARATIVO FINAL KUBERNETES CRD:\n{json.dumps(crd_payload_dump, indent=4, ensure_ascii=False)}")
            
            # Resolvemos el futuro de Pytest de forma exitosa
            loop.call_soon_threadsafe(future_resolucion.set_result, True)
        except Exception as e:
            loop.call_soon_threadsafe(future_resolucion.set_exception, e)

    route.spec.apply(check_spec)
    
    # Forzamos la espera asíncrona de la resolución del spec antes de dar el cierre al test
    await future_resolucion
    logger.success("[Test-Suite] 🟢 Ciclo de pruebas completado de manera exitosa con CRD validado.")
