from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QSpinBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import datetime
from typing import Callable, Dict, List, Any

class LogsWidget(QWidget):
    def __init__(self, navigate_callback):
        super().__init__()
        self.navigate_callback = navigate_callback
        
        # Get task manager from parent
        self.task_manager = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the logs UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Activity Logs")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setMinimumSize(150, 40)
        back_btn.clicked.connect(lambda: self.navigate_callback("dashboard"))
        header_layout.addWidget(back_btn)
        
        main_layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_form = QFormLayout()
        filter_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        self.log_level_filter = QComboBox()
        self.log_level_filter.addItems(["All Levels", "Info", "Warning", "Error"])
        self.log_level_filter.currentIndexChanged.connect(self.apply_filters)
        filter_form.addRow("Level:", self.log_level_filter)
        
        self.log_limit = QSpinBox()
        self.log_limit.setMinimum(10)
        self.log_limit.setMaximum(1000)
        self.log_limit.setValue(100)
        self.log_limit.setSingleStep(10)
        self.log_limit.valueChanged.connect(self.apply_filters)
        filter_form.addRow("Limit:", self.log_limit)
        
        filter_layout.addLayout(filter_form)
        filter_layout.addStretch()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_logs)
        filter_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels([
            "Timestamp", "Level", "Message"
        ])
        self.logs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.logs_table.verticalHeader().setVisible(False)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.logs_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.logs_table)
    
    def refresh_logs(self):
        """Refresh logs data"""
        if not self.task_manager:
            # Get task manager from parent
            parent = self.parent()
            while parent and not hasattr(parent, "task_manager"):
                parent = parent.parent()
            
            if parent and hasattr(parent, "task_manager"):
                self.task_manager = parent.task_manager
            else:
                return
        
        self.apply_filters()
    
    def apply_filters(self):
        """Apply filters to logs"""
        if not self.task_manager:
            return
            
        # Get logs
        logs = self.task_manager.get_logs(1000)  # Get a large number to filter
        
        # Apply level filter
        level_filter = self.log_level_filter.currentText().lower()
        if level_filter != "all levels":
            logs = [log for log in logs if log.get("level", "").lower() == level_filter]
        
        # Apply limit
        limit = self.log_limit.value()
        logs = logs[:limit]
        
        # Update logs table
        self.logs_table.setRowCount(0)
        for i, log in enumerate(logs):
            self.logs_table.insertRow(i)
            
            # Timestamp
            timestamp = datetime.datetime.fromisoformat(log.get("timestamp", datetime.datetime.now().isoformat()))
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            timestamp_item = QTableWidgetItem(timestamp_str)
            self.logs_table.setItem(i, 0, timestamp_item)
            
            # Level
            level = log.get("level", "info")
            level_item = QTableWidgetItem(level.upper())
            if level == "error":
                level_item.setForeground(QColor("#dc2626"))
            elif level == "warning":
                level_item.setForeground(QColor("#d97706"))
            else:
                level_item.setForeground(QColor("#059669"))
            self.logs_table.setItem(i, 1, level_item)
            
            # Message
            message_item = QTableWidgetItem(log.get("message", ""))
            self.logs_table.setItem(i, 2, message_item)