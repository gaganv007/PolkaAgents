import logging
import os
import time
from typing import Dict, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotModel:
    """Chatbot model using GPT-2 for local text generation."""
    
    def __init__(self):
        """Initialize the model."""
        logger.info("Initializing GPT-2 model for offline chatbot...")
        
        start_time = time.time()
        
        # Load model and tokenizer
        model_name = "gpt2-large"  # Using GPT-2 Large for better quality
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Move model to GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"Model loaded successfully on {self.device} in {time.time() - start_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def generate_response(self, prompt: str, max_length: int = 200) -> str:
        """
        Generate a response to the given prompt.
        
        Args:
            prompt: The input prompt/query
            max_length: Maximum length of generated text
            
        Returns:
            Generated text response
        """
        try:
            # Format the prompt for better results
            formatted_prompt = f"Question: {prompt}\n\nAnswer:"
            
            # Encode the prompt
            input_ids = self.tokenizer.encode(formatted_prompt, return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    max_length=max_length + len(input_ids[0]),
                    num_return_sequences=1,
                    temperature=0.8,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode the generated response
            full_response = self.tokenizer.decode(output[0], skip_special_tokens=True)
            
            # Extract just the answer part
            response = full_response.split("Answer:")[-1].strip()
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            # Return a fallback response
            return "I'm sorry, I couldn't generate a response at this time. Please try again later."
    
    def __del__(self):
        """Clean up resources."""
        try:
            # Clean up any resources if needed
            pass
        except Exception as e:
            logger.error(f"Error cleaning up model resources: {str(e)}")