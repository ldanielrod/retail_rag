from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from .db import CorotosDB
from ..core.config import FILTROS_DEFAULT
from ..scraper.pipeline import ejecutar_scraper

db = CorotosDB()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# El prompt se enviara a OpenAI solo 1 vez al final
system_prompt = """
Eres un Asesor Inmobiliario Dominicano.
A continuación te proporciono un contexto con apartamentos disponibles encontrados en nuestra base de datos que coinciden con lo que pide el usuario.
Contexto:
{contexto}

INSTRUCCIONES CLARAS:
1. Responde a la solicitud del usuario usando la información del contexto. 
2. Si el contexto está vacío, dile formalmente que no tenemos opciones exactas en este instante.
3. Usa un tono dominicano sutil (amigable, respetuoso "Saludos", "Excelente opción").
4. Presenta la información en un formato Markdown bonito (viñetas). No inventes detalles que no estén en el contexto.
"""

def chat_rag_lineal(mensaje_usuario: str, historial: list = None) -> str:
    """Implementa el RAG puro: Busca -> Extrae (Opcional) -> Pide 1 vez respuesta a GPT"""
    if historial is None:
        historial = []

    # 1. Buscar directamente en ChromaDB
    resultados = db.buscar_similares(mensaje_usuario, top_k=6)
    
    # 2. Si no hay, o hay muy pocos, raspar Internet para traer data FRESCA
    if len(resultados) < 2:
        print("🤖 [RAG Engine]: Pocos resultados en Chroma. Lanzando scraper silencioso 1 pág...")
        datos_scrappeados = ejecutar_scraper(FILTROS_DEFAULT)
        # Meter a la DB si trajo algo
        if datos_scrappeados:
            db.inyectar_apartamentos(datos_scrappeados)
            # Volver a buscar ahora que la BD está nutrida
            resultados = db.buscar_similares(mensaje_usuario, top_k=6)

    # 3. Empaquetar el contexto devuelto
    txt_contexto = ""
    if resultados:
        for r in resultados:
            txt_contexto += f"- {r['documento']}\n  URL: {r['id']}\n\n"
    else:
        txt_contexto = "No hay resultados disponibles en la base de datos."

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])
    
    mensajes_finales = prompt_template.format_messages(contexto=txt_contexto)
    
    # Añadimos el historial del gradiente para tener memoria (sólo últimos 4 mensajes para ahorrar tokens)
    # Gradio los pasa estructurados y nosotros los pasamos como diccionarios. 
    # Aquí transformamos tupla a objetos estandar de LangChain
    from langchain_core.messages import BaseMessage
    historia_langchain = []
    
    # Tomamos los últimos 6 mensajes (aprox 3 interacciones completas) para no saturar memoria
    if historial:
        for msg in historial[-6:]:
            if getattr(msg, "role", msg.get("role", "")) == "user":
                historia_langchain.append(HumanMessage(content=getattr(msg, "content", msg.get("content", ""))))
            elif getattr(msg, "role", msg.get("role", "")) == "assistant":
                historia_langchain.append(AIMessage(content=getattr(msg, "content", msg.get("content", ""))))
            
    historia_langchain.append(HumanMessage(content=mensaje_usuario))
    
    # Unificamos el prompt system (con datos) + el historial
    mensajes_completos = mensajes_finales + historia_langchain

    # 4. LLAMAR A LA LLM (1 Sola Vez)
    respuesta = llm.invoke(mensajes_completos)
    
    return respuesta.content
