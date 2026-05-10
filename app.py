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
    logger.info(f"[APP] User: '{message}'")

    result = agent_executor.invoke({
        "messages": [("user", message)]
    })

    # logs útiles pero más limpios
    final_response = result["messages"][-1].content

    logger.info(f"[APP] Response: {final_response[:500]}")
    logger.info(f"[APP] ===== END REQUEST =====")

    return final_response


#  Ejemplos para que el usuario pruebe rápido
examples = [
    "Tell me about Hollow Knight",
    "Games similar to Age of Empires",
    "Recommend me Open World games",
    "What is Stardew Valley about?"
]


# UI
theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="purple",
    neutral_hue="slate",
    radius_size="lg",
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"]
)

css = """
#title {
    text-align: center;
    font-size: 28px;
    font-weight: bold;
}

#subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 20px;
}

footer {
    display: none !important;
}
"""


with gr.Blocks(theme=theme, css=css) as demo:

    gr.Markdown("# 🎮 GameMind AI", elem_id="title")

    gr.Markdown(
        "### AI-powered video game assistant using Steam API + RAG + semantic search",
        elem_id="subtitle"
    )

    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.ChatInterface(
                fn=chat,
                examples=examples,
                title="",
            )

        with gr.Column(scale=1):
            gr.Markdown("## 🧠 What this does")
            gr.Markdown("""
- Steam game search (API)
- Game recommendation system (tags + ranking)
- Semantic similarity (RAG on player reviews)

## ⚙️ Architecture
Agent-based system using tools:
- Steam API
- SteamSpy API
- ChromaDB (RAG)

## ⚠️ Note
If APIs fail, the system gracefully falls back to RAG or error messages.
            """)


demo.launch()
