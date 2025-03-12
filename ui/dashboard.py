from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QStyle
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont, QColor

import datetime
from typing import Callable, Dict, List, Any

class DashboardWidget(QWidget):
    def __init__(self, task_manager, navigate_callback):
        super().__init__()
        self.task_manager = task_manager
        self.navigate_callback = navigate_callback
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Email Automation Dashboard")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        new_task_btn = QPushButton("Create New Task")
        new_task_btn.setMinimumSize(150, 40)
        new_task_btn.clicked.connect(lambda: self.navigate_callback("task_config"))
        header_layout.addWidget(new_task_btn)
        
        logs_btn = QPushButton("View Logs")
        logs_btn.setMinimumSize(150, 40)
        logs_btn.clicked.connect(lambda: self.navigate_callback("logs"))
        header_layout.addWidget(logs_btn)
        
        settings_btn = QPushButton("Settings")
        settings_btn.setMinimumSize(150, 40)
        settings_btn.clicked.connect(lambda: self.navigate_callback("settings"))
        header_layout.addWidget(settings_btn)
        
        main_layout.addLayout(header_layout)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        # Active tasks card
        active_tasks_card = QFrame()
        active_tasks_card.setFrameShape(QFrame.StyledPanel)
        active_tasks_card.setStyleSheet("background-color: #f0f7ff; border-radius: 10px;")
        active_tasks_layout = QVBoxLayout(active_tasks_card)
        
        active_tasks_title = QLabel("Active Tasks")
        active_tasks_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        active_tasks_layout.addWidget(active_tasks_title)
        
        self.active_tasks_count = QLabel("0")
        self.active_tasks_count.setStyleSheet("font-size: 32px; font-weight: bold; color: #2563eb;")
        self.active_tasks_count.setAlignment(Qt.AlignCenter)
        active_tasks_layout.addWidget(self.active_tasks_count)
        
        stats_layout.addWidget(active_tasks_card)
        
        # Emails sent card
        emails_sent_card = QFrame()
        emails_sent_card.setFrameShape(QFrame.StyledPanel)
        emails_sent_card.setStyleSheet("background-color: #f0fff4; border-radius: 10px;")
        emails_sent_layout = QVBoxLayout(emails_sent_card)
        
        emails_sent_title = QLabel("Emails Sent (Last 7 Days)")
        emails_sent_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        emails_sent_layout.addWidget(emails_sent_title)
        
        self.emails_sent_count = QLabel("0")
        self.emails_sent_count.setStyleSheet("font-size: 32px; font-weight: bold; color: #059669;")
        self.emails_sent_count.setAlignment(Qt.AlignCenter)
        emails_sent_layout.addWidget(self.emails_sent_count)
        
        stats_layout.addWidget(emails_sent_card)
        
        # Responses processed card
        responses_card = QFrame()
        responses_card.setFrameShape(QFrame.StyledPanel)
        responses_card.setStyleSheet("background-color: #fff0f6; border-radius: 10px;")
        responses_layout = QVBoxLayout(responses_card)
        
        responses_title = QLabel("Responses Processed (Last 7 Days)")
        responses_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        responses_layout.addWidget(responses_title)
        
        self.responses_count = QLabel("0")
        self.responses_count.setStyleSheet("font-size: 32px; font-weight: bold; color: #db2777;")
        self.responses_count.setAlignment(Qt.AlignCenter)
        responses_layout.addWidget(self.responses_count)
        
        stats_layout.addWidget(responses_card)
        
        main_layout.addLayout(stats_layout)
        
        # Tasks table
        tasks_label = QLabel("Scheduled Tasks")
        tasks_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(tasks_label)
        
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(5)
        self.tasks_table.setHorizontalHeaderLabels([
            "Task Name", "Status", "Next Run", "Recurrence", "Actions"
        ])
        self.tasks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tasks_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tasks_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tasks_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tasks_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.tasks_table.setColumnWidth(4, 90)
        self.tasks_table.verticalHeader().setVisible(False)
        self.tasks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.tasks_table)
        
        # Recent logs
        logs_label = QLabel("Recent Activity")
        logs_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(logs_label)
        
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
        
        # Refresh data
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh dashboard data"""
        # Get tasks
        tasks = self.task_manager.get_all_tasks()
        
        # Update active tasks count
        active_tasks = [task for task in tasks if task.get("active", True)]
        self.active_tasks_count.setText(str(len(active_tasks)))
        
        # Update tasks table
        self.tasks_table.setRowCount(0)
        for i, task in enumerate(tasks):
            self.tasks_table.insertRow(i)
            
            # Task name
            name_item = QTableWidgetItem(task.get("name", "Unnamed Task"))
            self.tasks_table.setItem(i, 0, name_item)
            
            # Status
            status = "Active" if task.get("active", True) else "Inactive"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor("#059669" if status == "Active" else "#6b7280"))
            self.tasks_table.setItem(i, 1, status_item)
            
            # Next run
            next_run = datetime.datetime.fromisoformat(task.get("next_run", datetime.datetime.now().isoformat()))
            next_run_str = next_run.strftime("%Y-%m-%d %H:%M")
            next_run_item = QTableWidgetItem(next_run_str)
            self.tasks_table.setItem(i, 2, next_run_item)
            
            # Recurrence
            recurrence = task.get("recurrence", "once")
            recurrence_map = {
                "once": "One-time",
                "daily": "Daily",
                "weekly": "Weekly",
                "monthly": "Monthly"
            }
            recurrence_item = QTableWidgetItem(recurrence_map.get(recurrence, recurrence))
            self.tasks_table.setItem(i, 3, recurrence_item)
            
            # Actions column with buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(4)
            actions_layout.setAlignment(Qt.AlignCenter)
            
            # Run Now button
            run_btn = QPushButton()
            run_btn.setIcon(QIcon(self.style().standardPixmap(QStyle.SP_MediaPlay)))
            run_btn.setIconSize(QSize(12, 12))
            run_btn.setFixedSize(16, 16)
            run_btn.setToolTip("Run Now")
            run_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #dcfce7;
                    border-radius: 4px;
                }
            """)
            run_btn.clicked.connect(lambda checked=False, t=task.get("id"): self._run_task_now(t))
            actions_layout.addWidget(run_btn)
            
            # View Results button
            results_btn = QPushButton()
            results_btn.setIcon(QIcon(self.style().standardPixmap(QStyle.SP_FileDialogContentsView)))
            results_btn.setIconSize(QSize(12, 12))
            results_btn.setFixedSize(16, 16)
            results_btn.setToolTip("View Results")
            results_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #dbeafe;
                    border-radius: 4px;
                }
            """)
            results_btn.clicked.connect(lambda checked=False, t=task: self.navigate_callback("results", t))
            actions_layout.addWidget(results_btn)
            
            # Edit button
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon(self.style().standardPixmap(QStyle.SP_FileIcon)))
            edit_btn.setIconSize(QSize(12, 12))
            edit_btn.setFixedSize(16, 16)
            edit_btn.setToolTip("Edit Task")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #e5e7eb;
                    border-radius: 4px;
                }
            """)
            edit_btn.clicked.connect(lambda checked=False, t=task.get("id"): self.navigate_callback("task_config", t))
            actions_layout.addWidget(edit_btn)
            
            # Delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon(self.style().standardPixmap(QStyle.SP_TrashIcon)))
            delete_btn.setIconSize(QSize(12, 12))
            delete_btn.setFixedSize(16, 16)
            delete_btn.setToolTip("Delete Task")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 2px;
                }
                QPushButton:hover {
                    background-color: #fee2e2;
                    border-radius: 4px;
                }
            """)
            delete_btn.clicked.connect(lambda checked=False, t=task.get("id"): self._delete_task(t))
            actions_layout.addWidget(delete_btn)
            
            self.tasks_table.setCellWidget(i, 4, actions_widget)
        
        # Get logs
        logs = self.task_manager.get_logs(10)  # Get 10 most recent logs
        
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
        
        # Update email stats
        email_logs = [log for log in self.task_manager.get_logs() 
                     if "Email sent to" in log.get("message", "")
                     and self._is_within_days(log.get("timestamp", ""), 7)]
        self.emails_sent_count.setText(str(len(email_logs)))
        
        # Update response stats
        response_logs = [log for log in self.task_manager.get_logs() 
                        if "Processed and stored" in log.get("message", "")
                        and self._is_within_days(log.get("timestamp", ""), 7)]
        self.responses_count.setText(str(len(response_logs)))
    
    def _delete_task(self, task_id):
        """Delete a task"""
        self.task_manager.delete_task(task_id)
        self.refresh_data()
    
    def _is_within_days(self, timestamp_str, days):
        """Check if a timestamp is within the specified number of days"""
        if not timestamp_str:
            return False
            
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
            now = datetime.datetime.now()
            delta = now - timestamp
            return delta.days < days
        except:
            return False
    
    def _run_task_now(self, task_id):
        """Execute a task immediately"""
        task = self.task_manager.get_task(task_id)
        if task:
            self.task_manager._execute_task(task)
            self.refresh_data()