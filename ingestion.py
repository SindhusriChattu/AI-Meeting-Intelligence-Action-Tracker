"""
Meeting transcript ingestion utilities.

Responsibilities:
1. Convert transcript text into a LangChain Document.
2. Clean common transcript/VTT artifacts.
3. Split long transcripts into smaller chunks.
"""

from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_transcript(
    text: str,
    meeting_title: str,
    meeting_date: str
) -> Document:
    """
    Convert the user-provided meeting transcript
    into a LangChain Document.
    """

    return Document(
        page_content=text,
        metadata={
            "meeting_title": meeting_title,
            "meeting_date": meeting_date,
        }
    )


def clean_transcript(text: str) -> str:
    """
    Remove common VTT/timestamp artifacts
    from the meeting transcript.
    """

    lines = text.splitlines()

    cleaned = [
        line
        for line in lines
        if line.strip()
        and "-->" not in line
        and not line.strip().isdigit()
    ]

    return "\n".join(cleaned)


def chunk_transcript(
    text: str,
    chunk_size: int = 3000,
    chunk_overlap: int = 200
) -> list:
    """
    Split a long transcript into smaller chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )

    return splitter.split_text(text)