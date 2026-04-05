import chromadb
from langchain_openai import OpenAIEmbeddings

class CorotosDB:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        self.collection = self.client.get_or_create_collection(name="corotos_apartamentos")
        
    def inyectar_apartamentos(self, lista_anuncios: list[dict]):
        if not lista_anuncios:
            return
            
        docs, metadatas, ids = [], [], []
        for anuncio in lista_anuncios:
            texto_documento = (
                f"Apartamento en {anuncio.get('operacion')} en {anuncio.get('ubicacion')} "
                f"({anuncio.get('sector_buscado')}). "
                f"Características: {anuncio.get('habitaciones')} habitaciones, "
                f"{anuncio.get('banos')} baños, {anuncio.get('metros_m2')} metros cuadrados. "
                f"Amueblado: {anuncio.get('amueblado')}. "
                f"Precio: {anuncio.get('precio_texto')}. "
                f"Título original: {anuncio.get('titulo')}."
            )
            meta = {k: str(v) if v is not None else "" for k, v in anuncio.items()}
            docs.append(texto_documento)
            metadatas.append(meta)
            ids.append(anuncio.get("url")) 
            
        embeddings = self.embedding_function.embed_documents(docs)
        self.collection.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metadatas)

    def buscar_similares(self, query: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.embedding_function.embed_query(query)
        resultados = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        if not resultados["documents"] or not resultados["documents"][0]:
            return []
            
        encontrados = []
        for i in range(len(resultados["ids"][0])):
            encontrados.append({
                "id": resultados["ids"][0][i],
                "documento": resultados["documents"][0][i],
                "metadata": resultados["metadatas"][0][i]
            })
        return encontrados
