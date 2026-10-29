# 🧠 AI Tool Usage Log

This document outlines how AI and machine learning tools are used in the Multi-Agent Finance Assistant.

---

## 1. 🤖 Local LLM Usage

**Model:** `gemma3:1b`  
**Runtime:** Ollama

Gemma 3 1B is used for translating retrieved financial news into the selected response language. The supported languages are English, Hindi, and German.

The model is instructed to:
- Translate financial news without adding new facts.
- Preserve company names, ticker symbols, dates, and financial figures.
- Return output in the selected language.
- Avoid introducing unsupported financial claims.

### Prompt Used

```text
Translate the financial news below into the selected language.

Requirements:
- Translate the complete text into the target language.
- Preserve company names, ticker symbols, dates, numbers,
  percentages, currencies, and financial terminology.
- Do not add explanations, predictions, or new information.
- Do not summarize or omit any claims.
- Return only the translation.

Source text:
{document}
```

The application also validates translated numerical values before including translated news in the final response.

---

## 2. 🔎 Vector Retrieval

- **Embedding Model:** `all-MiniLM-L6-v2`
- **Embedding Library:** Sentence Transformers
- **Vector Index:** `faiss.IndexFlatL2`
- **Agent:** `RetrieverAgent`

The retriever converts financial documents into embeddings and searches the indexed documents for information relevant to a user query.

FAISS retrieves information from the indexed corpus; it does not independently fetch live financial news or stock prices.

---

## 3. 📈 Financial Data Ingestion

### Yahoo Finance

- **Library:** `yfinance`
- **Agent:** `APIAgent`

Retrieves historical closing prices for supported stock tickers. Python calculates the percentage change between the previous and current closing prices:

```python
change = ((current - previous) / previous) * 100
```

### Earnings Information

- **Agent:** `ScraperAgent`

Retrieves earnings-related information for use in the financial briefing. The available information depends on the scraper's data source and retrieval results.

---

## 4. 🎤 Voice Processing

### Speech-to-Text

- **Tool:** Whisper
- **Agent:** `VoiceAgent`

Transcribes spoken queries and detects the spoken language to support voice-based interaction.

### Text-to-Speech

- **Tool:** Piper TTS
- **Voice Models:** English, Hindi, and German

Converts generated financial responses into spoken audio using language-specific voice models.

### Audio Processing

- FFmpeg
- SoundFile
- SciPy

These tools support audio processing and preparation for speech recognition and playback.

---

## 5. 🌐 Multilingual Response Generation

The application supports:

- 🇬🇧 English
- 🇮🇳 Hindi
- 🇩🇪 German

The `LanguageAgent` formats stock movements using deterministic Python calculations and language-specific templates. Retrieved financial news can be translated using Gemma 3 1B.

Numerical validation helps detect translation errors, although it cannot guarantee complete factual accuracy or grammatical correctness.

---

## 6. 👥 Agent Roles and Orchestration

| Agent | Responsibility |
|---|---|
| `APIAgent` | Retrieves stock price data through Yahoo Finance. |
| `ScraperAgent` | Retrieves earnings-related information. |
| `RetrieverAgent` | Generates document embeddings and retrieves relevant context using FAISS. |
| `LanguageAgent` | Formats market briefs, calculates stock movements, and translates relevant news. |
| `VoiceAgent` | Handles speech transcription and spoken response generation. |
| `Orchestrator` | Coordinates agents and routes user queries through the application pipeline. |

All agents are coordinated through the `Orchestrator` class.

---

## 7. 🔄 Processing Pipeline

```text
User Text or Voice Query
          |
          v
       Orchestrator
          |
     +----+-----+
     |          |
     v          v
  APIAgent   ScraperAgent
     |          |
     v          v
 Stock Data  Earnings Documents
     |          |
     |      RetrieverAgent
     |          |
     +----+-----+
          |
          v
     LanguageAgent
          |
   Python Calculations
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

---

## 8. ⏱️ Performance Observations

Actual latency depends on the hardware, model loading, network conditions, data availability, and audio duration.

The current implementation uses a local LLM and local speech-processing components. No fixed performance benchmarks are documented here because timings have not been systematically measured across representative queries.

---

## 9. ⚠️ Limitations

- Stock prices depend on the availability and freshness of Yahoo Finance data.
- FAISS can retrieve only documents that have been indexed.
- Retrieved documents may be irrelevant or outdated if retrieval is not sufficiently filtered.
- Gemma 3 1B may produce inaccurate translations despite prompt instructions.
- Numerical validation does not guarantee that every translated statement preserves its meaning.
- Speech recognition and synthesis quality depend on the selected language model and voice configuration.
- The application is intended for informational and educational purposes, not personalized financial advice.

---

## 🔗 Technologies Used

- [Ollama](https://ollama.com/)
- [Gemma](https://ai.google.dev/gemma)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [Whisper](https://github.com/openai/whisper)
- [Piper TTS](https://github.com/rhasspy/piper)
- [Streamlit](https://streamlit.io/)
- [yfinance](https://github.com/ranaroussi/yfinance)

---

**Project:** [Multi-Agent Finance Assistant](https://github.com/MadhalasaSJ/multi-agent-finance-assistant)
