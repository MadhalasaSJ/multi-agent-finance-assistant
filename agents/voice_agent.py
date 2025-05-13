import whisper
import pyttsx3
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from orchestrator.orchestrator import Orchestrator

class VoiceAgent:
    def __init__(self):
        print("🔈 Initializing Whisper STT and pyttsx3 TTS...")

        # Fix: Avoid calling .to() to prevent meta tensor error in PyTorch > 2.3
        self.model = whisper.load_model("small", download_root="models")

        self.engine = pyttsx3.init()

    def record_audio(self, duration=8, samplerate=16000):
        print(f"🎤 Recording for {duration} seconds...")
        try:
            recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1)
            sd.wait()
        except Exception as e:
            print(f"❌ Error during audio recording: {e}")
            return None

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            audio_data = np.int16(recording * 32767)
            wavfile.write(f.name, samplerate, audio_data)
            print(f"✅ Audio saved at: {f.name}")
            return f.name

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

    audio_path = voice_agent.record_audio(duration=8)
    if audio_path:
        query = voice_agent.speech_to_text(audio_path)
        print("👂 You said:", query)

        if query.strip():
            response = orchestrator.handle(query)
            voice_agent.text_to_speech(response)
        else:
            print("⚠️ No speech detected. Try again in a quieter environment.")