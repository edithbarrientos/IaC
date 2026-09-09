"""API Endpoint para capturar interacciones de Slack y despertar a LangGraph."""

import json
from fastapi import FastAPI, Form, Response
from langgraph.types import Command
from loguru import logger

# 🚨 AJUSTE EN LA IMPORTACIÓN: Traemos la fábrica y la clase, no una variable global 'app' inexistente
from src.infrastructure.ai.supervisor import compile_supervisor_workflow, AsyncAgentSupervisor

api = FastAPI()

@api.post("/v1/integrations/slack/actions")
async def handle_slack_interactive_buttons(payload: str = Form(...)):
    """Receptor global de interacciones de botones de Slack.
    
    Parsea la carga, extrae el thread_id inyectado originalmente en el botón 
    y envía la señal de continuación o cancelación al Checkpointer de LangGraph.
    """
    # 1. Slack envía los datos codificados como un string JSON en formularios planos
    data = json.loads(payload)
    
    # 2. Extraemos la acción ejecutada por el usuario (cuál botón presionó)
    action_executed = data["actions"][0]
    action_id = action_executed["action_id"]  # "slack_approve" o "slack_deny"
    thread_id = action_executed["value"]      # Recuperamos el thread_id oculto en el botón
    user_name = data["user"]["name"]          # Quién fue el administrador que firmó el cambio
    
    logger.info(f"[Slack-Callback] Usuario @{user_name} ejecutó '{action_id}' para Thread: {thread_id}")

    # 3. Determinamos la lógica de aprobación binaria según el botón presionado
    is_approved = True if action_id == "slack_approve" else False
    
    # 4. Construimos la configuración de direccionamiento del Checkpointer
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # 5. Instanciamos un supervisor mock temporal para compilar el grafo en caliente y recuperar el hilo
        # Esto nos permite colgaros del checkpointer en memoria de manera segura
        dummy_supervisor = AsyncAgentSupervisor(workers=[], memory_repo=None, governance_engine=None)
        compiled_graph = compile_supervisor_workflow(dummy_supervisor)

        # 6. Despertamos al agente de LangGraph pasándole el resultado del interrupt
        # La ejecución continuará exactamente donde se quedó congelada en el 'interrupt()'
        await compiled_graph.ainvoke(
            Command(resume={"approved": is_approved}), 
            config=config
        )
        logger.success(f"[Grafo-Reanudado] El hilo {thread_id} continuó su curso tras la firma de @{user_name}.")
    except Exception as e:
        logger.error(f"[Callback-Error] No se pudo reanudar el grafo del hilo {thread_id}: {str(e)}")
        return Response(content="Error interno al procesar el estado de la IA.", status_code=500)

    # 7. Reemplazamos el mensaje en Slack para que los botones desaparezcan de la interfaz
    status_text = "🟢 *Acción Aprobada*" if is_approved else "🔴 *Acción Denegada*"
    updated_slack_ui = {
        "text": f"Resolución de Gobernanza: {status_text} por @{user_name}."
    }
    
    return Response(
        content=json.dumps(updated_slack_ui), 
        media_type="application/json", 
        status_code=200
    )
