
import sys
import os
import re
import wave

# Make FFmpeg available to Whisper
ffmpeg_bin = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "Microsoft",
    "WinGet",
    "Packages",
    "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
    "ffmpeg-9.0.2-full_build",
    "bin"
)

if os.path.isdir(ffmpeg_bin):
    os.environ["PATH"] = (
        ffmpeg_bin + os.pathsep + os.environ.get("PATH", "")
    )

import whisper
from piper import PiperVoice

# Project root
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.append(PROJECT_ROOT)

from orchestrator.orchestrator import Orchestrator


class VoiceAgent:
    def __init__(self):
        print("Initializing Whisper STT and Piper TTS...")

        self.model = whisper.load_model("tiny")
        self.orchestrator = Orchestrator()

        # Whisper language codes mapped to supported languages
        self.language_codes = {
            "en": "English",
            "hi": "Hindi",
            "kn": "Kannada",
            "de": "German"
        }

        self.detected_language = "English"

        # Configure each local Piper voice through environment variables.
        # English retains your existing voice model as the default.
        self.voice_paths = {
            "English": os.getenv(
                "PIPER_VOICE_ENGLISH",
                os.path.join(PROJECT_ROOT, "en_US-lessac-medium.onnx")
            ),
            "Hindi": os.getenv(
                "PIPER_VOICE_HINDI",
                os.path.join(PROJECT_ROOT, "hi_IN-rohan-medium.onnx")
            ),
            "German": os.getenv(
                "PIPER_VOICE_GERMAN",
                os.path.join(PROJECT_ROOT, "de_DE-thorsten-medium.onnx")
            )
        }

        # Cache loaded voices so they aren't reloaded for every response.
        self.tts_voices = {}

        # Load English voice initially
        self.get_tts_voice("English")

    def get_tts_voice(self, language):
        """Load and cache the Piper voice for a language."""
        if language in self.tts_voices:
            return self.tts_voices[language]

        voice_path = self.voice_paths.get(language, "")

        if not voice_path or not os.path.isfile(voice_path):
            print(
                f"Piper voice unavailable for {language}. "
                "Using English voice as fallback."
            )
            language = "English"
            voice_path = self.voice_paths["English"]

            if language in self.tts_voices:
                return self.tts_voices[language]

        if not voice_path or not os.path.isfile(voice_path):
            print("English Piper voice model was not found.")
            return None

        try:
            voice = PiperVoice.load(voice_path)
            self.tts_voices[language] = voice
            print(f"Piper voice loaded: {language}")
            return voice
        except Exception as e:
            print(f"Could not load {language} voice: {e}")
            return None

    def speech_to_text(self, audio_file):
        """Transcribe speech and detect its language."""
        print("Transcribing audio...")

        try:
            result = self.model.transcribe(
                audio_file,
                task="transcribe"
            )

            language_code = result.get("language", "en")
            self.detected_language = self.language_codes.get(
                language_code, "English"
            )

            print("Detected language:", self.detected_language)

            return result.get("text", "").strip()

        except Exception as e:
            print(f"Transcription error: {e}")
            self.detected_language = "English"
            return ""

    def clean_text_for_speech(self, text):
        """Remove Markdown formatting before speech synthesis."""
        text = re.sub(r"(?m)^\s*#{1,6}\s*", "", text)
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"__(.*?)__", r"\1", text)
        text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
        text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", text)
        text = re.sub(r"`([^`]*)`", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"(?m)^\s*[-*+]\s+", "", text)
        text = re.sub(r"(?m)^\s*\d+[.)]\s+", "", text)
        text = re.sub(r"(?m)^\s*[-*_]{3,}\s*$", "", text)
        text = re.sub(r"[#*`_]", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def text_to_speech(
        self,
        text,
        out_file="output.wav",
        language=None
    ):
        if not text or not text.strip():
            print("No text provided for speech generation.")
            return None

        language = language or self.detected_language
        voice = self.get_tts_voice(language)

        if voice is None:
            print("Piper TTS is unavailable.")
            return None

        clean_text = self.clean_text_for_speech(text)

        if not clean_text:
            print("No readable text remains after cleaning.")
            return None

        if not os.path.isabs(out_file):
            out_file = os.path.join(PROJECT_ROOT, out_file)

        if os.path.exists(out_file):
            os.remove(out_file)

        try:
            print(f"Generating speech in {language}...")

            with wave.open(out_file, "wb") as wav_file:
                voice.synthesize_wav(clean_text, wav_file)

            if os.path.getsize(out_file) == 0:
                raise RuntimeError("Generated audio file is empty.")

            print(f"Speech saved to {out_file}")
            return out_file

        except Exception as e:
            print(f"Piper speech generation failed: {e}")

            if os.path.exists(out_file):
                os.remove(out_file)

            return None

    def handle_audio_query(self, audio_file):
        query = self.speech_to_text(audio_file)
        language = self.detected_language

        print("You said:", query)
        print("Detected language:", language)

        if query:
            response = self.orchestrator.handle(query)
            self.text_to_speech(response, language=language)
            return query, response

        return "", "No valid speech detected."


if __name__ == "__main__":
    agent = VoiceAgent()

    print("Supported languages: English, Hindi, German")
    print("Provide a recording through the app to test detection.")
