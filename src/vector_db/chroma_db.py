# ChromaDB implementation
import os
import logging
from typing import List, Dict, Any, Optional
import yaml
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDBManager:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the ChromaDB manager with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["vector_db"]
        
        self.persist_directory = self.config.get("persist_directory", "data/chroma_db")
        self.collection_name = self.config.get("collection_name", "tech_mentor")
        
        # Create directory for ChromaDB
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Default embedding function (we'll use our own embeddings)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Found existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, chunks: List[Dict[str, Any]], use_precomputed_embeddings: bool = True):
        """Add documents to the vector database."""
        if not chunks:
            logger.warning("No chunks to add to the database")
            return
        
        logger.info(f"Adding {len(chunks)} documents to ChromaDB")
        
        # Prepare data for ChromaDB
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # If using precomputed embeddings
        embeddings = None
        if use_precomputed_embeddings and "embedding" in chunks[0]:
            embeddings = [chunk["embedding"].tolist() for chunk in chunks]
            
        # Add documents in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            batch_ids = ids[i:end_idx]
            batch_documents = documents[i:end_idx]
            batch_metadatas = metadatas[i:end_idx]
            batch_embeddings = None if embeddings is None else embeddings[i:end_idx]
            
            self.collection.add(
                ids=batch_ids,
                documents=batch_documents,
                metadatas=batch_metadatas,
                embeddings=batch_embeddings
            )
            
            logger.info(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "text": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "id": results["ids"][0][i] if results["ids"] else f"result_{i}",
                    "distance": results["distances"][0][i] if "distances" in results and results["distances"] else None
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": self.persist_directory
        }

if __name__ == "__main__":
    # Example usage
    db = ChromaDBManager()
    print(db.get_collection_stats())
    
    # Test search if there are documents
    if db.collection.count() > 0:
        results = db.search("How to become a web developer?", top_k=3)
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"Text: {result['text'][:100]}...")
            print(f"Source: {result['metadata'].get('source', 'Unknown')}")
            print()