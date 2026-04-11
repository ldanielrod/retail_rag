# Retail RAG — Agente Inmobiliario Dominicano

Agente conversacional que scrapea las principales páginas de bienes raíces de República Dominicana y responde preguntas del usuario usando RAG (Retrieval-Augmented Generation).

---

## ¿Qué hace?

1. **Scraping** — extrae apartamentos en venta/alquiler de múltiples portales inmobiliarios
2. **Vectorización** — almacena los anuncios en ChromaDB como embeddings semánticos
3. **RAG** — cuando el usuario hace una pregunta, busca los anuncios más relevantes y los pasa como contexto a un LLM
4. **Chat** — responde a través de una interfaz web (Gradio) actuando como asesor inmobiliario

---

## Arquitectura

```
corotos_app/
├── core/
│   ├── base_scraper.py   # Interfaz abstracta para todos los scrapers
│   ├── models.py         # Modelos de datos (AnuncioBase, AnuncioDetalle)
│   └── config.py         # Configuración compartida (headers, filtros)
│
├── scraper/
│   ├── pipeline.py       # Orquestador multi-scraper
│   ├── processor.py      # Filtros y exportación de datos
│   │
│   ├── corotos/          # Scraper para corotos.com.do
│   │   ├── config.py
│   │   ├── fetcher.py
│   │   ├── parser.py
│   │   └── scraper.py
│   │
│   └── supercasas/       # Scraper para supercasas.com
│       ├── config.py
│       ├── fetcher.py
│       ├── parser.py
│       └── scraper.py
│
├── rag/
│   ├── db.py             # ChromaDB — almacenamiento vectorial
│   └── chain.py          # Cadena RAG + historial de conversación
│
└── ui/
    └── app.py            # Interfaz web con Gradio (puerto 7860)
```

---

## Cómo agregar un nuevo sitio

1. Crea `scraper/nuevositio/` con `config.py`, `fetcher.py`, `parser.py`, `scraper.py`
2. Tu clase hereda de `BaseScraper` e implementa 5 métodos
3. Pásala al pipeline:

```python
from corotos_app.scraper.pipeline import ejecutar_scraper
from corotos_app.scraper.corotos.scraper import CorotosScraper
from corotos_app.scraper.nuevositio.scraper import NuevoSitioScraper

resultados = ejecutar_scraper(filtros, scrapers=[CorotosScraper(), NuevoSitioScraper()])
```

---

## Stack

| Capa | Tecnología |
|---|---|
| Scraping | `requests` + `BeautifulSoup` |
| Almacenamiento vectorial | `ChromaDB` |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | `GPT-4o-mini` via LangChain |
| UI | `Gradio` |

---

## Objetivo final

Cubrir los principales portales inmobiliarios dominicanos (Corotos, SuperCasas, y otros) para ofrecer al usuario una búsqueda unificada e inteligente de propiedades a través de lenguaje natural.
