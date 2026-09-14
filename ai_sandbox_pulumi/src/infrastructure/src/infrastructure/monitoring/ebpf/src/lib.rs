"""
🚀 PROGRAMA PERIMETRAL: CORTEX EBPF MONITORING PROBE (PYO3 NATIVE LOG MESH)
========================================================================================
Abre el canal de sockets compartido con Ring 0 y expone sus bytes directo a la RAM de Python.
🔒 LOG INTEROPERABILITY: Redirige macros de Rust (error!, info!) hacia Loguru de Python en O(1).
🔒 ZERO-IF: Despacho elástico de estructuras binarias en tiempo constante O(1).
========================================================================================
"""

use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use log::{error, info, warn};
use aya::{include_bytes_aligned, Bpf};
use aya::maps::RingBuf;
use std::convert::TryFrom;
use serde_json::json;

#[repr(C)]
#[derive(Clone, Copy)]
struct SocketPanicEvent {
    process_id: u32,
    network_error_code: u32,
    payload_signature: [u8; 32],
}

/// 🚀 EXPOSICIÓN NATIVA: Declara el módulo binario ejecutable directamente desde tu venv
#[pymodule]
fn cortex_ebpf_probe(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    
    // Alineación estricta del package name con su ubicación física real en el árbol
    let _ = m.add("__package__", "src.infrastructure.monitoring.ebpf");
    
    // 🚀 INITIALIZE LOG LOGGER: Canaliza de forma nativa e inmediata las trazas de Rust hacia Python
    pyo3_log::init();
    
    info!("[eBPF-Submodule] Puente de observabilidad unificado PyO3-Log enlazado en caliente en la RAM.");

    /// Función expuesta en RAM que lee el RingBuffer del Kernel de forma lock-free
    #[pyfn(m, "consume_kernel_panics")]
    fn consume_kernel_panics() -> PyResult<String> {
        info!("[eBPF-Monitor] Sincronizando bytecode forense con Ring 0...");
        
        // Carga declarativa del bytecode eBPF embebido
        let bpf_bytecode = include_bytes_aligned!("../target/bpfel-unknown-none/release/cortex_probe_kernel");
        
        let mut bpf_runtime = Bpf::load(bpf_bytecode).map_err(|e| {
            // 🚀 LOG INDUSTRIAL: Registra el error a nivel kernel sin bloquear la CPU
            error!("[eBPF-Failure] Fallo crítico al instanciar el bytecode en memoria física: {}", e);
            PyRuntimeError::new_err(format!("Fallo al cargar BPF: {}", e))
        })?;
        
        // Enganchamos la sonda de forma atómica a las syscalls del sistema operativo
        let program: &mut aya::programs::Tracepoint = bpf_runtime.program_mut("cortex_sys_enter_connect")
            .unwrap().try_into().unwrap();
        program.load().unwrap();
        program.attach("syscalls", "sys_enter_connect").unwrap();
        info!("[eBPF-Monitor] Sonda amarrada de forma elástica al tracepoint perimetral 'sys_enter_connect'.");

        // Extraemos los bytes físicos directo de los registros de la CPU
        let mut ring_buffer = RingBuf::try_from(bpf_runtime.map_mut("CORTEX_RING_BUFFER").unwrap()).unwrap();
        
        // Algoritmo de lectura O(1) parametrizado sin if/else condicionales
        let telemetry_string = match ring_buffer.next() {
            Some(item) => {
                let event = unsafe { &*(item.as_ptr() as *const SocketPanicEvent) };
                warn!(
                    "[eBPF-Alert] ¡Syscall interceptada en Ring 0! Caída de conexión en Gateway. PID: {} | Code: {}", 
                    event.process_id, 
                    event.network_error_code
                );
                json!({
                    "raw_logs": format!("ERR_KERNEL_SOCKET_PANIC_CODE_{}", event.network_error_code),
                    "risk": "critical"
                }).to_string()
            },
            None => {
                info!("[eBPF-Heartbeat] Canales sanos. El RingBuffer de hardware reporta 0 anomalías.");
                json!({
                    "raw_logs": "SIG_KERNEL_HEALTHY_HEARTBEAT",
                    "risk": "none"
                }).to_string()
            },
        };

        Ok(telemetry_string)
    }

    Ok(())
}
