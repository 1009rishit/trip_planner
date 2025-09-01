import chromadb
from chromadb.config import Settings
from db.embedding import MiniLMEmbedder

# Initialize ChromaDB client with new API
client = chromadb.PersistentClient(
    settings=Settings(
        persist_directory="./chroma_db"
    )
)

def get_memory_collection(name="trip_memory"):
    existing_collections = [c.name for c in client.list_collections()]
    if name in existing_collections:
        return client.get_collection(name)
    else:
        return client.create_collection(name)

# Add memory to ChromaDB
def add_memory(doc_id: str, text: str, metadata: dict):
    collection = get_memory_collection()
    embedder = MiniLMEmbedder()
    vector = embedder.embed_text(text)
    collection.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[metadata],
        embeddings=[vector]
    )

# Query memory
def query_memory(query: str, top_k: int = 1):
    collection = get_memory_collection()
    embedder = MiniLMEmbedder()
    query_vector = embedder.embed_text(query)
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    return results
