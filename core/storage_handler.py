import os
import json
import datetime
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class StorageHandler:
    def __init__(self):
        pass
    
    def store_summary(self, summary: str, emails: List[Dict[str, Any]], 
                      storage_path: str, task_name: str) -> bool:
        """Store summary and emails in JSON format with history"""
        try:
            # Ensure path has .json extension
            if not storage_path.endswith(".json"):
                storage_path += ".json"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            # Prepare new entry
            new_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "task_name": task_name,
                "summary": summary,
                "emails": [{
                    "sender": email["sender"],
                    "sender_email": email["sender_email"],
                    "subject": email["subject"],
                    "received_time": email["received_time"],
                    "body": email["body"][:500] + "..." if len(email["body"]) > 500 else email["body"]
                } for email in emails]
            }
            
            # Load existing data or create new
            data = []
            if os.path.exists(storage_path):
                try:
                    with open(storage_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    # If file is corrupted, start fresh
                    data = []
            
            # Append new entry
            data.append(new_entry)
            
            # Save updated data
            with open(storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Stored summary and {len(emails)} emails with history at {storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing summary: {e}")
            return False
    
    def get_results(self, storage_path: str) -> List[Dict[str, Any]]:
        """Get stored results from a file"""
        try:
            if not storage_path.endswith(".json"):
                storage_path += ".json"
            
            if not os.path.exists(storage_path):
                return []
            
            with open(storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return data
        except Exception as e:
            logger.error(f"Error reading results: {e}")
            return []