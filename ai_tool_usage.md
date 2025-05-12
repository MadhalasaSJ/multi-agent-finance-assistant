# 🧠 AI Tool Usage Log

This document outlines how AI tools were used in the Multi-Agent Finance Assistant.

---

## 1. 🔍 Prompt Used for OpenAI GPT

```text
You are a market assistant.
Summarize today's Asia tech risk and highlight earnings.

Market data:
{market_data}

Documents:
{retrieved_texts}

Respond concisely and factually.

## 2. 🔧 LLM Configuration

- **Model**: `gpt-3.5-turbo`
- **Temperature**: `0.5`
- **Tool**: `openai.ChatCompletion.create` (via OpenAI Python SDK)

---

## 3. 🔄 Vector Retrieval

- **Embeddings**: `sentence-transformers` using `all-MiniLM-L6-v2`
- **Indexing**: `faiss.IndexFlatL2`
- **Used by**: `RetrieverAgent` to store and retrieve context for the LLM

---

## 4. 📈 Data Ingestion Tools

- `yfinance`: for fetching live market data for tech stocks in Asia  
- `Alpha Vantage API`: for quarterly earnings data (EPS and surprises)

---

## 5. 🎤 Voice Handling

- `whisper`: for speech-to-text transcription from mic input  
- `pyttsx3`: for offline text-to-speech output  
- **Controlled by**: `VoiceAgent`

---

## 6. 👥 Agent Roles and Orchestration

| Agent            | Role                                                        |
|------------------|-------------------------------------------------------------|
| `ScraperAgent`   | Fetches earnings data from Alpha Vantage                    |
| `APIAgent`       | Retrieves live market data                                  |
| `RetrieverAgent` | Indexes earnings text and retrieves relevant summaries      |
| `LanguageAgent`  | Synthesizes final brief using OpenAI GPT                    |
| `VoiceAgent`     | Handles voice input (Whisper) and voice output (TTS)        |

➡️ All agents are orchestrated via the `Orchestrator` class in a unified pipeline.

---

## ⏱️ Performance Observations

- API data fetch: ~1 second each  
- OpenAI GPT response time: ~2–3 seconds  
- Whisper transcription: ~2 seconds per 6s clip  
- Full voice-to-voice pipeline: ~5–6 seconds total