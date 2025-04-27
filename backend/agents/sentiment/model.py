import logging
import os
import time
from typing import Dict, Any, Tuple, List
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentModel:
    """Sentiment analysis model using BERT for local classification."""
    
    def __init__(self):
        """Initialize the model."""
        logger.info("Initializing BERT model for sentiment analysis...")
        
        start_time = time.time()
        
        # Load model and tokenizer
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Load model
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Move model to GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            # Define sentiment labels
            self.labels = ["Negative", "Positive"]
            
            logger.info(f"Model loaded successfully on {self.device} in {time.time() - start_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze the sentiment of the given text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            Sentiment analysis result as a formatted string
        """
        try:
            # Encode text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Get sentiment prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=1)
            
            # Get prediction and confidence
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item() * 100
            
            sentiment_label = self.labels[predicted_class]
            
            # Create a detailed response
            result = (
                f"Sentiment Analysis Result:\n\n"
                f"Sentiment: {sentiment_label}\n"
                f"Confidence: {confidence:.2f}%\n\n"
            )
            
            # Add explanation based on sentiment
            if sentiment_label == "Positive":
                result += (
                    "The text expresses a positive sentiment. "
                    "This indicates satisfaction, happiness, or approval. "
                    "Such content is generally associated with good experiences or favorable opinions."
                )
            else:
                result += (
                    "The text expresses a negative sentiment. "
                    "This indicates dissatisfaction, unhappiness, or disapproval. "
                    "Such content is generally associated with bad experiences or unfavorable opinions."
                )
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            # Return a fallback response
            return "I'm sorry, I couldn't analyze the sentiment at this time. Please try again later."
    
    def __del__(self):
        """Clean up resources."""
        try:
            # Clean up GPU memory if needed
            if hasattr(self, 'model'):
                self.model.cpu()
            torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"Error cleaning up model resources: {str(e)}")