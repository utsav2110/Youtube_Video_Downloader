# YouTube Video Downloader

This is a Django-based YouTube Video Downloader application.

## Features
- Download video from YouTube.
- Convert YouTube videos to audio (MP3).
- Download Audio Only from Youtube Video.
- Progress tracking using Django's caching.

## Setup

### Virtual Environment Setup
1. Create a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   
   # Linux/MacOS
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/MacOS
   source venv/bin/activate
   ```

### Project Setup
1. Install dependencies (with activated virtual environment):
   ```bash
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage
Visit `http://127.0.0.1:8000/download/` in your browser to use the application.

## Development Notes
- Always activate the virtual environment before running the project:
  ```bash
  # Windows
  .\venv\Scripts\activate
  
  # Linux/MacOS
  source venv/bin/activate
  ```
- To deactivate the virtual environment:
  ```bash
  deactivate
  ```
