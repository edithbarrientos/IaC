"""Infraestructura de Simulación de Red y Memoria Vectorial - Parte 1.

Este bloque define el comportamiento simulado (Mock) del repositorio vectorial
de largo plazo y los entornos controlados de red asíncrona para pruebas de carga.
"""

import asyncio
from typing import List
import pytest_asyncio
import httpx
from loguru import logger

# Importación de entidades de tu dominio base
from src.core.entities import AuditLogEntry
from src.core.interfaces import VectorMemoryRepository
from src.infrastructure.ai.supervisor import NotificationAdapter, ClientNotificationConfig

# =========================================================================
# --- DOBLE DE PRUEBA: MEMORIA VECTORIAL INMUTABLE ---
# =========================================================================

class MockVectorMemoryRepository(VectorMemoryRepository):
    """Implementación de pruebas para aislar la base de datos vectorial de producción.
    
    Simula la persistencia asíncrona de embeddings y bitácoras forenses de incidentes.
    """

    def __init__(self) -> None:
        self.storage: List[AuditLogEntry] = []

    async def save_audit_trail(self, audit_entry: AuditLogEntry) -> None:
        """Simula la inserción de un vector y sus metadatos en la base de datos vectorial."""
        await asyncio.sleep(0.005)
        self.storage.append(audit_entry)
        logger.success(f"[Mock-Vector-DB] Registro indexado semánticamente. ID: {audit_entry.audit_entry_id}")


# =========================================================================
# --- SIMULADOR DE API EXTERNA ---
# =========================================================================

class StableServerSimulator:
    """Emulador de API transaccional de alta disponibilidad con Pooling de sockets."""
    async def handle_request(self, request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(0.01)  # Simulación de latencia base
        return httpx.Response(200, json={"status": "dispatched"})


@pytest_asyncio.fixture(scope="function")
async def setup_test_infrastructure():
    """Aprovisiona el entorno telemétrico, el pool HTTPX y el repositorio vectorial."""
    logger.configure(handlers=[{
        "sink": lambda msg: print(msg, end=""),
        "serialize": True,
        "level": "INFO"
    }])
    
    vector_repo = MockVectorMemoryRepository()
    server = StableServerSimulator()
    
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(server.handle_request),
        limits=httpx.Limits(max_connections=200, max_keepalive_connections=50)
    ) as client:
        yield vector_repo, client
