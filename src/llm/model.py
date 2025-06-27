# LLM interface for local models
import os
import logging
from typing import Dict, Any, List, Optional
import yaml
from ctransformers import AutoModelForCausalLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalLLM:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the local LLM with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["llm"]
        
        self.model_type = self.config.get("model_type", "llama2")
        self.model_path = self.config.get("model_path", "models/llm/tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf")
        self.context_length = self.config.get("context_length", 2048)
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 512)
        
        # Make sure model directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        self.model = None
        
    def load_model(self):
        """Load the LLM model."""
        if not os.path.exists(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            logger.info("Please download a compatible GGUF model and place it in the specified path.")
            logger.info("Example models: Llama-2-7B-Chat, Mistral-7B-Instruct, Phi-2, etc.")
            logger.info("You can download models from: https://huggingface.co/TheBloke")
            return False
        
        try:
            logger.info(f"Loading LLM from {self.model_path}...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                model_type=self.model_type,
                context_length=self.context_length
            )
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def generate(self, prompt: str) -> str:
        """Generate a response to the given prompt."""
        if self.model is None:
            success = self.load_model()
            if not success:
                return "Error: Model could not be loaded. Please check the logs."
        
        try:
            logger.info("Generating response...")
            response = self.model(
                prompt,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response
        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            return f"Error during text generation: {str(e)}"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_type": self.model_type,
            "model_path": self.model_path,
            "context_length": self.context_length,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "loaded": self.model is not None
        }

if __name__ == "__main__":
    # Example usage
    llm = LocalLLM()
    if llm.load_model():
        sample_prompt = "What are the key skills needed for a software developer?"
        response = llm.generate(sample_prompt)
        print(f"Prompt: {sample_prompt}")
        print(f"Response: {response}")
            