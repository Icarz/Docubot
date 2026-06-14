import anthropic
import json
from pydantic import BaseModel
from dotenv import load_dotenv
import re

load_dotenv()
client = anthropic.Anthropic()

class DocumentAnswer(BaseModel):
    reasoning: str  
    answer: str
    confidence: str
    section_referenced: str
    sources: list[str]

def extract_json_from_markdown(text):
    """Remove markdown code blocks if present."""   
    match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

system_prompt = """You are a document assistant. Your role is to answer questions about documents provided by the user.

ALWAYS follow this reasoning process:
1. Search the document for relevant information
2. Identify the specific section and quote
3. Evaluate your confidence in the answer
4. Explain your reasoning clearly

Rules:
1. Only use information from the provided document.
2. If the answer is not in the document, say: "I cannot find this information in the provided document."
3. Be concise and direct.
4. Always cite which section you're referencing.

Return your response as valid JSON with this exact structure:
{
  "reasoning": "",
  "answer": "",
  "confidence": "",
  "section_referenced": "
",
  "sources": [""]
}"""

user_question = """
Document: "Refund policy allows returns within 30 days. Shipping costs are non-refundable. Contact support@company.com for refund requests."
Question: What is the refund window?
"""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0.2,
    system=system_prompt,
    messages=[{"role": "user", "content": user_question}]
)

response_text = response.content[0].text
clean_json = extract_json_from_markdown(response_text)  # ← Strip the backticks
answer_data = json.loads(clean_json)
answer = DocumentAnswer(**answer_data)

print(f"Answer: {answer.answer}")
print(f"Confidence: {answer.confidence}")
print(f"Section: {answer.section_referenced}")
print(f"Sources: {', '.join(answer.sources)}")