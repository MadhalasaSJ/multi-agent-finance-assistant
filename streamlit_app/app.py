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
    st.info("🎙️ Click the mic, wait a second, and then speak clearly.")

    audio_bytes = audio_recorder(pause_threshold=3.0)

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        try:
            # Save bytes and ensure correct audio format
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                f.flush()

            data, samplerate = sf.read(f.name)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as corrected_file:
                sf.write(corrected_file.name, data, samplerate)
                query = voice_agent.speech_to_text(corrected_file.name)

            if query.strip():
                st.success(f"🗣️ You said: `{query}`")
            else:
                st.warning("😕 Couldn't understand your voice. Try again.")
        except Exception as e:
            st.error(f"❌ Audio processing failed: {e}")
            query = ""

# --- Text Input ---
else:
    query = st.text_input("📝 Type your question:")

# --- Handle Query ---
if query and st.button("🔍 Run"):
    with st.spinner("Thinking..."):
        response = orchestrator.handle(query)

    st.success("✅ Response Generated")
    st.markdown("### 🧠 Market Brief:")
    st.markdown(response)

    voice_agent.text_to_speech(response)
    if os.path.exists("output.wav"):
        st.audio("output.wav", format="audio/wav")
