import logging
import os
import time
import re
from typing import Dict, Any, Tuple, List, Optional
import torch
from transformers import MarianMTModel, MarianTokenizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Language codes for MarianMT
LANGUAGE_MAP = {
    "english": "en",
    "french": "fr",
    "spanish": "es",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    "chinese": "zh",
    "japanese": "ja",
    "korean": "ko",
    "arabic": "ar",
    "hindi": "hi",
    "dutch": "nl",
    "swedish": "sv",
    "finnish": "fi",
    "polish": "pl",
    "turkish": "tr",
    "czech": "cs",
    "greek": "el",
    "danish": "da",
    "norwegian": "no",
    "romanian": "ro",
    "ukrainian": "uk",
    "vietnamese": "vi"
}

class TranslationModel:
    """Translation model using MarianMT for local translation."""
    
    def __init__(self):
        """Initialize the model."""
        logger.info("Initializing Translation models...")
        
        start_time = time.time()
        
        # Initialize model cache
        self.models = {}
        self.tokenizers = {}
        
        # Pre-load a few common translation models
        self._load_model("en", "es")  # English to Spanish
        self._load_model("en", "fr")  # English to French
        self._load_model("en", "de")  # English to German
        
        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Models initialized on {self.device} in {time.time() - start_time:.2f} seconds")
    
    def _load_model(self, source_lang: str, target_lang: str) -> Tuple[MarianMTModel, MarianTokenizer]:
        """
        Load a translation model for the given language pair.
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Tuple of model and tokenizer
        """
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        model_key = f"{source_lang}-{target_lang}"
        
        if model_key not in self.models:
            try:
                logger.info(f"Loading model: {model_name}")
                
                # Load tokenizer and model
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                
                # Move model to device
                model.to(self.device)
                
                # Store in cache
                self.models[model_key] = model
                self.tokenizers[model_key] = tokenizer
                
                logger.info(f"Model {model_name} loaded successfully")
            
            except Exception as e:
                logger.error(f"Error loading model {model_name}: {str(e)}")
                raise
        
        return self.models[model_key], self.tokenizers[model_key]
    
    def _parse_translation_request(self, query: str) -> Tuple[str, str, str]:
        """
        Parse a translation request to extract source language, target language, and text.
        
        Args:
            query: The input query, expected format: 
                  "Translate from [source_lang] to [target_lang]: [text]"
                  
        Returns:
            Tuple of (source_lang_code, target_lang_code, text)
        """
        # Default to English-Spanish if not specified
        source_lang_code = "en"
        target_lang_code = "es"
        text = query
        
        # Try to extract language information
        pattern = r"translate\s+from\s+(\w+)\s+to\s+(\w+)\s*:?\s*(.*)"
        match = re.search(pattern, query, re.IGNORECASE)
        
        if match:
            source_lang = match.group(1).lower()
            target_lang = match.group(2).lower()
            text = match.group(3).strip()
            
            # Convert language names to codes
            source_lang_code = LANGUAGE_MAP.get(source_lang, source_lang)
            target_lang_code = LANGUAGE_MAP.get(target_lang, target_lang)
        else:
            # If no pattern match, assume the entire query is the text to translate
            # and use default language pair
            pass
        
        return source_lang_code, target_lang_code, text
    
    def translate_text(self, query: str) -> str:
        """
        Translate text as specified in the query.
        
        Args:
            query: The input query containing source language, target language, and text
            
        Returns:
            Translated text
        """
        try:
            # Parse the query
            source_lang, target_lang, text = self._parse_translation_request(query)
            
            # Load the appropriate model
            try:
                model, tokenizer = self._load_model(source_lang, target_lang)
            except Exception as e:
                logger.error(f"Error loading model for {source_lang}-{target_lang}: {str(e)}")
                return f"I'm sorry, translation from {source_lang} to {target_lang} is not currently supported. Please try another language pair."
            
            # Prepare input
            encoded = tokenizer(text, return_tensors="pt", padding=True)
            input_ids = encoded.input_ids.to(self.device)
            attention_mask = encoded.attention_mask.to(self.device)
            
            # Generate translation
            with torch.no_grad():
                output = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True
                )
            
            # Decode output
            translated_text = tokenizer.decode(output[0], skip_special_tokens=True)
            
            return translated_text
        
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            # Return a fallback response
            return "I'm sorry, I couldn't translate the text at this time. Please check your input format and try again."
    
    def __del__(self):
        """Clean up resources."""
        try:
            # Clean up GPU memory if needed
            for model in self.models.values():
                model.cpu()
            torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"Error cleaning up model resources: {str(e)}")