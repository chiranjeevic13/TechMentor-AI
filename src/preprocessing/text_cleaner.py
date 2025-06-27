# Text cleaning and normalization
import re
import logging
from typing import List, Dict, Any
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextCleaner:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the text cleaner with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["preprocessing"]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '[EMAIL]', text)
        
        # Replace multiple newlines with a single one
        text = re.sub(r'\n+', '\n', text)
        
        # Fix common unicode issues
        text = text.replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
        
        # Replace multiple spaces with a single space
        text = re.sub(r' +', ' ', text)
        
        return text
    
    def clean_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean the text in each chunk."""
        cleaned_chunks = []
        
        for chunk in chunks:
            chunk_copy = chunk.copy()
            chunk_copy["text"] = self.clean_text(chunk["text"])
            cleaned_chunks.append(chunk_copy)
        
        return cleaned_chunks

if __name__ == "__main__":
    # Example usage
    cleaner = TextCleaner()
    sample_text = "This is a   test\n\nwith multiple spaces   and newlines. https://example.com"
    clean = cleaner.clean_text(sample_text)
    print(f"Original: {sample_text}")
    print(f"Cleaned: {clean}")