import os
import json
import csv
import datetime
import pandas as pd
import win32com.client
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class StorageHandler:
    def __init__(self):
        pass
    
    def store_summary(self, summary: str, emails: List[Dict[str, Any]], 
                      storage_type: str, storage_path: str, task_name: str) -> bool:
        """Store summary and emails in the specified storage type"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            
            # Store based on type
            if storage_type == "csv":
                return self._store_as_csv(summary, emails, storage_path, task_name)
            elif storage_type == "excel":
                return self._store_as_excel(summary, emails, storage_path, task_name)
            elif storage_type == "onenote":
                return self._store_in_onenote(summary, emails, storage_path, task_name)
            else:
                logger.error(f"Unsupported storage type: {storage_type}")
                return False
        except Exception as e:
            logger.error(f"Error storing summary: {e}")
            return False
    
    def _store_as_csv(self, summary: str, emails: List[Dict[str, Any]], 
                     storage_path: str, task_name: str) -> bool:
        """Store summary and emails as CSV files"""
        try:
            # Ensure path has .csv extension
            if not storage_path.endswith(".csv"):
                storage_path += ".csv"
            
            # Create summary file
            summary_path = storage_path.replace(".csv", "_summary.csv")
            with open(summary_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Task Name", "Date", "Summary"])
                writer.writerow([
                    task_name,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    summary
                ])
            
            # Create emails file
            emails_data = []
            for email in emails:
                emails_data.append({
                    "Sender": email["sender"],
                    "Email": email["sender_email"],
                    "Subject": email["subject"],
                    "Date": email["received_time"],
                    "Content": email["body"][:500] + "..." if len(email["body"]) > 500 else email["body"]
                })
            
            df = pd.DataFrame(emails_data)
            df.to_csv(storage_path, index=False, encoding="utf-8")
            
            logger.info(f"Stored summary and {len(emails)} emails as CSV at {storage_path}")
            return True
        except Exception as e:
            logger.error(f"Error storing as CSV: {e}")
            return False
    
    def _store_as_excel(self, summary: str, emails: List[Dict[str, Any]], 
                       storage_path: str, task_name: str) -> bool:
        """Store summary and emails as Excel file"""
        try:
            # Ensure path has .xlsx extension
            if not storage_path.endswith((".xlsx", ".xls")):
                storage_path += ".xlsx"
            
            # Create Excel writer
            with pd.ExcelWriter(storage_path, engine="openpyxl") as writer:
                # Summary sheet
                summary_data = pd.DataFrame({
                    "Task Name": [task_name],
                    "Date": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Summary": [summary]
                })
                summary_data.to_excel(writer, sheet_name="Summary", index=False)
                
                # Emails sheet
                emails_data = []
                for email in emails:
                    emails_data.append({
                        "Sender": email["sender"],
                        "Email": email["sender_email"],
                        "Subject": email["subject"],
                        "Date": email["received_time"],
                        "Content": email["body"][:500] + "..." if len(email["body"]) > 500 else email["body"]
                    })
                
                emails_df = pd.DataFrame(emails_data)
                emails_df.to_excel(writer, sheet_name="Emails", index=False)
            
            logger.info(f"Stored summary and {len(emails)} emails as Excel at {storage_path}")
            return True
        except Exception as e:
            logger.error(f"Error storing as Excel: {e}")
            return False
    
    def _store_in_onenote(self, summary: str, emails: List[Dict[str, Any]], 
                         storage_path: str, task_name: str) -> bool:
        """Store summary and emails in OneNote"""
        try:
            # Connect to OneNote
            onenote = win32com.client.Dispatch("OneNote.Application")
            
            # Parse storage path (expected format: "Section/Page")
            path_parts = storage_path.split("/")
            if len(path_parts) < 2:
                section_name = "Email Automation"
                page_name = storage_path
            else:
                section_name = path_parts[0]
                page_name = path_parts[1]
            
            # Get notebooks
            notebooks = onenote.GetHierarchy("", 0)  # 0 = hsNotebooks
            
            # Find or create section
            section_id = self._find_or_create_section(onenote, notebooks, section_name)
            if not section_id:
                logger.error(f"Could not find or create section: {section_name}")
                return False
            
            # Create page title with date
            page_title = f"{page_name} - {datetime.datetime.now().strftime('%Y-%m-%d')}"
            
            # Create page content
            page_content = f"""
            <html>
                <head>
                    <title>{page_title}</title>
                </head>
                <body>
                    <h1>{task_name} - Email Summary</h1>
                    <p><strong>Date:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    
                    <h2>Summary</h2>
                    <p>{summary}</p>
                    
                    <h2>Emails ({len(emails)})</h2>
            """
            
            # Add emails
            for i, email in enumerate(emails):
                page_content += f"""
                    <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
                        <p><strong>From:</strong> {email['sender']} &lt;{email['sender_email']}&gt;</p>
                        <p><strong>Subject:</strong> {email['subject']}</p>
                        <p><strong>Date:</strong> {email['received_time']}</p>
                        <p><strong>Content:</strong></p>
                        <pre>{email['body'][:500]}{'...' if len(email['body']) > 500 else ''}</pre>
                    </div>
                """
            
            page_content += """
                </body>
            </html>
            """
            
            # Create the page
            onenote.CreateNewPage(section_id, "", "")
            
            # Get the new page ID
            section_pages = onenote.GetHierarchy(section_id, 1)  # 1 = hsPages
            page_id = section_pages.getAttribute("ID")
            
            # Update page content
            onenote.UpdatePageContent(page_content, page_id)
            
            logger.info(f"Stored summary and {len(emails)} emails in OneNote at {section_name}/{page_title}")
            return True
        except Exception as e:
            logger.error(f"Error storing in OneNote: {e}")
            return False
    
    def _find_or_create_section(self, onenote, notebooks, section_name):
        """Find or create a section in OneNote"""
        try:
            # Try to find the section
            for notebook in notebooks:
                sections = onenote.GetHierarchy(notebook.getAttribute("ID"), 2)  # 2 = hsSections
                for section in sections:
                    if section.getAttribute("name") == section_name:
                        return section.getAttribute("ID")
            
            # Section not found, create it in the first notebook
            notebook_id = notebooks[0].getAttribute("ID")
            onenote.CreateNewSection(notebook_id, section_name)
            
            # Get the new section ID
            sections = onenote.GetHierarchy(notebook_id, 2)  # 2 = hsSections
            for section in sections:
                if section.getAttribute("name") == section_name:
                    return section.getAttribute("ID")
            
            return None
        except Exception as e:
            logger.error(f"Error finding or creating OneNote section: {e}")
            return None