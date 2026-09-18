"""
The core LangChain piece of the project:
1. A summarization chain (map-reduce for long transcripts, plain for short ones)
2. A structured-output chain that extracts action items as validated Pydantic objects

This is the part worth understanding line-by-line before it goes on your resume.
"""
import os
from typing import List, Literal

from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

from ingestion import chunk_transcript


def get_llm(model: str = "llama-3.3-70b-versatile", temperature: float = 0):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Set GROQ_API_KEY as an environment variable before running.")
    return ChatGroq(model=model, temperature=temperature, api_key=api_key)


# ---------- 1. Summarization ----------

def summarize_transcript(transcript: str, llm=None) -> str:
    """Uses map-reduce so long transcripts don't blow past context limits.
    For short transcripts this still works fine, just slightly slower."""
    llm = llm or get_llm()
    chunks = chunk_transcript(transcript)
    docs = [Document(page_content=c) for c in chunks]

    map_prompt = PromptTemplate.from_template(
        "Summarize the key points, decisions, and open questions from this "
        "portion of a meeting transcript:\n\n{text}\n\nSUMMARY:"
    )
    combine_prompt = PromptTemplate.from_template(
        "Combine these partial meeting summaries into one clear, well-organized "
        "final summary with sections for Key Discussion Points and Decisions Made:"
        "\n\n{text}\n\nFINAL SUMMARY:"
    )

    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt,
    )
    return chain.invoke({"input_documents": docs})["output_text"]


# ---------- 2. Structured action-item extraction ----------

class ActionItem(BaseModel):
    task: str = Field(description="A specific, actionable task mentioned in the meeting")
    owner: str = Field(description="Person responsible, or 'Unassigned' if not stated")
    deadline: str = Field(description="Deadline mentioned, or 'Not specified'")
    priority: Literal["High", "Medium", "Low"] = Field(description="Inferred urgency")


class ActionItemList(BaseModel):
    items: List[ActionItem] = Field(description="All action items found in the transcript")


def extract_action_items(transcript: str, llm=None) -> List[dict]:
    """Uses LangChain's with_structured_output so the model returns validated
    Pydantic objects directly -- no manual JSON parsing or regex needed."""
    llm = llm or get_llm()
    structured_llm = llm.with_structured_output(ActionItemList)

    prompt = PromptTemplate.from_template(
        "Read this meeting transcript and extract every action item, task, or "
        "commitment mentioned. If no owner or deadline was stated, say so "
        "explicitly rather than guessing.\n\nTRANSCRIPT:\n{transcript}"
    )

    chain = prompt | structured_llm
    result: ActionItemList = chain.invoke({"transcript": transcript})
    return [item.model_dump() for item in result.items]
