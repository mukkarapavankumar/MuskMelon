# Windows Email Automation Application

A desktop application for automating email scheduling, response summarization, and data storage using Microsoft Outlook COM automation.

## Features

### Email Scheduling
- Schedule emails to be sent at specific times
- Create email templates with placeholders
- Add recipients manually or import from CSV/Excel files
- Attach files to emails

### Response Summarization
- Collect and filter email responses
- Summarize responses using AI (Ollama)
- Customize AI prompts for summarization

### Data Storage
- Store summarized responses in CSV, Excel, or OneNote
- Organize data with customizable storage paths
- Automatic backups

## Requirements

- Windows operating system
- Microsoft Outlook installed
- Python 3.8 or higher

## Installation

1. Clone or download this repository
2. Install required dependencies:

```
pip install -r requirements.txt
```

3. Run the application:

```
python main.py
```

## Usage

### Creating a Task

1. Click "Create New Task" on the dashboard
2. Fill in the basic settings (name, recurrence, next run time)
3. Configure email settings if sending emails
4. Set up response processing if needed
5. Choose storage options for summarized data
6. Click "Save Task"

### Managing Tasks

- View all tasks on the dashboard
- Edit or delete tasks as needed
- Monitor task status and execution logs

### Settings

- Configure AI model for summarization
- Set default email signature
- Customize storage locations
- Configure application behavior

## Development

### Project Structure

- `main.py`: Application entry point
- `core/`: Core functionality modules
  - `task_manager.py`: Task management and execution
  - `outlook_handler.py`: Outlook COM integration
  - `ai_summarizer.py`: AI-powered email summarization
  - `storage_handler.py`: Data storage in various formats
  - `logger.py`: Logging configuration
- `ui/`: User interface components
  - `dashboard.py`: Main dashboard
  - `task_config.py`: Task configuration screen
  - `logs.py`: Log viewer
  - `settings.py`: Application settings
  - `styles/`: UI styling

### Dependencies

- PySide6: Qt-based UI framework
- pywin32: Windows COM automation
- pandas: Data manipulation
- openpyxl: Excel file handling
- ollama: AI model integration

## License

This project is licensed under the MIT License - see the LICENSE file for details.