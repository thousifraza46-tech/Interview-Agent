"""
Browser-based audio recording module for Streamlit.
Uses audio-recorder-streamlit for client-side recording.
No server-side microphone access required - works on Render and other cloud platforms.
"""

import os
import tempfile
from datetime import datetime
from typing import Optional


def save_recorded_audio(audio_bytes: bytes, filename: Optional[str] = None) -> str:
    """
    Save recorded audio bytes to a WAV file.
    
    Args:
        audio_bytes: Raw audio data from the browser recorder
        filename: Optional custom filename. If not provided, generates timestamp-based name.
        
    Returns:
        str: Path to the saved audio file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
    
    # Create recordings directory if it doesn't exist
    recordings_dir = "recordings"
    os.makedirs(recordings_dir, exist_ok=True)
    
    filepath = os.path.join(recordings_dir, filename)
    
    # Save the audio bytes to file
    with open(filepath, "wb") as f:
        f.write(audio_bytes)
    
    return filepath


def cleanup_audio_file(filepath: str) -> None:
    """
    Remove temporary audio file after processing.
    
    Args:
        filepath: Path to the audio file to delete
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Warning: Could not delete audio file {filepath}: {e}")
