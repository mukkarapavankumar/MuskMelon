from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFormLayout, QGroupBox, QCheckBox,
    QSpinBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import os
import json
import ollama
from typing import Callable, Dict, Any

class SettingsWidget(QWidget):
    def __init__(self, navigate_callback):
        super().__init__()
        self.navigate_callback = navigate_callback
        self.settings_file = "data/settings.json"
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the settings UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Settings")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setMinimumSize(150, 40)
        back_btn.clicked.connect(lambda: self.navigate_callback("dashboard"))
        header_layout.addWidget(back_btn)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setMinimumSize(150, 40)
        save_btn.clicked.connect(self.save_settings)
        header_layout.addWidget(save_btn)
        
        main_layout.addLayout(header_layout)
        
        # AI settings
        ai_group = QGroupBox("AI Settings")
        ai_layout = QFormLayout(ai_group)
        
        self.ai_model = QComboBox()
        self.update_model_list()  # Fetch available models from Ollama
        ai_layout.addRow("AI Model:", self.ai_model)
        
        main_layout.addWidget(ai_group)
        
        # Email settings
        email_group = QGroupBox("Email Settings")
        email_layout = QFormLayout(email_group)
        
        self.default_signature = QLineEdit()
        self.default_signature.setPlaceholderText("Enter default email signature (HTML supported)")
        email_layout.addRow("Default Signature:", self.default_signature)
        
        self.auto_bcc = QLineEdit()
        self.auto_bcc.setPlaceholderText("Enter email address to BCC on all outgoing emails")
        email_layout.addRow("Auto BCC:", self.auto_bcc)
        
        main_layout.addWidget(email_group)
        
        # Storage settings
        storage_group = QGroupBox("Storage Settings")
        storage_layout = QFormLayout(storage_group)
        
        storage_dir_layout = QHBoxLayout()
        
        self.default_storage_dir = QLineEdit()
        self.default_storage_dir.setPlaceholderText("Enter default storage directory")
        storage_dir_layout.addWidget(self.default_storage_dir)
        
        browse_dir_btn = QPushButton("Browse")
        browse_dir_btn.clicked.connect(self.browse_storage_dir)
        storage_dir_layout.addWidget(browse_dir_btn)
        
        storage_layout.addRow("Default Storage Directory:", storage_dir_layout)
        
        self.auto_backup = QCheckBox("Enable automatic backups")
        storage_layout.addRow("Backup:", self.auto_backup)
        
        self.backup_interval = QSpinBox()
        self.backup_interval.setMinimum(1)
        self.backup_interval.setMaximum(30)
        self.backup_interval.setValue(7)
        self.backup_interval.setSuffix(" days")
        storage_layout.addRow("Backup Interval:", self.backup_interval)
        
        main_layout.addWidget(storage_group)
        
        # Application settings
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout(app_group)
        
        self.run_at_startup = QCheckBox("Run application at system startup")
        app_layout.addRow("Startup:", self.run_at_startup)
        
        self.minimize_to_tray = QCheckBox("Minimize to system tray when closed")
        self.minimize_to_tray.setChecked(True)
        app_layout.addRow("System Tray:", self.minimize_to_tray)
        
        main_layout.addWidget(app_group)
        
        main_layout.addStretch()
    
    def update_model_list(self):
        """Fetch and update the list of available models from Ollama"""
        try:
            # Clear existing items
            self.ai_model.clear()
            
            # Get list of models from Ollama
            models = ollama.list()
            
            # Add models to combobox
            for model in models['models']:
                self.ai_model.addItem(model['name'])
                
            if self.ai_model.count() == 0:
                self.ai_model.addItem("No models found")
                
        except Exception as e:
            print(f"Error fetching models from Ollama: {e}")
            self.ai_model.addItem("Error fetching models")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
                
                # AI settings
                self.ai_model.setCurrentText(settings.get("ai_model", ""))
                
                # Email settings
                self.default_signature.setText(settings.get("default_signature", ""))
                self.auto_bcc.setText(settings.get("auto_bcc", ""))
                
                # Storage settings
                self.default_storage_dir.setText(settings.get("default_storage_dir", ""))
                self.auto_backup.setChecked(settings.get("auto_backup", False))
                self.backup_interval.setValue(settings.get("backup_interval", 7))
                
                # Application settings
                self.run_at_startup.setChecked(settings.get("run_at_startup", False))
                self.minimize_to_tray.setChecked(settings.get("minimize_to_tray", True))
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            settings = {
                # AI settings
                "ai_model": self.ai_model.currentText(),
                
                # Email settings
                "default_signature": self.default_signature.text(),
                "auto_bcc": self.auto_bcc.text(),
                
                # Storage settings
                "default_storage_dir": self.default_storage_dir.text(),
                "auto_backup": self.auto_backup.isChecked(),
                "backup_interval": self.backup_interval.value(),
                
                # Application settings
                "run_at_startup": self.run_at_startup.isChecked(),
                "minimize_to_tray": self.minimize_to_tray.isChecked()
            }
            
            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=2)
            
            # Navigate back to dashboard
            self.navigate_callback("dashboard")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def browse_storage_dir(self):
        """Browse for storage directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Default Storage Directory"
        )
        
        if dir_path:
            self.default_storage_dir.setText(dir_path)