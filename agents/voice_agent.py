import whisper
import pyttsx3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile
from orchestrator.orchestrator import Orchestrator

class VoiceAgent:
    def __init__(self):
        print("🔈 Initializing Whisper STT and pyttsx3 TTS...")
        self.model = whisper.load_model("base")
        self.engine = pyttsx3.init()

    def record_audio(self, duration=5, samplerate=16000):
        print(f"🎤 Recording for {duration} seconds...")
        recording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1)
        sd.wait()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wavfile.write(f.name, samplerate, np.int16(recording * 32767))
            return f.name

    def speech_to_text(self, audio_file):
        print("📝 Transcribing audio...")
        result = self.model.transcribe(audio_file)
        return result["text"]

    def text_to_speech(self, text):
        print("🗣️ Speaking: " + text)
        self.engine.say(text)
        self.engine.runAndWait()

if __name__ == "__main__":
    # Initialize agents
    voice_agent = VoiceAgent()
    orchestrator = Orchestrator()

    # Record voice input
    audio_path = voice_agent.record_audio(duration=6)
    query = voice_agent.speech_to_text(audio_path)
    print("👂 You said:", query)

    response = orchestrator.handle(query)
    voice_agent.text_to_speech(response)
