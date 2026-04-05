import gradio as gr
import sys
import os
from dotenv import load_dotenv, find_dotenv

# Cargar variables de entorno desde el .env sin importar dónde esté ubicado
load_dotenv(find_dotenv())

# Ajustar path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from corotos_app.rag.chain import chat_rag_lineal

def responder_al_chatbot(mensaje_usuario, historial):
    try:
        # Aquí el RAG lineal gasta exactamente 1 LLM call y se encarga del scraping en código duro.
        respuesta = chat_rag_lineal(mensaje_usuario, historial)
        return respuesta
    except Exception as e:
        return f"Ups, error del sistema: {str(e)}\n\n¿Tienes tu OPENAI_API_KEY configurada?"

def lanzar_ui():
    print("=" * 60)
    print(" 🤖 INICIANDO AGENTE VIRTUAL LINEAL DE COROTOS (Bajo Costo)")
    print("=" * 60)
    
    with gr.Blocks(title="Asesor Inmobiliario Dominicano") as demo:
        gr.Markdown("# 🇩🇴 Tu Asesor Inmobiliario Dominicano")
        gr.Markdown(
            "¡Saludos! Escribe qué andas buscando (ej: *Busco un apartamento.*). \n"
            "Buscaré en mi base de datos interna y sino, investigaré Corotos en tiempo real por ti extrayendo y respondiendo al instante."
        )
        
        chatbot = gr.Chatbot(height=500, label="Cerebro IA (RAG Directo)")
        msg = gr.Textbox(label="Mensaje", placeholder="Escribe aquí tu búsqueda...")
        clear = gr.ClearButton([msg, chatbot])

        def handle_user_input(user_message, history):
            history.append({"role": "user", "content": user_message})
            respuesta_ia = responder_al_chatbot(user_message, history[:-1])
            history.append({"role": "assistant", "content": respuesta_ia})
            return "", history

        msg.submit(handle_user_input, [msg, chatbot], [msg, chatbot])
        
    demo.launch(server_port=7860, show_error=True)

if __name__ == "__main__":
    lanzar_ui()
