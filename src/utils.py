import os
from datetime import datetime
from pathlib import Path
from typing import Tuple

def get_unique_filename(base_path: str) -> str:
    """Generate a unique filename with timestamp."""
    directory = os.path.dirname(base_path) or '.'
    base_name, ext = os.path.splitext(os.path.basename(base_path))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{base_name}_{timestamp}{ext}"
    return os.path.join(directory, new_filename)

def save_uploaded_file(uploaded_file) -> Tuple[str, str]:
    """Save uploaded file and return its path."""
    if uploaded_file is None:
        return None, "No file uploaded"

    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        # Save the file
        file_path = upload_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return str(file_path), None
    except Exception as e:
        return None, str(e)