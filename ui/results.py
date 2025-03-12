from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QSplitter, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

import datetime
from typing import Callable, Dict, List, Any

class ResultsWidget(QWidget):
    def __init__(self, task_manager, navigate_callback):
        super().__init__()
        self.task_manager = task_manager
        self.navigate_callback = navigate_callback
        self.current_task = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the results viewer UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Task Results")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setMinimumSize(150, 40)
        back_btn.clicked.connect(lambda: self.navigate_callback("dashboard"))
        header_layout.addWidget(back_btn)
        
        main_layout.addLayout(header_layout)
        
        # Splitter for results table and detail view
        splitter = QSplitter(Qt.Vertical)
        
        # Results table
        results_frame = QFrame()
        results_layout = QVBoxLayout(results_frame)
        results_layout.setContentsMargins(0, 0, 0, 0)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels([
            "Date", "Emails Processed", "Summary"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.selectionModel().selectionChanged.connect(self._show_details)
        
        results_layout.addWidget(self.results_table)
        splitter.addWidget(results_frame)
        
        # Detail view
        detail_frame = QFrame()
        detail_layout = QVBoxLayout(detail_frame)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        
        detail_label = QLabel("Details")
        detail_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        detail_layout.addWidget(detail_label)
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text)
        
        splitter.addWidget(detail_frame)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 400])
        main_layout.addWidget(splitter)
    
    def load_results(self, task: Dict[str, Any]):
        """Load results for a task"""
        self.current_task = task
        self.title_label.setText(f"Results: {task.get('name', '')}")
        
        # Get results from storage
        storage_path = task.get("storage_path", f"data/summaries/{task.get('id')}")
        results = self.task_manager.storage_handler.get_results(storage_path)
        
        # Update results table
        self.results_table.setRowCount(0)
        for i, result in enumerate(results):
            self.results_table.insertRow(i)
            
            # Date
            timestamp = datetime.datetime.fromisoformat(result["timestamp"])
            date_item = QTableWidgetItem(timestamp.strftime("%Y-%m-%d %H:%M"))
            self.results_table.setItem(i, 0, date_item)
            
            # Emails processed
            emails_item = QTableWidgetItem(str(len(result["emails"])))
            self.results_table.setItem(i, 1, emails_item)
            
            # Summary
            summary_item = QTableWidgetItem(result["summary"][:100] + "..." if len(result["summary"]) > 100 else result["summary"])
            self.results_table.setItem(i, 2, summary_item)
            
            # Store full result data
            for col in range(3):
                self.results_table.item(i, col).setData(Qt.UserRole, result)
    
    def _show_details(self):
        """Show details for selected result"""
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            return
        
        # Get full result data
        result = selected_items[0].data(Qt.UserRole)
        
        # Format details
        details = []
        details.append(f"Date: {datetime.datetime.fromisoformat(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        details.append(f"\nSummary:\n{result['summary']}")
        details.append("\nProcessed Emails:")
        
        for i, email in enumerate(result["emails"], 1):
            details.append(f"\nEmail {i}:")
            details.append(f"From: {email['sender']} <{email['sender_email']}>")
            details.append(f"Subject: {email['subject']}")
            details.append(f"Date: {email['received_time']}")
            details.append(f"Content:\n{email['body']}")
            details.append("-" * 50)
        
        self.detail_text.setText("\n".join(details)) 