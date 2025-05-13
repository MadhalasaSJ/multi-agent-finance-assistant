# 🧠 Multi-Agent Finance Assistant

This project is a multi-agent system that uses real-time market data, earnings summaries, vector retrieval, LLM synthesis, and voice interaction to generate and speak a concise financial briefing focused on Asia tech stocks.

---

## 📌 Features

- 📈 Live stock data (Yahoo Finance)
- 📊 Earnings reports (Alpha Vantage API)
- 🧠 Context-aware summary using OpenAI's GPT
- 🔎 Vector-based retrieval with FAISS
- 🎤 Voice input (Whisper) and 🗣️ speech output (pyttsx3)
- 📺 Streamlit Web App for user interaction

---

## 🧱 Architecture

[Voice Input]
↓
[Whisper STT] ─┐

├→ [ScraperAgent] → Earnings

├→ [APIAgent] → Market Data

├→ [RetrieverAgent] → FAISS vector search

└→ [LanguageAgent] → GPT synthesis

↓
[Text + TTS Output]


---

## 🚀 Getting Started

### 🔧 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/MadhalasaSJ/multi-agent-finance-assistant.git
   cd multi-agent-finance-assistant

2. Create .env file:
   ```bash
   OPENAI_API_KEY=your_openai_key
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key 

3. Install dependencies:
   ```bash
   pip install -r requirements.txt

4. Run the app:
   ```bash
   streamlit run streamlit_app/app.py


## 🌐 Deployment (Streamlit Cloud)

To deploy this app on [Streamlit Cloud](https://streamlit.io/cloud):

- Set **App path** to: `streamlit_app/app.py`
- In **Secrets**, add:
  ```bash
  OPENAI_API_KEY=your_openai_key
  ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key     
- Click **Deploy**


## 📦 Agent Modules

| Agent            | Function                                                  |
|------------------|-----------------------------------------------------------|
| `APIAgent`       | Retrieves live stock price data from Yahoo Finance        |
| `ScraperAgent`   | Fetches latest earnings data from Alpha Vantage API       |
| `RetrieverAgent` | Stores and retrieves context using FAISS + embeddings     |
| `LanguageAgent`  | Uses OpenAI GPT to synthesize a final summary             |
| `VoiceAgent`     | Handles voice input (Whisper) and output (pyttsx3 TTS)    |
<<<<<<< HEAD

=======
>>>>>>> f44bf72 (🧹 Removed pycache and added .gitignore)
