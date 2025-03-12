import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, 
    QSystemTrayIcon, QMenu, QStyle
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QIcon, QAction
from dotenv import load_dotenv

from ui.dashboard import DashboardWidget
from ui.task_config import TaskConfigWidget
from ui.settings import SettingsWidget
from ui.logs import LogsWidget
from ui.results import ResultsWidget
from core.task_manager import TaskManager
from core.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Outlook Email Automation")
        self.setMinimumSize(1200, 800)
        
        # Initialize task manager
        self.task_manager = TaskManager()
        
        # Create stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        
        # Create widgets for different screens
        self.dashboard = DashboardWidget(self.task_manager, self.navigate_to)
        self.task_config = TaskConfigWidget(self.task_manager, self.navigate_to)
        self.settings = SettingsWidget(self.navigate_to)
        self.logs = LogsWidget(self.navigate_to)
        self.results = ResultsWidget(self.task_manager, self.navigate_to)
        
        # Add widgets to stacked widget
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.task_config)
        self.stacked_widget.addWidget(self.settings)
        self.stacked_widget.addWidget(self.logs)
        self.stacked_widget.addWidget(self.results)
        
        # Set central widget
        self.setCentralWidget(self.stacked_widget)
        
        # Set up timer for background task checking
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_tasks)
        self.timer.start(60000)  # Check every minute
        
        # Set up system tray
        self.setup_system_tray()
        
        # Start with dashboard
        self.navigate_to("dashboard")
    
    def setup_system_tray(self):
        """Set up system tray icon and menu"""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_icon.setToolTip("Outlook Email Automation")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Add actions
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide_window)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Connect double click to show window
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """Show and restore the window"""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
    
    def hide_window(self):
        """Hide the window to system tray"""
        self.hide()
    
    def quit_application(self):
        """Quit the application"""
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.settings.minimize_to_tray.isChecked():
            event.ignore()
            self.hide_window()
            self.tray_icon.showMessage(
                "Outlook Email Automation",
                "Application is still running in the background.",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.accept()
    
    def navigate_to(self, screen, data=None):
        """Navigate to a specific screen"""
        if screen == "dashboard":
            self.dashboard.refresh_data()
            self.stacked_widget.setCurrentWidget(self.dashboard)
        elif screen == "task_config":
            if data:  # task_id
                self.task_config.load_task(data)
            else:
                self.task_config.clear_form()
            self.stacked_widget.setCurrentWidget(self.task_config)
        elif screen == "settings":
            self.stacked_widget.setCurrentWidget(self.settings)
        elif screen == "logs":
            self.logs.refresh_logs()
            self.stacked_widget.setCurrentWidget(self.logs)
        elif screen == "results":
            if data:  # task data
                self.results.load_results(data)
                self.stacked_widget.setCurrentWidget(self.results)
    
    def check_tasks(self):
        """Check for tasks that need to be executed"""
        self.task_manager.process_due_tasks()
        # Refresh dashboard if it's the current widget
        if self.stacked_widget.currentWidget() == self.dashboard:
            self.dashboard.refresh_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed
    
    # Set application style
    app.setStyle("Fusion")
    
    # Load stylesheet
    try:
        style_path = resource_path('ui/styles/style.qss')
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        logger.error(f"Failed to load stylesheet: {e}")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())