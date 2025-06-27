import os
import logging
import argparse
import yaml
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up the necessary environment for the project."""
    # Create required directories
    directories = [
        "data/raw/web",
        "data/raw/pdf_extracted",
        "data/raw/youtube",
        "data/processed",
        "data/embeddings",
        "models/embeddings",
        "models/llm",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def collect_data():
    """Collect data from various sources."""
    logger.info("Starting data collection")
    
    # Import data collection modules
    from src.data_collection.web_scraper import WebScraper
    from src.data_collection.pdf_extractor import PDFExtractor
    from src.data_collection.youtube_transcripts import YouTubeTranscriptFetcher
    
    # Run web scraper
    logger.info("Running web scraper")
    web_scraper = WebScraper()
    web_scraper.scrape_urls()
    
    # Run PDF extractor
    logger.info("Running PDF extractor")
    pdf_extractor = PDFExtractor()
    pdf_extractor.extract_pdfs()
    
    # Run YouTube transcript fetcher
    logger.info("Running YouTube transcript fetcher")
    youtube_fetcher = YouTubeTranscriptFetcher()
    youtube_fetcher.fetch_transcripts()
    
    logger.info("Data collection completed")

def process_data():
    """Process the collected data."""
    logger.info("Starting data processing")
    
    # Import preprocessing modules
    from src.preprocessing.chunker import TextChunker
    from src.preprocessing.text_cleaner import TextCleaner
    
    # Chunk the text
    logger.info("Chunking text")
    chunker = TextChunker()
    chunks = chunker.process_files()
    
    # Clean the chunks
    logger.info("Cleaning text chunks")
    cleaner = TextCleaner()
    cleaned_chunks = cleaner.clean_chunks(chunks)
    
    logger.info(f"Processed {len(cleaned_chunks)} chunks")
    return cleaned_chunks

def create_embeddings(chunks):
    """Create embeddings for the processed chunks."""
    logger.info("Creating embeddings")
    
    # Import embedding module
    from src.embeddings.model import EmbeddingModel
    
    # Generate embeddings
    embedding_model = EmbeddingModel()
    embedded_chunks = embedding_model.embed_chunks(chunks)
    
    # Save embeddings
    embedding_model.save_embeddings(embedded_chunks)
    
    logger.info("Embeddings created and saved")
    return embedded_chunks

def build_vector_db(embedded_chunks):
    """Build the vector database."""
    logger.info("Building vector database")
    
    # Import vector DB module
    from src.vector_db.chroma_db import ChromaDBManager
    
    # Add documents to the database
    db_manager = ChromaDBManager()
    db_manager.add_documents(embedded_chunks)
    
    # Print database stats
    stats = db_manager.get_collection_stats()
    logger.info(f"Vector database built with {stats['document_count']} documents")

def download_llm_model():
    """Download the LLM model if it doesn't exist."""
    logger.info("Checking LLM model")
    
    # Load config to get model path
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
        model_path = config["llm"]["model_path"]
    
    if not os.path.exists(model_path):
        logger.info(f"Model not found at {model_path}")
        logger.info("Please download a compatible GGUF model from Hugging Face")
        logger.info("Example models: Llama-2-7B-Chat, Mistral-7B-Instruct, Phi-2, etc.")
        logger.info("You can download models from: https://huggingface.co/TheBloke")
        
        # Provide instructions for a specific model as an example
        logger.info("\nExample download instructions:")
        logger.info("1. Go to https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/tree/main")
        logger.info("2. Download 'llama-2-7b-chat.Q4_K_M.gguf'")
        logger.info(f"3. Save it to {model_path}")
    else:
        logger.info(f"LLM model found at {model_path}")

def run_app():
    """Run the Streamlit app."""
    logger.info("Running Streamlit app")
    os.system("streamlit run app/app.py")

def main():
    """Main function to run the entire pipeline."""
    parser = argparse.ArgumentParser(description="TechMentor AI RAG Pipeline")
    parser.add_argument("--collect", action="store_true", help="Collect data")
    parser.add_argument("--process", action="store_true", help="Process data")
    parser.add_argument("--embed", action="store_true", help="Create embeddings")
    parser.add_argument("--build-db", action="store_true", help="Build vector database")
    parser.add_argument("--check-model", action="store_true", help="Check LLM model")
    parser.add_argument("--app", action="store_true", help="Run Streamlit app")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Run selected steps
    chunks = None
    embedded_chunks = None
    
    if args.all or args.collect:
        collect_data()
    
    if args.all or args.process:
        chunks = process_data()
    
    if args.all or args.embed:
        if chunks is None:
            logger.warning("No chunks available for embedding. Running processing step.")
            chunks = process_data()
        embedded_chunks = create_embeddings(chunks)
    
    if args.all or args.build_db:
        if embedded_chunks is None:
            logger.info("Loading pre-saved embeddings for vector DB")
            # Add the import here if you prefer a local import
            from src.embeddings.model import EmbeddingModel
            embedding_model = EmbeddingModel()
            embedded_chunks = embedding_model.load_embeddings()
            
        if embedded_chunks:
            build_vector_db(embedded_chunks)
        else:
            logger.error("No embedded chunks available for building vector DB")
    
    if args.all or args.check_model:
        download_llm_model()
    
    if args.all or args.app:
        run_app()
    
    # If no args specified, show help
    if not any(vars(args).values()):
        parser.print_help()

if __name__ == "__main__":
    main()