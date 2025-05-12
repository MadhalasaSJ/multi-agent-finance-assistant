import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from orchestrator.orchestrator import Orchestrator
from agents.voice_agent import VoiceAgent

st.set_page_config(page_title="🧠 Finance Assistant", layout="centered")

# Initialize
orchestrator = Orchestrator()
voice_agent = VoiceAgent()

st.title("📈 Multi-Agent Finance Assistant")
st.markdown("Ask a market question and get a spoken response!")

# Input Section
query = st.text_input("🗣️ Ask your question:", "What’s our risk exposure in Asia tech stocks today, and highlight any earnings surprises?")

if st.button("🔍 Run"):
    with st.spinner("Thinking..."):
        response = orchestrator.handle(query)

    st.text("✅ Response ready!")  # Debug marker — delete later if all works
    st.success("✅ Response Generated")
    st.markdown("### 🧠 Market Brief:")
    st.markdown(response)

    audio_path = "output.wav"
    voice_agent.text_to_speech(response)
    st.audio(audio_path, format="audio/wav")
