import os
import json
import datetime
import threading
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any

from core.outlook_handler import OutlookHandler
from core.ai_summarizer import AISummarizer
from core.storage_handler import StorageHandler

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self):
        self.tasks_file = Path("data/tasks.json")
        self.logs_file = Path("data/logs.json")
        self.settings_file = Path("data/settings.json")
        self.outlook = OutlookHandler()
        
        # Load AI model from settings
        ai_model = "llama2"  # default model
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                    ai_model = settings.get("ai_model", ai_model)
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
        
        self.ai_summarizer = AISummarizer(model=ai_model)
        self.storage_handler = StorageHandler()
        self.task_locks = {}  # Dictionary to store locks for each task
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize tasks file if it doesn't exist
        if not self.tasks_file.exists():
            with open(self.tasks_file, "w") as f:
                json.dump([], f)
        
        # Initialize logs file if it doesn't exist
        if not self.logs_file.exists():
            with open(self.logs_file, "w") as f:
                json.dump([], f)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        try:
            with open(self.tasks_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            return []
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID"""
        tasks = self.get_all_tasks()
        for task in tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def save_task(self, task: Dict[str, Any]) -> bool:
        """Save a task (create or update)"""
        try:
            tasks = self.get_all_tasks()
            
            # Check if task already exists
            for i, existing_task in enumerate(tasks):
                if existing_task["id"] == task["id"]:
                    tasks[i] = task
                    break
            else:
                # Task doesn't exist, add it
                tasks.append(task)
            
            # Save tasks
            with open(self.tasks_file, "w") as f:
                json.dump(tasks, f, indent=2)
            
            self.log_event(f"Task '{task['name']}' saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving task: {e}")
            self.log_event(f"Error saving task: {e}", "error")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID"""
        try:
            tasks = self.get_all_tasks()
            tasks = [task for task in tasks if task["id"] != task_id]
            
            # Save tasks
            with open(self.tasks_file, "w") as f:
                json.dump(tasks, f, indent=2)
            
            self.log_event(f"Task with ID {task_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            self.log_event(f"Error deleting task: {e}", "error")
            return False
    
    def process_due_tasks(self) -> None:
        """Process tasks that are due to run"""
        tasks = self.get_all_tasks()
        now = datetime.datetime.now()
        
        for task in tasks:
            if not task.get("active", True):
                continue
            
            task_id = task.get("id")
            if task_id not in self.task_locks:
                self.task_locks[task_id] = threading.Lock()
            
            # Try to acquire lock - skip if task is already running
            if not self.task_locks[task_id].acquire(blocking=False):
                continue
            
            try:
                # Check if task is due
                next_run = datetime.datetime.fromisoformat(task["next_run"])
                if next_run <= now:
                    # Update next run time before executing to prevent multiple executions
                    self._update_next_run_time(task)
                    
                    # Execute task directly instead of in a thread
                    self._execute_task(task)
            finally:
                self.task_locks[task_id].release()
    
    def _execute_task(self, task: Dict[str, Any]) -> None:
        """Execute a task"""
        try:
            self.log_event(f"Starting execution of task '{task['name']}'")
            
            # Step 1: Send emails if needed
            if task.get("send_emails", False):
                self._send_emails(task)
            
            # Step 2: Process responses if needed
            if task.get("process_responses", False):
                self._process_responses(task)
            
            self.log_event(f"Task '{task['name']}' executed successfully")
        except Exception as e:
            logger.error(f"Error executing task '{task['name']}': {e}")
            self.log_event(f"Error executing task '{task['name']}': {e}", "error")
    
    def _send_emails(self, task: Dict[str, Any]) -> None:
        """Send emails for a task"""
        try:
            # Get recipients
            recipients = self._get_recipients(task)
            
            # Get email template
            subject = task.get("email_subject", "")
            body = task.get("email_body", "")
            
            # Send emails
            for recipient in recipients:
                # Replace placeholders in subject and body
                personalized_subject = self._replace_placeholders(subject, recipient)
                personalized_body = self._replace_placeholders(body, recipient)
                
                # Send email
                self.outlook.send_email(
                    recipient["email"],
                    personalized_subject,
                    personalized_body,
                    task.get("email_attachments", [])
                )
                
                self.log_event(f"Email sent to {recipient['email']}")
            
            self.log_event(f"Sent {len(recipients)} emails for task '{task['name']}'")
        except Exception as e:
            logger.error(f"Error sending emails for task '{task['name']}': {e}")
            self.log_event(f"Error sending emails for task '{task['name']}': {e}", "error")
            raise
    
    def _get_recipients(self, task: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get recipients for a task"""
        recipients = []
        
        # Manual recipients
        if task.get("manual_recipients"):
            recipients.extend(task["manual_recipients"])
        
        # File recipients
        if task.get("recipient_file"):
            try:
                file_path = task["recipient_file"]
                if file_path.endswith(".csv"):
                    df = pd.read_csv(file_path)
                elif file_path.endswith((".xlsx", ".xls")):
                    df = pd.read_excel(file_path)
                else:
                    raise ValueError(f"Unsupported file format: {file_path}")
                
                # Convert DataFrame to list of dictionaries
                file_recipients = df.to_dict(orient="records")
                recipients.extend(file_recipients)
            except Exception as e:
                logger.error(f"Error loading recipients from file: {e}")
                self.log_event(f"Error loading recipients from file: {e}", "error")
        
        return recipients
    
    def _replace_placeholders(self, text: str, data: Dict[str, str]) -> str:
        """Replace placeholders in text with data"""
        for key, value in data.items():
            text = text.replace(f"{{{key}}}", str(value))
        
        # Add current date
        text = text.replace("{current_date}", datetime.datetime.now().strftime("%Y-%m-%d"))
        
        return text
    
    def _process_responses(self, task: Dict[str, Any]) -> None:
        """Process email responses for a task"""
        try:
            # Get filter criteria
            filter_criteria = {
                "subject": task.get("response_subject_filter", ""),
                "keywords": task.get("response_keywords", []),
                "date_range": {
                    "start": datetime.datetime.now() - datetime.timedelta(days=task.get("response_days_back", 7)),
                    "end": datetime.datetime.now()
                }
            }
            
            # Get responses
            responses = self.outlook.get_responses(filter_criteria)
            
            if not responses:
                self.log_event(f"No responses found for task '{task['name']}'")
                return
            
            # Summarize responses
            ai_prompt = task.get("ai_prompt", "Summarize the following email responses:")
            summary = self.ai_summarizer.summarize(responses, ai_prompt)
            
            # Store summary
            storage_path = task.get("storage_path", f"data/summaries/{task['id']}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            self.storage_handler.store_summary(
                summary,
                responses,
                storage_path,
                task["name"]
            )
            
            self.log_event(f"Processed and stored {len(responses)} responses for task '{task['name']}'")
        except Exception as e:
            logger.error(f"Error processing responses for task '{task['name']}': {e}")
            self.log_event(f"Error processing responses for task '{task['name']}': {e}", "error")
            raise
    
    def _update_next_run_time(self, task: Dict[str, Any]) -> None:
        """Update the next run time for a task based on recurrence"""
        try:
            recurrence = task.get("recurrence", "once")
            current_next_run = datetime.datetime.fromisoformat(task["next_run"])
            
            if recurrence == "once":
                # For one-time tasks, deactivate after running
                task["active"] = False
                new_next_run = current_next_run
            elif recurrence == "daily":
                new_next_run = current_next_run + datetime.timedelta(days=1)
            elif recurrence == "weekly":
                new_next_run = current_next_run + datetime.timedelta(weeks=1)
            elif recurrence == "monthly":
                # Add one month (approximately)
                if current_next_run.month == 12:
                    new_next_run = current_next_run.replace(year=current_next_run.year + 1, month=1)
                else:
                    new_next_run = current_next_run.replace(month=current_next_run.month + 1)
            else:
                # Default to daily
                new_next_run = current_next_run + datetime.timedelta(days=1)
            
            # Update task
            task["next_run"] = new_next_run.isoformat()
            self.save_task(task)
        except Exception as e:
            logger.error(f"Error updating next run time for task '{task['name']}': {e}")
            self.log_event(f"Error updating next run time for task '{task['name']}': {e}", "error")
    
    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs with optional limit"""
        try:
            with open(self.logs_file, "r") as f:
                logs = json.load(f)
            
            # Sort logs by timestamp (newest first)
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Apply limit
            return logs[:limit]
        except Exception as e:
            logger.error(f"Error loading logs: {e}")
            return []
    
    def log_event(self, message: str, level: str = "info") -> None:
        """Log an event"""
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "message": message,
                "level": level
            }
            
            # Load existing logs
            try:
                with open(self.logs_file, "r") as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            # Add new log entry
            logs.append(log_entry)
            
            # Save logs
            with open(self.logs_file, "w") as f:
                json.dump(logs, f, indent=2)
            
            # Log to logger as well
            if level == "error":
                logger.error(message)
            else:
                logger.info(message)
        except Exception as e:
            logger.error(f"Error logging event: {e}")