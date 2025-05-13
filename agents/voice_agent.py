import streamlit as st
import whisper
import pyttsx3
import tempfile
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from orchestrator.orchestrator import Orchestrator

class VoiceAgent:
    def __init__(self):
        print("🔈 Initializing Whisper STT and pyttsx3 TTS...")

        # Load Whisper model
        self.model = whisper.load_model("small", download_root="models")

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

    def speech_to_text(self, audio_file):
        print("📝 Transcribing audio...")
        try:
            result = self.model.transcribe(audio_file)
            print("🧾 Whisper result:", result)
            return result.get("text", "").strip()
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return ""

    def text_to_speech(self, text):
        print("🗣️ Speaking: " + text)
        self.engine.say(text)
        self.engine.runAndWait()

if __name__ == "__main__":
    voice_agent = VoiceAgent()
    orchestrator = Orchestrator()

    # Upload audio file
    audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3"])
    if audio_file is not None:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_file.read())
            f.close()
            
            # Transcribe the uploaded audio file
            query = voice_agent.speech_to_text(f.name)
            print("👂 You said:", query)

            if query.strip():
                response = orchestrator.handle(query)
                voice_agent.text_to_speech(response)
            else:
                print("⚠️ No speech detected. Try again.")
