import logging
import os
import time
import re
from typing import Dict, Any
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummarizationModel:
    """Summarization model using T5 for local text summarization."""
    
    def __init__(self):
        """Initialize the model."""
        logger.info("Initializing T5 model for text summarization...")
        
        start_time = time.time()
        
        # Load model and tokenizer
        model_name = "t5-base"
        
        try:
            # Load tokenizer
            self.tokenizer = T5Tokenizer.from_pretrained(model_name)
            
            # Load model
            self.model = T5ForConditionalGeneration.from_pretrained(model_name)
            
            # Move model to GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"Model loaded successfully on {self.device} in {time.time() - start_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def _extract_text_to_summarize(self, query: str) -> str:
        """
        Extract the text to summarize from the query.
        
        Args:
            query: The input query, which may contain instructions
            
        Returns:
            The text to summarize
        """
        # Check if the query starts with "Summarize:" or similar
        patterns = [
            r"^summarize:\s*(.*)",
            r"^please\s+summarize:\s*(.*)",
            r"^summarize\s+this\s+text:\s*(.*)",
            r"^summarize\s+the\s+following:\s*(.*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, use the entire query
        return query
    
    def summarize_text(self, query: str, max_length: int = 150, min_length: int = 30) -> str:
        """
        Summarize the given text.
        
        Args:
            query: The input query containing text to summarize
            max_length: Maximum length of the summary
            min_length: Minimum length of the summary
            
        Returns:
            Generated summary
        """
        try:
            # Extract the text to summarize
            text = self._extract_text_to_summarize(query)
            
            # Check if the text is too short to summarize
            if len(text.split()) < 30:
                return "The text is too short to summarize. Please provide a longer text."
            
            # Prepare input
            input_text = "summarize: " + text
            input_ids = self.tokenizer.encode(input_text, return_tensors="pt").to(self.device)
            
            # Generate summary
            with torch.no_grad():
                summary_ids = self.model.generate(
                    input_ids,
                    max_length=max_length,
                    min_length=min_length,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
            
            # Decode summary
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            # Format the response
            result = f"Summary:\n\n{summary}\n\n"
            result += f"Original Text Length: {len(text.split())} words\n"
            result += f"Summary Length: {len(summary.split())} words\n"
            
            return result
        
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            # Return a fallback response
            return "I'm sorry, I couldn't generate a summary at this time. Please try again later."
    
    def __del__(self):
        """Clean up resources."""
        try:
            # Clean up GPU memory if needed
            if hasattr(self, 'model'):
                self.model.cpu()
            torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"Error cleaning up model resources: {str(e)}")