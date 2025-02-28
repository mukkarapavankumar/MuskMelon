import logging
import json
import os
from typing import List, Dict, Any, Optional
import ollama

logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self, model: str = "llama2"):
        self.model = self._validate_model(model)
    
    def _validate_model(self, model: str) -> str:
        """Validate and return a valid model name"""
        try:
            # Get list of available models
            models = ollama.list()
            available_models = [m['name'] for m in models['models']]
            
            # If model exists, use it
            if model in available_models:
                return model
            
            # If model doesn't exist, try to find a close match
            for available_model in available_models:
                if model.lower() in available_model.lower():
                    logger.info(f"Using model {available_model} instead of {model}")
                    return available_model
            
            # If no match found, use first available model
            if available_models:
                default_model = available_models[0]
                logger.warning(f"Model {model} not found. Using {default_model} instead")
                return default_model
            
            # If no models available, use llama2 as default
            logger.warning("No models found. Using llama2 as default")
            return "llama2"
        except Exception as e:
            logger.error(f"Error validating model: {e}")
            return "llama2"
    
    def summarize(self, emails: List[Dict[str, Any]], prompt: str) -> str:
        """Summarize a list of emails using Ollama"""
        try:
            # Format emails for the prompt
            email_text = self._format_emails_for_prompt(emails)
            
            # Combine prompt with emails
            full_prompt = f"{prompt}\n\n{email_text}"
            
            # Call Ollama API
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            summary = response['message']['content']
            logger.info(f"Generated summary of {len(emails)} emails using model {self.model}")
            return summary
        except Exception as e:
            logger.error(f"Error summarizing emails: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _format_emails_for_prompt(self, emails: List[Dict[str, Any]]) -> str:
        """Format emails for inclusion in the prompt"""
        formatted_emails = []
        
        for i, email in enumerate(emails):
            formatted_email = f"EMAIL {i+1}:\n"
            formatted_email += f"From: {email['sender']} <{email['sender_email']}>\n"
            formatted_email += f"Subject: {email['subject']}\n"
            formatted_email += f"Date: {email['received_time']}\n"
            formatted_email += f"Body:\n{email['body']}\n"
            formatted_email += "-" * 50
            
            formatted_emails.append(formatted_email)
        
        return "\n\n".join(formatted_emails)