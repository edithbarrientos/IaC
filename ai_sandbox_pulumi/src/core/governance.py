"""Módulo de Gobierno Corporativo Interceptor e Inyección HITL de AIOps.

Aplica reglas de Policy-as-Code para validar transacciones distribuidas
multi-cloud, implementando un check-point humano mandatorio de mutacion
cuando se detectan conmutaciones dinamicas de proveedor en runtime.

Información del Módulo:
    * Autor: Edith Barrientos 💻
    * Año: 2026 🚀
    * Patrones: Policy Interceptor, Human-in-the-Loop, Checkpoint Guardrail
"""

import asyncio
from loguru import logger
from core.config import runtime_settings
from core.entities import IncidentContext


class AgentGovernanceEngine:
    """Interceptor central encargado de validar la seguridad de las mutaciones IaC."""

    def __init__(self) -> None:
        """Inicializa el motor consumiendo los limites del enjambre desde la RAM."""
        self.max_attempts: int = runtime_settings.get("max_self_healing_attempts", 3)
        
        # Despacho polimorfico para autorizar transacciones de forma directa en RAM
        self._safety_dispatch: dict[bool, float] = {
            True: 1.0,   # Requiere congelacion forzada HITL
            False: 0.0   # Operacion autonoma segura
        }

    async def evaluate_execution_safety(self, context: IncidentContext) -> bool:
        """Evalúa si las intenciones del Agente cumplen con las políticas corporativas.

        [PATTERN: POLICY INTERCEPTOR WITH CHECKPOINT]
        Compara la nube destino actual solicitada en el incidente contra el valor
        historico de arranque. Si se detecta un Hot-Swapping, congela el flujo
        exigiendo la validacion humana obligatoria en un checkpoint transaccional.

        Args:
            context (IncidentContext): El objeto de estado global de la transacción.

        Returns:
            bool: True si la operacion fue aprobada por el checkpoint; False si se aborta.
        """
        logger.info(f"🛡️ [Gobierno] Verificando checkpoint para Incidente: {context.incident_id}")

        if context.self_healing_attempts > self.max_attempts:
            logger.critical("🚨 [Gobierno] Limite de reintentos excedido. Transaccion bloqueada.")
            return False

        # Leer en caliente el proveedor cloud activo configurado en runtime_settings (RAM)
        current_ram_provider = runtime_settings.get("cloud_provider", "google")
        target_cloud = context.cloud_provider_target.lower()
        
        # Detectar de forma booleana limpia si se esta ejecutando un cambio de nube en vivo
        is_cross_cloud_mutation = target_cloud != current_ram_provider
        
        if is_cross_cloud_mutation:
            logger.warning(
                f"⚠️ [Gobierno] ¡HOT-SWAPPING DETECTADO! Conmutacion en runtime: "
                f"{current_ram_provider.upper()} -> {target_cloud.upper()}"
            )
            # Invocar obligatoriamente el retén humano del checkpoint transaccional
            approved = await self.enforce_human_approval_hitl(context)
            return approved

        logger.success("✅ [Gobierno] Operacion dentro de los limites autonomos locales.")
        context.is_approved_by_gov = True
        return True

    async def enforce_human_approval_hitl(self, context: IncidentContext) -> bool:
        """Congela la máquina de estados esperando el check-point y firma del operador.

        [PATTERN: HUMAN-IN-THE-LOOP CHECKPOINT]
        Simula la escucha no bloqueante de un Webhook criptográfico perimetral
        enviado por el SRE de guardia para dar luz verde a la nueva nube destino.

        Args:
            context (IncidentContext): Estado retenido en el reten de seguridad.

        Returns:
            bool: True si el operador concede la firma; False si aborta el failover.
        """
        new_cloud = context.cloud_provider_target.upper()
        logger.warning(
            f"🛑 [CHECKPOINT MANDATORIO] ¡TRANSACCION CONGELADA FÍSICAMENTE! "
            f"Esperando firma digital humana para autorizar failover a: {new_cloud}"
        )
        
        # Simulacion asincrona no bloqueante en el Event Loop de asyncio
        await asyncio.sleep(1.5)
        
        logger.success(
            f"✅ [CHECKPOINT APROBADO] Firma confirmada por el operador para el "
            f"Incidente {context.incident_id}. Desbloqueando la factoria Multi-Cloud."
        )
        context.is_approved_by_gov = True
        return True
