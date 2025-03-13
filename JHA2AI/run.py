"""
Main entry point for the application.
Handles graceful shutdown and server initialization.
"""
import os
import signal
import sys
import logging
from typing import Any  # Add this import
from backend.app import app, socketio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

def signal_handler(sig: int, frame: Any) -> None:
    """Handle shutdown signals gracefully."""
    logging.info('Shutting down gracefully...')
    sys.exit(0)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize eventlet
        import eventlet
        eventlet.monkey_patch()
        
        # Run the server
        socketio.run(app, host='0.0.0.0', port=3000, debug=False, use_reloader=False)
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)