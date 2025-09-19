# backend/app/services/voice.py

import whisper
import pyttsx3
import tempfile
import os
import io
from fastapi import UploadFile

# Load the "base" Whisper model.
model = whisper.load_model("base")

def transcribe_audio(file: UploadFile) -> str:
    """Transcribe audio to text using local Whisper model"""
    temp_audio_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_audio_file:
            content = file.file.read()
            temp_audio_file.write(content)
            temp_audio_file_path = temp_audio_file.name

        result = model.transcribe(temp_audio_file_path)
        return result["text"]
    finally:
        if temp_audio_file_path and os.path.exists(temp_audio_file_path):
            os.remove(temp_audio_file_path)

def synthesize_speech(text: str) -> bytes:
    """Convert text to speech using local pyttsx3 and return audio bytes"""
    try:
        engine = pyttsx3.init()
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as temp_audio_file:
            temp_path = temp_audio_file.name

        engine.save_to_file(text, temp_path)
        engine.runAndWait()

        with open(temp_path, 'rb') as f:
            return f.read() # Return the raw audio bytes
    except Exception as e:
        print(f"Error in TTS: {e}")
        return b""