# Document retrieval logic
import logging
from typing import List, Dict, Any
import yaml
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vector_db.chroma_db import ChromaDBManager
from embeddings.model import EmbeddingModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the document retriever with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            self.rag_config = self.config["rag"]
        
        self.top_k = self.rag_config.get("top_k", 5)
        
        # Initialize vector database
        self.vector_db = ChromaDBManager(config_path)
        
        # Initialize embedding model for query embedding
        self.embedding_model = EmbeddingModel(config_path)
    
    def retrieve(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for the query."""
        logger.info(f"Retrieving documents for query: {query}")
        
        # Search in vector database
        results = self.vector_db.search(query, top_k=self.top_k)
        
        # If we have filters, apply them (basic implementation)
        if filters and results:
            filtered_results = []
            for doc in results:
                # Check if document metadata matches all filters
                match = True
                for key, value in filters.items():
                    if key in doc["metadata"] and doc["metadata"][key] != value:
                        match = False
                        break
                if match:
                    filtered_results.append(doc)
            results = filtered_results
        
        logger.info(f"Retrieved {len(results)} documents")
        return results
    
    def format_for_prompt(self, results: List[Dict[str, Any]]) -> str:
        """Format retrieved documents for insertion into a prompt."""
        if not results:
            return "No relevant information found."
        
        formatted_text = "RELEVANT INFORMATION:\n\n"
        
        for i, doc in enumerate(results):
            formatted_text += f"[Document {i+1}]\n"
            formatted_text += doc["text"] + "\n"
            
            # Add source information if available
            if "metadata" in doc and doc["metadata"].get("source"):
                formatted_text += f"Source: {doc['metadata']['source']}\n"
            
            formatted_text += "\n" + "-" * 40 + "\n\n"
        
        return formatted_text

if __name__ == "__main__":
    # Example usage
    retriever = Retriever()
    query = "How to become a full stack developer?"
    results = retriever.retrieve(query)
    formatted = retriever.format_for_prompt(results)
    print(f"Query: {query}")
    print(f"Formatted Results:\n{formatted[:500]}...")