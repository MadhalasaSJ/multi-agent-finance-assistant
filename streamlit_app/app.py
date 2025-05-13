import sys
import os
import streamlit as st
import tempfile
import numpy as np
import soundfile as sf

# Add parent directory to path for importing agents
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

# --- Microphone Input Handling ---
if use_mic:
    st.info("🎙️ Click the mic, wait 1 sec, then speak clearly for 5–6 seconds.")
    audio_bytes = audio_recorder(pause_threshold=3.0)

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        try:
            # Save incoming .wav bytes to file and reprocess to correct format
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                f.flush()

            # Read and re-save the audio properly
            data, samplerate = sf.read(f.name)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f2:
                sf.write(f2.name, data, samplerate)
                query = voice_agent.speech_to_text(f2.name)

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

    # Generate & stream audio response
    voice_agent.text_to_speech(response)
    st.audio("output.wav", format="audio/wav")
