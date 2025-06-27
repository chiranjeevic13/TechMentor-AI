# Text chunking logic
import os
import logging
from typing import List, Dict, Any
import yaml
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextChunker:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the text chunker with configuration."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            self.config = config["preprocessing"]
        
        self.chunk_size = self.config.get("chunk_size", 500)
        self.chunk_overlap = self.config.get("chunk_overlap", 50)
        self.min_chunk_length = self.config.get("min_chunk_length", 100)
        
        self.input_dir = "data/raw"
        self.output_dir = "data/processed"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap.
        Returns list of dictionaries with text and metadata.
        """
        chunks = []
        
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence exceeds the chunk size and we have content
            if len(current_chunk) + len(sentence) > self.chunk_size and len(current_chunk) >= self.min_chunk_length:
                # Save the current chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "metadata": metadata.copy()
                })
                
                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_text = " ".join(words[-self.chunk_overlap:]) if len(words) > self.chunk_overlap else ""
                current_chunk = overlap_text + " " + sentence
            else:
                # Add the sentence to the current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk if it's not empty and meets minimum length
        if current_chunk and len(current_chunk) >= self.min_chunk_length:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": metadata.copy()
            })
        
        return chunks
    
    def process_files(self) -> List[Dict[str, Any]]:
        """Process all text files in the input directory and create chunks."""
        all_chunks = []
        
        # Process each subfolder in the raw data directory
        for subfolder in ['web', 'pdf_extracted', 'youtube']:
            folder_path = os.path.join(self.input_dir, subfolder)
            if not os.path.exists(folder_path):
                continue
                
            logger.info(f"Processing files in {folder_path}")
            
            for filename in os.listdir(folder_path):
                if not filename.endswith('.txt'):
                    continue
                    
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract source information from the first line if it exists
                    source = ""
                    lines = content.split('\n')
                    if lines and lines[0].startswith('Source:'):
                        source = lines[0].replace('Source:', '').strip()
                        content = '\n'.join(lines[1:])
                    
                    # Create metadata
                    metadata = {
                        "source": source,
                        "filename": filename,
                        "source_type": subfolder,
                        "doc_id": f"{subfolder}_{filename}"
                    }
                    
                    # Chunk the text
                    chunks = self._chunk_text(content, metadata)
                    all_chunks.extend(chunks)
                    
                    logger.info(f"Processed {filename}: created {len(chunks)} chunks")
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
        
        # Save all chunks to a single file for convenience
        chunks_file = os.path.join(self.output_dir, "all_chunks.jsonl")
        import json
        with open(chunks_file, 'w', encoding='utf-8') as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk) + '\n')
        
        logger.info(f"Created {len(all_chunks)} total chunks, saved to {chunks_file}")
        return all_chunks

if __name__ == "__main__":
    chunker = TextChunker()
    chunks = chunker.process_files()
    print(f"Created {len(chunks)} chunks from all documents")