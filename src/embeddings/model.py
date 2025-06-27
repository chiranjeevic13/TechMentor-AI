# Embedding model wrapper
import os
import logging
from typing import List, Dict, Any, Union
import yaml
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the embedding model with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["embeddings"]
        
        self.model_name = self.config.get("model_name", "all-MiniLM-L6-v2")
        self.device = self.config.get("device", "cpu")
        
        # Load the model
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        logger.info(f"Model loaded on {self.device}")
        
        # Create directory for saved embeddings
        self.save_dir = "data/embeddings"
        os.makedirs(self.save_dir, exist_ok=True)
    
    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for a single text or a list of texts."""
        if isinstance(text, str):
            # Single text
            return self.model.encode(text)
        else:
            # List of texts
            return self.model.encode(text, show_progress_bar=True)
    
    def embed_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 32) -> List[Dict[str, Any]]:
        """Embed all chunks and return with embeddings added."""
        texts = [chunk["text"] for chunk in chunks]
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        
        # Process in batches to avoid memory issues
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self.embed_text(batch_texts)
            all_embeddings.extend(batch_embeddings)
            
            if (i+1) % 100 == 0 or i+batch_size >= len(texts):
                logger.info(f"Embedded {i+len(batch_texts)}/{len(texts)} chunks")
        
        # Add embeddings to chunks
        embedded_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_with_embedding = chunk.copy()
            chunk_with_embedding["embedding"] = all_embeddings[i]
            embedded_chunks.append(chunk_with_embedding)
        
        return embedded_chunks
    
    def save_embeddings(self, embedded_chunks: List[Dict[str, Any]], filename: str = "embeddings.npz"):
        """Save embeddings to a file."""
        save_path = os.path.join(self.save_dir, filename)
        
        # Extract texts, embeddings, and metadata
        texts = [chunk["text"] for chunk in embedded_chunks]
        embeddings = np.array([chunk["embedding"] for chunk in embedded_chunks])
        metadata = [chunk["metadata"] for chunk in embedded_chunks]
        
        # Save to numpy compressed format
        np.savez_compressed(
            save_path,
            texts=np.array(texts, dtype=object),
            embeddings=embeddings,
            metadata=np.array(metadata, dtype=object)
        )
        
        logger.info(f"Saved {len(embedded_chunks)} embeddings to {save_path}")
        return save_path
    
    def load_embeddings(self, filename: str = "embeddings.npz") -> List[Dict[str, Any]]:
        """Load embeddings from a file."""
        load_path = os.path.join(self.save_dir, filename)
        
        if not os.path.exists(load_path):
            logger.error(f"Embedding file not found: {load_path}")
            return []
        
        data = np.load(load_path, allow_pickle=True)
        texts = data["texts"]
        embeddings = data["embeddings"]
        metadata = data["metadata"]
        
        # Reconstruct chunks
        embedded_chunks = []
        for i in range(len(texts)):
            embedded_chunks.append({
                "text": texts[i],
                "embedding": embeddings[i],
                "metadata": metadata[i]
            })
        
        logger.info(f"Loaded {len(embedded_chunks)} embeddings from {load_path}")
        return embedded_chunks

if __name__ == "__main__":
    # Example usage
    model = EmbeddingModel()
    sample_texts = [
        "How do I become a machine learning engineer?",
        "What are the best resources for learning web development?",
        "Compare data science and machine learning career paths."
    ]
    embeddings = model.embed_text(sample_texts)
    print(f"Generated {len(embeddings)} embeddings of dimension {embeddings[0].shape}")