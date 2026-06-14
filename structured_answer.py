import anthropic
import json
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Define the output structure
class DocumentAnswer(BaseModel):
    answer: str  # The actual answer
    confidence: str  # "high", "medium", or "low"
    section_referenced: str  # Which part of the document
    sources: list[str]  # Page numbers or section names

system_prompt = """You are a document assistant. Answer questions using ONLY the provided document.

For every answer:
1. Provide the answer itself
2. Rate your confidence (high/medium/low)
3. Cite which section you found it in
4. List any page references"""

user_question = """
Document context: "Our refund policy allows returns within 30 days of purchase. 
Shipping costs are non-refundable. Please contact support@company.com for refund requests."

Question: What is the refund window?
"""

# Call Claude with structured output
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0.2,
    system=system_prompt,
    messages=[{"role": "user", "content": user_question}]
)

# Parse the response as JSON
import json
response_text = response.content[0].text
answer_data = json.loads(response_text)
answer = DocumentAnswer(**answer_data)

# Now you have a typed object
print(f"Answer: {answer.answer}")
print(f"Confidence: {answer.confidence}")
print(f"Section: {answer.section_referenced}")
print(f"Sources: {', '.join(answer.sources)}")