import logging
import os
import time
import re
from typing import Dict, Any, Tuple, Optional
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobApplicationModel:
    """Job application writer using GPT-2 for local text generation."""
    
    def __init__(self):
        """Initialize the model."""
        logger.info("Initializing GPT-2 model for job application writing...")
        
        start_time = time.time()
        
        # Load model and tokenizer
        model_name = "gpt2-large"  # Using GPT-2 Large for better quality
        
        try:
            # Load tokenizer
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            
            # Load model
            self.model = GPT2LMHeadModel.from_pretrained(model_name)
            
            # Move model to GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"Model loaded successfully on {self.device} in {time.time() - start_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def _parse_job_application_request(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse a job application request to extract resume and job description.
        
        Args:
            query: The input query containing resume and job description
            
        Returns:
            Tuple of (resume, job_description)
        """
        # Try to extract resume and job description using patterns
        resume = None
        job_description = None
        
        # Pattern 1: Explicit labeling
        resume_pattern = r"resume:\s*(.*?)(?=job description:|$)"
        job_desc_pattern = r"job description:\s*(.*)"
        
        resume_match = re.search(resume_pattern, query, re.IGNORECASE | re.DOTALL)
        job_match = re.search(job_desc_pattern, query, re.IGNORECASE | re.DOTALL)
        
        if resume_match:
            resume = resume_match.group(1).strip()
        
        if job_match:
            job_description = job_match.group(1).strip()
        
        # If pattern 1 didn't work, try pattern 2: Double newline separation
        if not resume or not job_description:
            parts = query.split("\n\n")
            if len(parts) >= 2:
                # Assume first part is resume, second is job description
                resume = parts[0].strip()
                job_description = parts[1].strip()
        
        return resume, job_description
    
    def generate_document(self, query: str, max_length: int = 500) -> str:
        """
        Generate a job application document based on resume and job description.
        
        Args:
            query: The input query containing resume and job description
            max_length: Maximum length of generated text
            
        Returns:
            Generated job application document
        """
        try:
            # Parse the query to extract resume and job description
            resume, job_description = self._parse_job_application_request(query)
            
            # Check if we have both resume and job description
            if not resume:
                return "I couldn't identify your resume in the query. Please provide your resume details."
            
            if not job_description:
                return "I couldn't identify the job description in the query. Please provide the job description details."
            
            # Format the prompt
            prompt = (
                "Write a professional cover letter for a job application based on the following resume and job description.\n\n"
                f"Resume:\n{resume}\n\n"
                f"Job Description:\n{job_description}\n\n"
                "Cover Letter:"
            )
            
            # Encode the prompt
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # Generate cover letter
            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    max_length=min(len(input_ids[0]) + max_length, self.model.config.max_position_embeddings),
                    num_return_sequences=1,
                    temperature=0.8,
                    do_sample=True,
                    top_p=0.95,
                    no_repeat_ngram_size=3,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode the generated text
            generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
            
            # Extract the cover letter part
            cover_letter = generated_text.split("Cover Letter:")[-1].strip()
            
            # Format the result
            result = "Professional Cover Letter\n\n"
            result += cover_letter
            
            return result
        
        except Exception as e:
            logger.error(f"Error generating job application: {str(e)}")
            # Return a fallback response
            return "I'm sorry, I couldn't generate a job application document at this time. Please try again later."
    
    def __del__(self):
        """Clean up resources."""
        try:
            # Clean up GPU memory if needed
            if hasattr(self, 'model'):
                self.model.cpu()
            torch.cuda.empty_cache()
        except Exception as e:
            logger.error(f"Error cleaning up model resources: {str(e)}")