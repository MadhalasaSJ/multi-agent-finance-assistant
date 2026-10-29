# 🧠 Multi-Agent Finance Assistant

A multilingual, voice-enabled financial assistant that retrieves stock market data, searches relevant financial information using FAISS, and generates concise market briefs in **English, Hindi, and German**. Users can ask questions by voice or text and listen to the generated response.

## ✨ Features

- 📈 **Stock Market Data:** Retrieves stock prices using Yahoo Finance (`yfinance`).
- 📊 **Earnings Information:** Fetches earnings summaries through the scraper agent.
- 🔎 **Semantic Search:** Uses FAISS and Sentence Transformers for relevant document retrieval.
- 🤖 **Local LLM:** Uses Gemma 3 1B through Ollama for financial news translation.
- 🌐 **Multilingual Responses:** Supports English, Hindi, and German.
- 🎤 **Voice Input:** Uses Whisper for speech recognition and language detection.
- 🗣️ **Text-to-Speech:** Uses Piper TTS with language-specific voices.
- 🖥️ **Interactive Interface:** Streamlit application for text and voice-based queries.
- 🧮 **Deterministic Calculations:** Calculates stock price percentage changes using Python.

## 🏗️ Architecture

```text
                    User Query
                   /          \
              Text Input    Voice Input
                                |
                            Whisper STT
                                |
                                v
                           Orchestrator
                           /          \
                          v            v
                     APIAgent      ScraperAgent
                         |              |
                    Yahoo Finance   Earnings Data
                         |              |
                         v              v
                     Market Data   RetrieverAgent
                                       |
                              Sentence Transformers
                                       |
                                     FAISS
                          \            /
                           v          v
                            LanguageAgent
                                  |
                          Gemma 3 1B Translation
                                  |
                       English / Hindi / German
                                  |
                            Text Response
                                  |
                               Piper TTS
                                  |
                           Spoken Response
```

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Market Data | Yahoo Finance (`yfinance`) |
| Information Retrieval | FAISS |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Local Language Model | Gemma 3 1B via Ollama |
| Speech Recognition | Whisper |
| Speech Synthesis | Piper TTS |
| Web Interface | Streamlit |
| Audio Processing | FFmpeg, SoundFile, SciPy |

## 🚀 Getting Started

### Prerequisites

Install the following before running the application:

- Python (3.11 recommended)
- Git
- FFmpeg
- Ollama
- Piper voice models for the required languages

### 1. Clone the Repository

```bash
git clone https://github.com/MadhalasaSJ/multi-agent-finance-assistant.git
cd multi-agent-finance-assistant
```

### 2. Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Ollama

Install Ollama from [ollama.com](https://ollama.com/) and download the model:

```bash
ollama pull gemma3:1b
```

Verify that the model is available:

```bash
ollama list
```

Ensure the Ollama service is running before starting the application.

### 5. Configure Piper TTS Voices

Download the required voice models:

```bash
python -m piper.download_voices en_US-lessac-medium
python -m piper.download_voices hi_IN-rohan-medium
python -m piper.download_voices de_DE-thorsten-medium
```

Ensure the downloaded `.onnx` files are available at the paths configured in `agents/voice_agent.py`.

### 6. Configure API Credentials

If your earnings scraper requires an Alpha Vantage API key, obtain one from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) and configure it using the environment variable expected by your scraper agent.

Never commit API keys, `.env` files, or other secrets to GitHub.

### 7. Run the Application

From the repository root:

```bash
streamlit run streamlit_app/app.py
```

Open the local URL displayed in the terminal.

## 📂 Project Structure

```text
multi-agent-finance-assistant/
├── agents/
│   ├── api_agent.py
│   ├── language_agent.py
│   ├── retriever_agent.py
│   ├── scraper_agent.py
│   └── voice_agent.py
├── orchestrator/
│   └── orchestrator.py
├── streamlit_app/
│   └── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🧩 Agent Modules

| Agent | Responsibility |
|---|---|
| `APIAgent` | Retrieves stock prices from Yahoo Finance. |
| `ScraperAgent` | Retrieves earnings-related information. |
| `RetrieverAgent` | Generates embeddings and searches indexed documents using FAISS. |
| `LanguageAgent` | Formats financial summaries, calculates stock movements from supplied prices, and translates relevant news. |
| `VoiceAgent` | Converts speech to text and generates spoken responses. |
| `Orchestrator` | Coordinates the agents and routes user queries. |

## 💬 Example Queries

**English**
- What is the latest stock price of NVIDIA?
- Compare Apple's and Microsoft's stock movements.

**Hindi**
- NVIDIA के शेयर की कीमत में कितना बदलाव आया?
- Apple और Microsoft में से किसके शेयर में अधिक वृद्धि हुई?

**German**
- Wie hat sich der NVIDIA-Aktienkurs verändert?
- Vergleiche die Kursentwicklung von Apple und Microsoft.

## 🔐 Notes and Limitations

- Stock data availability and freshness depend on Yahoo Finance and the requested trading period.
- FAISS retrieves information only from documents that have been indexed; it does not independently fetch live financial news.
- Financial calculations depend on the accuracy of the supplied market data.
- Local language generation and translation quality depend on the installed model.
- This project is intended for informational and educational purposes and does not provide personalized financial advice.

---
