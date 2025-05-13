import sys
import whisper
import pyttsx3
import platform
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from orchestrator.orchestrator import Orchestrator

class VoiceAgent:
    def __init__(self):
        print("🔈 Initializing Whisper STT and optional TTS...")
        self.model = whisper.load_model("small")
        self.enable_tts = platform.system() in ["Windows", "Darwin"]
        if self.enable_tts:
            self.engine = pyttsx3.init()

        # 💡 THIS is where you load the orchestrator
        self.orchestrator = Orchestrator()

    def speech_to_text(self, audio_file):
        print("📝 Transcribing audio...")
        try:
            result = self.model.transcribe(audio_file)
            print("🧾 Whisper result:", result)
            return result.get("text", "").strip()
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""

    def text_to_speech(self, text, out_file="output.wav"):
        if not self.enable_tts:
            print("⚠️ TTS disabled on this platform")
            return

        print("🗣️ Saving speech to file...")
        try:
            self.engine.save_to_file(text, out_file)
            self.engine.runAndWait()
        except RuntimeError:
            print("⚠️ pyttsx3 event loop already running — skipping voice playback.")

    def handle_audio_query(self, audio_file):
        """👂 Record → 🧠 Understand → 💬 Speak"""
        query = self.speech_to_text(audio_file)
        print("👂 You said:", query)

        if query.strip():
            response = self.orchestrator.handle(query)
            self.text_to_speech(response)
            return query, response
        else:
            return "", "⚠️ No valid speech detected."

