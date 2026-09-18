# AI Meeting Intelligence & Action Tracker

## Setup
```bash
pip install -r requirements.txt
```

Get a free Groq API key from https://console.groq.com and set it:
```bash
export GROQ_API_KEY=your_key_here   # Windows: set GROQ_API_KEY=your_key_here
```

## Run
```bash
streamlit run app.py
```

Test it with `sample_transcript.txt` first — paste its content or upload it in the
"Upload Meeting" tab, hit **Process Meeting**, and check the summary + extracted
action items look right before trying your own transcripts.

## What's built (v1)
- Transcript ingestion + cleaning (`ingestion.py`)
- Map-reduce summarization chain (`chains.py`)
- Structured action-item extraction via `with_structured_output` + Pydantic (`chains.py`)
- SQLite storage for meetings and action items (`database.py`)
- Streamlit dashboard: upload, summary view, action item tracker with status toggle

## Not built yet (next steps)
- RAG-based meeting history search (FAISS + sentence-transformers) — ask me when ready
- Audio input (would need Whisper for transcription before this pipeline)
- Streamlit Cloud deployment (watch for the usual package version conflicts like your other projects)
