import win32com.client
import datetime
import logging
from typing import Dict, List, Any, Optional
from datetime import timezone

logger = logging.getLogger(__name__)

class OutlookHandler:
    def __init__(self):
        self.outlook = None
        self.namespace = None
        
    def _connect_to_outlook(self) -> None:
        """Connect to Outlook application"""
        if not self.outlook:
            try:
                self.outlook = win32com.client.Dispatch("Outlook.Application")
                self.namespace = self.outlook.GetNamespace("MAPI")
                logger.info("Connected to Outlook")
            except Exception as e:
                logger.error(f"Error connecting to Outlook: {e}")
                raise
    
    def send_email(self, recipient: str, subject: str, body: str, attachments: List[str] = None) -> bool:
        """Send an email using Outlook"""
        try:
            self._connect_to_outlook()
            
            # Create a new mail item
            mail = self.outlook.CreateItem(0)  # 0 = olMailItem
            
            # Set properties
            mail.To = recipient
            mail.Subject = subject
            mail.HTMLBody = body
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    mail.Attachments.Add(attachment)
            
            # Send the email
            mail.Send()
            
            logger.info(f"Email sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def get_responses(self, filter_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get email responses based on filter criteria"""
        try:
            self._connect_to_outlook()
            
            # Get the inbox folder
            inbox = self.namespace.GetDefaultFolder(6)  # 6 = olFolderInbox
            items = inbox.Items
            
            # Sort by received time (newest first)
            items.Sort("[ReceivedTime]", True)
            
            # Process items with manual filtering
            responses = []
            for item in items:
                matches = True
                
                # Subject filter
                if filter_criteria.get("subject"):
                    if filter_criteria["subject"].lower() not in item.Subject.lower():
                        matches = False
                        continue
                
                # Date range filter
                if filter_criteria.get("date_range"):
                    received_time = item.ReceivedTime
                    # Convert naive datetime to UTC
                    start_date = filter_criteria["date_range"]["start"].replace(tzinfo=timezone.utc)
                    end_date = (filter_criteria["date_range"]["end"] + datetime.timedelta(days=1)).replace(tzinfo=timezone.utc)
                    
                    # Convert received_time to UTC for comparison
                    try:
                        # Try to get timezone info from Outlook datetime
                        received_utc = received_time.astimezone(timezone.utc)
                    except:
                        # If that fails, assume it's in local timezone and convert to UTC
                        local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
                        received_utc = received_time.replace(tzinfo=local_tz).astimezone(timezone.utc)
                    
                    if not (start_date <= received_utc < end_date):
                        matches = False
                        continue
                
                # Keywords filter
                if filter_criteria.get("keywords") and not self._contains_keywords(item.Body, filter_criteria["keywords"]):
                    matches = False
                    continue
                
                # If all filters pass, add to responses
                if matches:
                    responses.append({
                        "id": item.EntryID,
                        "subject": item.Subject,
                        "sender": item.SenderName,
                        "sender_email": item.SenderEmailAddress,
                        "received_time": item.ReceivedTime.isoformat(),
                        "body": item.Body,
                        "html_body": item.HTMLBody
                    })
            
            logger.info(f"Found {len(responses)} email responses matching criteria")
            return responses
        except Exception as e:
            logger.error(f"Error getting email responses: {e}")
            return []
    
    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if text contains any of the keywords"""
        if not keywords:
            return True
            
        text = text.lower()
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        
        return False