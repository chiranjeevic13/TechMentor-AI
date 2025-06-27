import logging
from typing import List, Dict, Any
import yaml
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.model import LocalLLM
from rag.retriever import Retriever
from data_collection.dynamic_search import DynamicSearchEngine  # Import the dynamic search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the response generator with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            self.rag_config = self.config["rag"]
        
        self.prompt_template = self.rag_config.get("prompt_template", "")
        self.dynamic_search_enabled = self.rag_config.get("dynamic_search_enabled", True)
        self.min_relevance_score = self.rag_config.get("min_relevance_score", 0.6)
        
        # Initialize LLM
        self.llm = LocalLLM(config_path)
        self.llm.load_model()
        
        # Initialize retriever
        self.retriever = Retriever(config_path)
        
        # Initialize dynamic search engine
        self.dynamic_search = DynamicSearchEngine()
    
    def is_content_relevant(self, question: str, retrieved_docs: List[Dict[str, Any]]) -> bool:
        """Check if the retrieved content is relevant to the question."""
        # If no documents retrieved, it's definitely not relevant
        if not retrieved_docs:
            return False
            
        # Simple heuristic: If we have less than 2 documents or they're very short, likely not relevant
        if len(retrieved_docs) < 2:
            return False
            
        total_content_length = sum(len(doc["text"]) for doc in retrieved_docs)
        if total_content_length < 500:  # Arbitrary threshold
            return False
        
        # For more advanced relevance checking, you could use the LLM to evaluate
        # or compare embedding similarity between question and retrieved content
        
        return True
    
    def perform_dynamic_search(self, question: str) -> str:
        """Perform dynamic web search and extract content."""
        logger.info(f"Performing dynamic web search for: {question}")
        
        # Search for relevant web pages
        search_results = self.dynamic_search.search(question, num_results=3)
        
        if not search_results:
            return "No relevant information found from web search."
        
        # Extract content from the top results
        all_content = []
        for i, result in enumerate(search_results):
            if "url" in result and result["url"]:
                content = self.dynamic_search.extract_content(result["url"])
                all_content.append(f"[Source {i+1}: {result['url']}]\n{content}\n")
        
        # Combine all extracted content
        combined_content = "\n".join(all_content)
        
        # If combined content is too long, truncate it
        max_length = 4000  # Arbitrary limit to avoid context length issues
        if len(combined_content) > max_length:
            combined_content = combined_content[:max_length] + "... [content truncated]"
        
        return combined_content
    
    def generate_response(self, question: str) -> Dict[str, Any]:
        """Generate a response using the RAG pipeline with dynamic search fallback."""
        logger.info(f"Generating response for question: {question}")
        
        # First try with local knowledge base
        retrieved_docs = self.retriever.retrieve(question)
        
        # Check if we need to use dynamic search
        sources = [doc["metadata"].get("source", "Unknown") for doc in retrieved_docs]
        dynamic_content = None
        
        if self.dynamic_search_enabled and not self.is_content_relevant(question, retrieved_docs):
            logger.info("Local content not sufficient, performing dynamic search")
            dynamic_content = self.perform_dynamic_search(question)
            
            if dynamic_content and dynamic_content != "No relevant information found from web search.":
                # Add dynamic content to the context
                context = self.retriever.format_for_prompt(retrieved_docs)
                if context == "No relevant information found.":
                    context = dynamic_content
                else:
                    context = context + "\n\nADDITIONAL WEB SEARCH RESULTS:\n" + dynamic_content
                
                # Add web sources to the sources list
                sources.append("Dynamic Web Search")
            else:
                context = self.retriever.format_for_prompt(retrieved_docs)
        else:
            context = self.retriever.format_for_prompt(retrieved_docs)
        
        # Create prompt using template or a default format
        if "{context}" in self.prompt_template and "{question}" in self.prompt_template:
            prompt = self.prompt_template.format(
                context=context,
                question=question
            )
        else:
            # TinyLlama specific prompt format
            prompt = f"""<|system|>
You are TechMentor AI, a helpful tech career advisor. Answer the user's question based on the following information:
{context}
</s>

<|user|>
{question}
</s>

<|assistant|>
"""
        
        # Generate response with LLM
        response = self.llm.generate(prompt)
        
        # Return response with sources
        return {
            "question": question,
            "answer": response,
            "sources": sources,
            "used_dynamic_search": dynamic_content is not None
        }

    def format_response_with_sources(self, response: Dict[str, Any]) -> str:
        """Format the response with citation sources."""
        formatted_response = response["answer"]
        
        # Add dynamic search indicator
        if response.get("used_dynamic_search", False):
            formatted_response += "\n\n[Note: This response includes information from a real-time web search]"
        
        # Add sources if available
        if response["sources"]:
            formatted_response += "\n\nSources:\n"
            unique_sources = list(set(response["sources"]))
            for i, source in enumerate(unique_sources):
                if source and source != "Unknown":
                    formatted_response += f"{i+1}. {source}\n"
        
        return formatted_response