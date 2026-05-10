import gradio as gr
import logging
from agent import agent_executor

logging.basicConfig(
    filename='agent_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s',
    datefmt='%H:%M:%S',
    force=True
)
logger = logging.getLogger('app')

def chat(message, history):
    logger.info(f"[APP] ===== NUEVA PETICIÓN =====")
    logger.info(f"[APP] Mensaje del usuario: '{message}'")
    
    result = agent_executor.invoke({"messages": [("user", message)]})
    
    # Log de TODOS los mensajes del agente
    logger.info(f"[APP] Total mensajes en resultado: {len(result['messages'])}")
    for i, msg in enumerate(result["messages"]):
        msg_type = type(msg).__name__
        content = getattr(msg, 'content', '')
        tool_calls = getattr(msg, 'tool_calls', [])
        logger.info(f"[APP] Mensaje [{i}] tipo={msg_type}")
        if content:
            logger.info(f"[APP]   content={content[:500]}")
        if tool_calls:
            for tc in tool_calls:
                logger.info(f"[APP]   tool_call: {tc.get('name', '?')} args={tc.get('args', {})}")
    
    final_response = result["messages"][-1].content
    logger.info(f"[APP] Respuesta final: {final_response[:500]}")
    logger.info(f"[APP] ===== FIN PETICIÓN =====")
    
    return final_response

gr.ChatInterface(fn=chat, title="🎮 GameMind AI").launch()