# app.py
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any

# Third-party imports
from flask import Flask, render_template, send_from_directory, abort
from flask_socketio import SocketIO
from flask_cors import CORS
from backend.jha2_ai import JHA2AI
from backend.utils import secure_path, validate_file_type

# Load configuration from config.json
def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path) as f:
        return json.load(f)

config = load_config(os.path.join(os.path.dirname(__file__), 'config.json'))

app = Flask(__name__,
            static_folder='../frontend/static',
            template_folder='../templates')

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Configure logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


def jha2_callback(update_type: str, data: Any) -> None:
    # Callback function implementation remains unchanged
    pass

# Initialize JHA2AI with the callback
jha2 = JHA2AI(callback=jha2_callback)

@app.route("/")
def index() -> str:
    """Render the main page."""
    try:
        return render_template("index.html")
    except Exception as e:
        app.logger.error(f"Error rendering template: {e}")
        abort(500)

@app.route("/download/<filename>")
def download_file(filename: str) -> Any:
    """Handle file downloads with proper validation."""
    try:
        if not validate_file_type(filename):
            abort(400, "Invalid file type")

        safe_path = secure_path(filename, jha2)
        if not safe_path or not os.path.exists(safe_path):
            abort(404)

        return send_from_directory(jha2.state['working_directory'], filename)
    except Exception as e:
        app.logger.error(f"Error downloading file: {e}")
        abort(500)

@socketio.on('connect')
def handle_connect() -> None:
    """Handle client connection."""
    app.logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect() -> None:
    """Handle client disconnection."""
    app.logger.info('Client disconnected')

@socketio.on('user_input')
def handle_user_input(data: Dict[str, str]) -> None:
    """Process user input received via websocket."""
    try:
        if not data or 'text' not in data:
            raise ValueError("Invalid input data")

        user_text = data['text'].strip()
        if not user_text:
            raise ValueError("Empty input")

        jha2.process_input(user_text)

    except ValueError as e:
        error_msg = f"Validation error: {str(e)}"
        app.logger.warning(error_msg)
        socketio.emit('message', {'type': 'warning', 'text': error_msg})
    except Exception as e:
        error_msg = f"Error processing input: {str(e)}"
        app.logger.error(error_msg)
        socketio.emit('message', {'type': 'error', 'text': error_msg})
    finally:
        socketio.sleep(0)  # Allow other events to be processed

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)