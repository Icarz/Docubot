import re
from pydantic import BaseModel


class DocumentAnswer(BaseModel):
    reasoning: str
    answer: str
    confidence: str
    section_referenced: str
    sources: list[str]


def extract_json_from_markdown(text: str) -> str:
    """Strip markdown code fences from a JSON response."""
    match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1)
    return text


DOCUMENT_QA_SYSTEM_PROMPT = """You are a document assistant. Answer questions using ONLY the provided document context.

REASONING PROCESS:
1. Search the document for relevant information
2. Identify the specific section and quote
3. Evaluate your confidence in the answer
4. Explain your reasoning clearly

RULES:
1. Only use information from the provided document.
2. If the answer is not in the document, say: "I cannot find this information in the provided document."
3. Always cite which section you're referencing.
4. Be concise and direct.

Return your response as valid JSON:
{
  "reasoning": "<explain how you found the answer>",
  "answer": "<the answer>",
  "confidence": "<high/medium/low>",
  "section_referenced": "<section name>",
  "sources": ["<exact quote from document>"]
}"""
