/*
🚀 PROGRAMA PERIMETRAL: CORTEX EBPF MONITORING PROBE (PYO3 NATIVE LOG MESH)
========================================================================================
Abre el canal de sockets compartido con Ring 0 y expone sus bytes directo a la RAM de Python.
🔒 FEATURE ISOLATION HARDENING: Mock-Bridge inmune a fallas de libc en entornos macOS (Darwin).
🔒 PYO3 MODERN SYNTAX: Erradica el uso de pyfn obsoleto migrando a #[pyfunction] nativo.
🔒 ZERO-WARNINGS: Inyecta directivas allow(dead_code) para silenciar el descarte del compilador.
========================================================================================
*/

use pyo3::prelude::*;
use log::{info, warn};
use serde_json::json;

// 🚀 REPARACIÓN DE WARNING: Silencia el aviso en macOS permitiendo la definición inactiva en Ring 3
#[allow(dead_code)]
#[repr(C)]
#[derive(Clone, Copy)]
struct SocketPanicEvent {
    process_id: u32,
    network_error_code: u32,
    payload_signature: [u8; 32],
}

// =================================================================================
// 🐧 IMPLEMENTACIÓN EN PRODUCCIÓN (LINUX-EBPF ACTIVO)
// =================================================================================
#[cfg(feature = "linux-ebpf")]
#[pyfunction]
fn consume_kernel_panics() -> PyResult<String> {
    use ::aya::{include_bytes_aligned, Bpf};
    use ::aya::maps::RingBuf;
    use std::convert::TryFrom;
    use pyo3::exceptions::PyRuntimeError;
    use log::error;

    info!("[eBPF-Monitor-Linux] Sincronizando bytecode forense con Ring 0...");
    let bpf_bytecode = include_bytes_aligned!("../target/bpfel-unknown-none/release/cortex_probe_kernel");
    
    let mut bpf_runtime = Bpf::load(bpf_bytecode).map_err(|e| {
        error!("[eBPF-Failure] Fallo crítico al instanciar el bytecode en memoria física: {}", e);
        PyRuntimeError::new_err(format!("Fallo al cargar BPF: {}", e))
    })?;
    
    let program: &mut ::aya::programs::Tracepoint = bpf_runtime.program_mut("cortex_sys_enter_connect")
        .unwrap().try_into().unwrap();
    program.load().unwrap();
    program.attach("syscalls", "sys_enter_connect").unwrap();
    info!("[eBPF-Monitor] Sonda amarrada de forma elástica al tracepoint 'sys_enter_connect'.");

    let mut ring_buffer = RingBuf::try_from(bpf_runtime.map_mut("CORTEX_RING_BUFFER").unwrap()).unwrap();
    
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

// =================================================================================
// 🍏 MOCK BRIDGE PARA ENTORNO DE DESARROLLO (MAC/WINDOWS SINTAXIS MODERNA)
// =================================================================================
#[cfg(not(feature = "linux-ebpf"))]
#[pyfunction]
fn consume_kernel_panics() -> PyResult<String> {
    warn!("[eBPF-Mock-Darwin] Sonda ejecutándose en macOS (Aislamiento de Kernel Activo vía Features).");
    info!("[eBPF-Heartbeat] Simulando canal elástico de RingBuffer compartido en RAM...");
    
    let telemetry_string = json!({
        "raw_logs": "SIG_ERR_TLS_GWMISMATCH_P01",
        "risk": "crit"
    }).to_string();
    
    Ok(telemetry_string)
}

/// 🚀 EXPOSICIÓN NATIVA MODERNA: Registra la función en el módulo con wrap_pyfunction
#[pymodule]
fn cortex_ebpf_probe(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    let _ = m.add("__package__", "src.infrastructure.monitoring.ebpf");
    
    let _ = pyo3_log::try_init();
    
    info!("[eBPF-Submodule] Puente de observabilidad unificado PyO3-Log enlazado en la RAM.");

    m.add_function(wrap_pyfunction!(consume_kernel_panics, m)?)?;
    
    Ok(())
}
