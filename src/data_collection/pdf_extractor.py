import os
import logging
from typing import List, Dict, Any
import yaml
import PyPDF2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the PDF extractor with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["data_collection"]
        
        self.output_dir = "data/raw/pdf_extracted"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_pdfs(self) -> List[Dict[str, Any]]:
        """Extract text content from configured PDFs."""
        results = []
        
        pdf_sources = [source for source in self.config["sources"] if source["type"] == "pdf"]
        for source in pdf_sources:
            for pdf_path in source.get("paths", []):
                try:
                    if not os.path.exists(pdf_path):
                        logger.warning(f"PDF not found: {pdf_path}")
                        continue
                        
                    logger.info(f"Extracting text from: {pdf_path}")
                    
                    # Extract text from PDF
                    text = ""
                    with open(pdf_path, "rb") as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        num_pages = len(pdf_reader.pages)
                        
                        for page_num in range(num_pages):
                            page = pdf_reader.pages[page_num]
                            text += page.extract_text() + "\n\n"
                    
                    # Save the extracted text
                    basename = os.path.basename(pdf_path).replace(".pdf", "")
                    output_path = os.path.join(self.output_dir, f"{basename}.txt")
                    
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(f"Source: {pdf_path}\n\n")
                        f.write(text)
                    
                    results.append({
                        "pdf_path": pdf_path,
                        "output_path": output_path,
                        "num_pages": num_pages,
                        "content_length": len(text)
                    })
                    
                except Exception as e:
                    logger.error(f"Error extracting {pdf_path}: {str(e)}")
        
        return results

if __name__ == "__main__":
    extractor = PDFExtractor()
    results = extractor.extract_pdfs()
    logger.info(f"Extracted text from {len(results)} PDFs")