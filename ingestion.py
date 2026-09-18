"""
Load a raw meeting transcript and prep it for the LangChain summarization
and extraction chains. Kept deliberately simple for v1: plain .txt/.vtt
transcripts only. Swap in Whisper here later if you add audio input.
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_transcript(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def clean_transcript(text: str) -> str:
    """Strip common VTT/timestamp artifacts. Extend this as you feed in
    real transcripts from different tools (Zoom, Teams, Otter.ai, etc.)."""
    lines = text.splitlines()
    cleaned = [
        line for line in lines
        if line.strip() and "-->" not in line and not line.strip().isdigit()
    ]
    return "\n".join(cleaned)


def chunk_transcript(text: str, chunk_size: int = 3000, chunk_overlap: int = 200) -> list:
    """Only needed for long transcripts that would blow past the model's
    context window in the map-reduce summarization step."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )
    return splitter.split_text(text)
