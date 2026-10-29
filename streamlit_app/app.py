
import sys
import os
import tempfile
import math

import streamlit as st
import soundfile as sf
from scipy.signal import resample_poly

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.append(PROJECT_ROOT)

from orchestrator.orchestrator import Orchestrator
from agents.voice_agent import VoiceAgent
from audio_recorder_streamlit import audio_recorder


# --- Streamlit Config ---
st.set_page_config(
    page_title="Multi-Agent Finance Assistant",
    layout="centered"
)

st.title("📈 Multi-Agent Finance Assistant")
st.markdown(
    "Ask a market question by voice or text "
    "and receive a finance brief in your preferred language."
)


# --- Initialize Agents ---
@st.cache_resource
def load_agents():
    return Orchestrator(), VoiceAgent()


orchestrator, voice_agent = load_agents()


# --- Language Settings ---
language_mode = st.radio(
    "Response language",
    ["Automatic (voice)", "English", "Hindi", "German"],
    horizontal=True
)

use_mic = st.toggle("🎤 Use Microphone", value=False)

query = None
audio_bytes = None
formatted_path = None
raw_path = None
detected_language = "English"


# --- Microphone Input ---
if use_mic:
    st.info(
        "Record your question clearly. "
        "Automatic mode detects the spoken language."
    )

    audio_bytes = audio_recorder(pause_threshold=2.0)

    if audio_bytes:
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".wav"
            ) as raw_file:
                raw_file.write(audio_bytes)
                raw_path = raw_file.name

            data, samplerate = sf.read(raw_path)

            if data.size == 0:
                raise ValueError("The recording is empty.")

            # Convert stereo to mono
            if data.ndim > 1:
                data = data.mean(axis=1)

            # Resample correctly to 16 kHz
            if samplerate != 16000:
                divisor = math.gcd(int(samplerate), 16000)
                data = resample_poly(
                    data,
                    16000 // divisor,
                    int(samplerate) // divisor
                )

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".wav"
            ) as formatted_file:
                formatted_path = formatted_file.name

            sf.write(formatted_path, data, 16000)

            # Whisper transcribes and detects the spoken language
            query = voice_agent.speech_to_text(formatted_path)
            detected_language = voice_agent.detected_language

            if query:
                st.success(f"🗣️ You said: {query}")
                st.caption(
                    f"Detected spoken language: {detected_language}"
                )
            else:
                st.warning(
                    "Couldn't understand your recording. "
                    "Please record again."
                )
                query = None

        except Exception as e:
            st.error(f"Audio processing failed: {e}")
            query = None

        finally:
            for path in (raw_path, formatted_path):
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

else:
    query = st.text_input(
        "📝 Type your question:",
        placeholder="e.g. Summarize NVIDIA's stock performance"
    )


# --- Choose Response Language ---
if language_mode == "Automatic (voice)":
    response_language = (
        detected_language if use_mic else "English"
    )
else:
    response_language = language_mode


# --- Generate Response ---
if query and st.button("🔍 Run"):
    output_path = None

    try:
        with st.spinner(
            f"Generating your market brief in {response_language}..."
        ):
            response = orchestrator.handle(
                query,
                language=response_language
            )

            output_path = voice_agent.text_to_speech(
                response,
                language=response_language
            )

        st.success("✅ Response generated")
        st.markdown("### 🧠 Market Brief")
        st.markdown(response)

        if output_path and os.path.exists(output_path):
            st.markdown("### 🔊 Spoken Finance Response")
            st.audio(output_path, format="audio/wav")
        else:
            st.warning(
                "Speech generation was unavailable. "
                "You can still read the market brief above."
            )

    except Exception as e:
        st.error(f"Could not generate the market brief: {e}")
