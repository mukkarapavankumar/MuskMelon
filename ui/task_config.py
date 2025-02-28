from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QCheckBox,
    QTabWidget, QFileDialog, QListWidget, QListWidgetItem,
    QScrollArea, QFormLayout, QGroupBox, QSpinBox, QFrame
)
from PySide6.QtCore import Qt, QDateTime, QSize
from PySide6.QtGui import QIcon, QFont

import datetime
import uuid
import os
import json
from typing import Callable, Dict, List, Any, Optional

class TaskConfigWidget(QWidget):
    def __init__(self, task_manager, navigate_callback):
        super().__init__()
        self.task_manager = task_manager
        self.navigate_callback = navigate_callback
        self.current_task_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the task configuration UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Create New Task")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(120, 40)
        cancel_btn.clicked.connect(lambda: self.navigate_callback("dashboard"))
        header_layout.addWidget(cancel_btn)
        
        self.save_btn = QPushButton("Save Task")
        self.save_btn.setMinimumSize(120, 40)
        self.save_btn.clicked.connect(self.save_task)
        header_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(header_layout)
        
        # Scroll area for form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # Basic settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.task_name = QLineEdit()
        self.task_name.setPlaceholderText("Enter task name")
        basic_layout.addRow("Task Name:", self.task_name)
        
        self.task_active = QCheckBox("Active")
        self.task_active.setChecked(True)
        basic_layout.addRow("Status:", self.task_active)
        
        self.task_recurrence = QComboBox()
        self.task_recurrence.addItems(["One-time", "Daily", "Weekly", "Monthly"])
        basic_layout.addRow("Recurrence:", self.task_recurrence)
        
        self.task_next_run = QDateTimeEdit()
        self.task_next_run.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # Default to 1 hour from now
        self.task_next_run.setCalendarPopup(True)
        basic_layout.addRow("Next Run:", self.task_next_run)
        
        scroll_layout.addWidget(basic_group)
        
        # Tab widget for different sections
        tab_widget = QTabWidget()
        
        # Email settings tab
        email_tab = QWidget()
        email_layout = QVBoxLayout(email_tab)
        
        self.send_emails = QCheckBox("Send emails as part of this task")
        self.send_emails.setChecked(True)
        email_layout.addWidget(self.send_emails)
        
        email_settings = QGroupBox("Email Settings")
        email_settings.setEnabled(True)
        self.send_emails.toggled.connect(email_settings.setEnabled)
        
        email_form = QFormLayout(email_settings)
        
        self.email_subject = QLineEdit()
        self.email_subject.setPlaceholderText("Enter email subject")
        email_form.addRow("Subject:", self.email_subject)
        
        self.email_body = QTextEdit()
        self.email_body.setPlaceholderText("Enter email body (HTML supported)\n\nYou can use placeholders like {name}, {email}, {current_date}")
        self.email_body.setMinimumHeight(200)
        email_form.addRow("Body:", self.email_body)
        
        # Recipients section
        recipients_group = QGroupBox("Recipients")
        recipients_layout = QVBoxLayout(recipients_group)
        
        # Manual recipients
        manual_layout = QHBoxLayout()
        
        self.recipient_name = QLineEdit()
        self.recipient_name.setPlaceholderText("Name")
        manual_layout.addWidget(self.recipient_name)
        
        self.recipient_email = QLineEdit()
        self.recipient_email.setPlaceholderText("Email")
        manual_layout.addWidget(self.recipient_email)
        
        add_recipient_btn = QPushButton("Add")
        add_recipient_btn.clicked.connect(self.add_manual_recipient)
        manual_layout.addWidget(add_recipient_btn)
        
        recipients_layout.addLayout(manual_layout)
        
        self.recipients_list = QListWidget()
        self.recipients_list.setMaximumHeight(150)
        recipients_layout.addWidget(self.recipients_list)
        
        # Import from file
        import_layout = QHBoxLayout()
        
        self.recipient_file = QLineEdit()
        self.recipient_file.setPlaceholderText("No file selected")
        self.recipient_file.setReadOnly(True)
        import_layout.addWidget(self.recipient_file)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_recipient_file)
        import_layout.addWidget(browse_btn)
        
        recipients_layout.addLayout(import_layout)
        
        email_form.addRow("Recipients:", recipients_group)
        
        # Attachments
        attachments_layout = QHBoxLayout()
        
        self.attachment_path = QLineEdit()
        self.attachment_path.setPlaceholderText("No file selected")
        self.attachment_path.setReadOnly(True)
        attachments_layout.addWidget(self.attachment_path)
        
        browse_attachment_btn = QPushButton("Browse")
        browse_attachment_btn.clicked.connect(self.browse_attachment)
        attachments_layout.addWidget(browse_attachment_btn)
        
        email_form.addRow("Attachment:", attachments_layout)
        
        email_layout.addWidget(email_settings)
        tab_widget.addTab(email_tab, "Email Settings")
        
        # Response processing tab
        response_tab = QWidget()
        response_layout = QVBoxLayout(response_tab)
        
        self.process_responses = QCheckBox("Process email responses as part of this task")
        self.process_responses.setChecked(True)
        response_layout.addWidget(self.process_responses)
        
        response_settings = QGroupBox("Response Processing Settings")
        response_settings.setEnabled(True)
        self.process_responses.toggled.connect(response_settings.setEnabled)
        
        response_form = QFormLayout(response_settings)
        
        self.response_subject_filter = QLineEdit()
        self.response_subject_filter.setPlaceholderText("Filter by subject (leave empty to include all)")
        response_form.addRow("Subject Filter:", self.response_subject_filter)
        
        self.response_keywords = QLineEdit()
        self.response_keywords.setPlaceholderText("Comma-separated keywords (leave empty to include all)")
        response_form.addRow("Keywords:", self.response_keywords)
        
        self.response_days_back = QSpinBox()
        self.response_days_back.setMinimum(1)
        self.response_days_back.setMaximum(30)
        self.response_days_back.setValue(7)
        response_form.addRow("Days to Look Back:", self.response_days_back)
        
        self.ai_prompt = QTextEdit()
        self.ai_prompt.setPlaceholderText("Enter prompt for AI summarization")
        self.ai_prompt.setText("Summarize the following email responses and extract key information:")
        self.ai_prompt.setMaximumHeight(100)
        response_form.addRow("AI Prompt:", self.ai_prompt)
        
        response_layout.addWidget(response_settings)
        tab_widget.addTab(response_tab, "Response Processing")
        
        # Storage settings tab
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)
        
        storage_form = QFormLayout()
        
        self.storage_type = QComboBox()
        self.storage_type.addItems(["CSV", "Excel", "OneNote"])
        storage_form.addRow("Storage Type:", self.storage_type)
        
        storage_path_layout = QHBoxLayout()
        
        self.storage_path = QLineEdit()
        self.storage_path.setPlaceholderText("Enter storage path")
        storage_path_layout.addWidget(self.storage_path)
        
        browse_storage_btn = QPushButton("Browse")
        browse_storage_btn.clicked.connect(self.browse_storage_path)
        storage_path_layout.addWidget(browse_storage_btn)
        
        storage_form.addRow("Storage Path:", storage_path_layout)
        
        storage_layout.addLayout(storage_form)
        storage_layout.addStretch()
        
        tab_widget.addTab(storage_tab, "Storage Settings")
        
        scroll_layout.addWidget(tab_widget)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Connect signals
        self.send_emails.toggled.connect(self.update_ui_state)
        self.process_responses.toggled.connect(self.update_ui_state)
        self.storage_type.currentIndexChanged.connect(self.update_ui_state)
    
    def update_ui_state(self):
        """Update UI state based on current selections"""
        # Update storage path placeholder based on storage type
        storage_type = self.storage_type.currentText().lower()
        if storage_type == "csv":
            self.storage_path.setPlaceholderText("Enter path for CSV file (e.g., data/responses.csv)")
        elif storage_type == "excel":
            self.storage_path.setPlaceholderText("Enter path for Excel file (e.g., data/responses.xlsx)")
        elif storage_type == "onenote":
            self.storage_path.setPlaceholderText("Enter OneNote section/page (e.g., Work/Email Responses)")
    
    def add_manual_recipient(self):
        """Add a manual recipient to the list"""
        name = self.recipient_name.text().strip()
        email = self.recipient_email.text().strip()
        
        if not email:
            return
        
        item_text = f"{name} <{email}>" if name else email
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, {"name": name, "email": email})
        
        self.recipients_list.addItem(item)
        
        # Clear input fields
        self.recipient_name.clear()
        self.recipient_email.clear()
    
    def browse_recipient_file(self):
        """Browse for recipient file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Recipients File", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            self.recipient_file.setText(file_path)
    
    def browse_attachment(self):
        """Browse for attachment file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Attachment", "", "All Files (*.*)"
        )
        
        if file_path:
            self.attachment_path.setText(file_path)
    
    def browse_storage_path(self):
        """Browse for storage path"""
        storage_type = self.storage_type.currentText().lower()
        
        if storage_type in ["csv", "excel"]:
            file_filter = "CSV Files (*.csv)" if storage_type == "csv" else "Excel Files (*.xlsx *.xls)"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Select Storage Location", "", file_filter
            )
            
            if file_path:
                self.storage_path.setText(file_path)
        else:
            # For OneNote, just show a directory dialog as a hint
            dir_path = QFileDialog.getExistingDirectory(
                self, "Select Storage Directory (for reference only)"
            )
            
            if dir_path:
                self.storage_path.setText("Section/Page")
    
    def load_task(self, task_id):
        """Load an existing task for editing"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return
        
        self.current_task_id = task_id
        self.title_label.setText(f"Edit Task: {task.get('name', '')}")
        
        # Basic settings
        self.task_name.setText(task.get("name", ""))
        self.task_active.setChecked(task.get("active", True))
        
        recurrence = task.get("recurrence", "once")
        recurrence_map = {
            "once": "One-time",
            "daily": "Daily",
            "weekly": "Weekly",
            "monthly": "Monthly"
        }
        self.task_recurrence.setCurrentText(recurrence_map.get(recurrence, "One-time"))
        
        next_run = datetime.datetime.fromisoformat(task.get("next_run", datetime.datetime.now().isoformat()))
        self.task_next_run.setDateTime(QDateTime(
            next_run.year, next_run.month, next_run.day,
            next_run.hour, next_run.minute, next_run.second
        ))
        
        # Email settings
        self.send_emails.setChecked(task.get("send_emails", False))
        self.email_subject.setText(task.get("email_subject", ""))
        self.email_body.setText(task.get("email_body", ""))
        
        # Recipients
        self.recipients_list.clear()
        for recipient in task.get("manual_recipients", []):
            name = recipient.get("name", "")
            email = recipient.get("email", "")
            
            item_text = f"{name} <{email}>" if name else email
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, {"name": name, "email": email})
            
            self.recipients_list.addItem(item)
        
        self.recipient_file.setText(task.get("recipient_file", ""))
        self.attachment_path.setText(task.get("email_attachments", [""])[0] if task.get("email_attachments") else "")
        
        # Response processing
        self.process_responses.setChecked(task.get("process_responses", False))
        self.response_subject_filter.setText(task.get("response_subject_filter", ""))
        self.response_keywords.setText(", ".join(task.get("response_keywords", [])))
        self.response_days_back.setValue(task.get("response_days_back", 7))
        self.ai_prompt.setText(task.get("ai_prompt", "Summarize the following email responses and extract key information:"))
        
        # Storage settings
        storage_type = task.get("storage_type", "csv").lower()
        storage_type_map = {
            "csv": "CSV",
            "excel": "Excel",
            "onenote": "OneNote"
        }
        self.storage_type.setCurrentText(storage_type_map.get(storage_type, "CSV"))
        self.storage_path.setText(task.get("storage_path", ""))
        
        # Update UI state
        self.update_ui_state()
    
    def clear_form(self):
        """Clear the form for a new task"""
        self.current_task_id = None
        self.title_label.setText("Create New Task")
        
        # Basic settings
        self.task_name.clear()
        self.task_active.setChecked(True)
        self.task_recurrence.setCurrentText("One-time")
        self.task_next_run.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        
        # Email settings
        self.send_emails.setChecked(True)
        self.email_subject.clear()
        self.email_body.clear()
        
        # Recipients
        self.recipients_list.clear()
        self.recipient_name.clear()
        self.recipient_email.clear()
        self.recipient_file.clear()
        self.attachment_path.clear()
        
        # Response processing
        self.process_responses.setChecked(True)
        self.response_subject_filter.clear()
        self.response_keywords.clear()
        self.response_days_back.setValue(7)
        self.ai_prompt.setText("Summarize the following email responses and extract key information:")
        
        # Storage settings
        self.storage_type.setCurrentText("CSV")
        self.storage_path.clear()
        
        # Update UI state
        self.update_ui_state()
    
    def save_task(self):
        """Save the task"""
        # Validate form
        task_name = self.task_name.text().strip()
        if not task_name:
            return
        
        # Create task dictionary
        task = {
            "id": self.current_task_id if self.current_task_id else str(uuid.uuid4()),
            "name": task_name,
            "active": self.task_active.isChecked(),
            "recurrence": self.task_recurrence.currentText().lower(),
            "next_run": self.task_next_run.dateTime().toPython().isoformat(),
            
            # Email settings
            "send_emails": self.send_emails.isChecked(),
            "email_subject": self.email_subject.text(),
            "email_body": self.email_body.toPlainText(),
            
            # Recipients
            "manual_recipients": [
                self.recipients_list.item(i).data(Qt.UserRole)
                for i in range(self.recipients_list.count())
            ],
            "recipient_file": self.recipient_file.text() if self.recipient_file.text() else None,
            "email_attachments": [self.attachment_path.text()] if self.attachment_path.text() else [],
            
            # Response processing
            "process_responses": self.process_responses.isChecked(),
            "response_subject_filter": self.response_subject_filter.text(),
            "response_keywords": [
                keyword.strip() for keyword in self.response_keywords.text().split(",") if keyword.strip()
            ],
            "response_days_back": self.response_days_back.value(),
            "ai_prompt": self.ai_prompt.toPlainText(),
            
            # Storage settings
            "storage_type": self.storage_type.currentText().lower(),
            "storage_path": self.storage_path.text()
        }
        
        # Save task
        self.task_manager.save_task(task)
        
        # Navigate back to dashboard
        self.navigate_callback("dashboard")