# utils.py
import os
from typing import Any, Optional

def secure_path(filename: str, jha2_instance: Any) -> Optional[str]:
    """
    Ensures a file path is within the allowed working directory.

    Args:
        filename (str): Name of the file to check
        jha2_instance: JHA2 instance containing working directory info

    Returns:
        Optional[str]: Safe path if valid, None otherwise
    """
    base_dir = os.path.abspath(jha2_instance.state['working_directory'])
    requested_path = os.path.abspath(os.path.join(base_dir, filename))

    if not requested_path.startswith(base_dir):
        jha2_instance.callback("error", "Error: Invalid file path.")
        return None

    return requested_path

def validate_file_type(filename: str) -> bool:
    """
    Validates file type against allowed extensions.

    Args:
        filename (str): Name of file to validate

    Returns:
        bool: True if valid file type, False otherwise
    """
    ALLOWED_EXTENSIONS = {'txt', 'py', 'js', 'json', 'html', 'css'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes filename to prevent path traversal.

    Args:
        filename (str): Name of file to sanitize

    Returns:
        str: Sanitized filename
    """
    return os.path.basename(filename)