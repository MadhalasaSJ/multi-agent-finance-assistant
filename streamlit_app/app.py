import sys
import os
import streamlit as st
import tempfile
import numpy as np
import soundfile as sf
import platform

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orchestrator.orchestrator import Orchestrator
from agents.voice_agent import VoiceAgent
from audio_recorder_streamlit import audio_recorder

# --- Streamlit Config ---
st.set_page_config(page_title="🧠 Finance Assistant", layout="centered")
st.title("📈 Multi-Agent Finance Assistant")
st.markdown("Ask a market question — by **voice** or **text** — and get a spoken market brief!")

# --- Initialize Agents ---
orchestrator = Orchestrator()
voice_agent = VoiceAgent()

# --- Mic Toggle ---
use_mic = st.toggle("🎤 Use Microphone", value=False)
query = None

# --- Microphone Input ---
if use_mic:
    st.info("🎙️ Click the mic, wait a second, then speak clearly for 5–6 seconds.")

    audio_bytes = audio_recorder(pause_threshold=3.0)

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        try:
            # Save raw audio bytes to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as raw_file:
                raw_file.write(audio_bytes)
                raw_file.flush()
                data, samplerate = sf.read(raw_file.name)

            # Save in correct format for Whisper
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as formatted_file:
                sf.write(formatted_file.name, data, 16000)

            # Transcribe via VoiceAgent
            query = voice_agent.speech_to_text(formatted_file.name)

            if query.strip():
                st.success(f"🗣️ You said: `{query}`")
            else:
                st.warning("😕 Couldn't understand your voice. Please try again.")
        except Exception as e:
            st.error(f"❌ Audio processing failed: {e}")
            query = ""

# --- Text Input Fallback ---
else:
    query = st.text_input("📝 Type your question:")

# --- Run Assistant ---
if query and st.button("🔍 Run"):
    with st.spinner("Thinking..."):
        response = orchestrator.handle(query)

    st.success("✅ Response Generated")
    st.markdown("### 🧠 Market Brief:")
    st.markdown(response)

    voice_agent.text_to_speech(response)
    if os.path.exists("output.wav"):
        st.audio("output.wav", format="audio/wav")
