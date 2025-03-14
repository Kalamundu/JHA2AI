

# JHA2AI Project

## Overview

JHA2AI is a Flask-based AI assistant application that interfaces with the OpenRouter API to facilitate natural language processing and user interaction. The project allows users to send prompts and receive responses using a customizable AI model.

## Features

- Web-based interface for user interactions
- Integration with OpenRouter API for AI-based responses
- Customizable configuration using JSON
- Real-time interaction via WebSockets

## Requirements

- Python 3.11 or higher
- Flask
- Flask-SocketIO
- Flask-CORS
- Requests

## Setup Instructions

### 1. Clone the Repository

Clone the repository to your local machine or Replit workspace:
```bash
git clone <your-repo-url>

2. Install Dependencies

Install the required packages:

pip install -r requirements.txt

3. Configuration

Create or modify the

file in the JHA2AI/backend directory with the following structure:

{
    "api_key": "YOUR_OPENROUTER_API_KEY",
    "huggingface_api_key": "YOUR_HUGGINGFACE_API_KEY",
    "default_model": "mistralai/mistral-7b-instruct",
    "default_persona": "autonomous assistant",
    "personas": {
        "autonomous assistant": "You are an advanced AI assistant."
    },
    "working_directory": "./jha2_workspace",
    "allowed_commands": [
        "ls", "pwd", "cat", "echo", "mkdir", "touch", "rm", "cp",
        "mv", "python", "node", "git", "grep", "find"
    ]
}

4. Run the Application

Start the Flask application:

python -m flask run --host=0.0.0.0 --port=3000

5. Access the Application

Navigate to http://<your_ip_or_domain>:3000/ in your web browser.
Usage

    Interacting with the AI:
    Send text prompts through the input box on the main page. The AI will respond in real-time.

    Error Handling:
    Ensure to check console logs for any errors encountered while running the application.

API Reference

The application interacts with the OpenRouter API to fetch AI responses based on user prompts. More information about the API endpoints can be found in the OpenRouter API Documentation.
Contributing

Contributions are welcome! Please follow these steps to contribute:

    Fork the repository.
    Create your feature branch (git checkout -b feature/NewFeature).
    Commit your changes (git commit -m 'Add some feature').
    Push to the branch (git push origin feature/NewFeature).
    Open a Pull Request.

License

This project is licensed under the MIT License.
