import anthropic
import json
import re
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Define the structured output format
class DocumentAnswer(BaseModel):
    reasoning: str  
    answer: str
    confidence: str  # "high", "medium", or "low"
    section_referenced: str
    sources: list[str]

def extract_json_from_markdown(text):
    """Remove markdown code blocks if present."""
    match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

# Sample document — in real DocuBot, this comes from PDF
SAMPLE_DOCUMENT = """
COMPANY REFUND AND RETURN POLICY (Section 3)

3.1 Refund Window
All purchases are eligible for refund or return within 30 days of purchase. 
Items must be in original condition with all packaging intact.

3.2 Shipping Costs
Original shipping costs are non-refundable. Return shipping is the responsibility 
of the customer unless the return is due to a defect.

3.3 Refund Processing
Refunds are processed within 5-7 business days after we receive and inspect 
the returned item. The refund is issued to the original payment method.

3.4 Contact Information
For refund requests, contact support@company.com or call 1-800-COMPANY.
"""

# Conversation history — managed by you
messages = []

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

def chat(user_question):
    """Send a question and get a structured answer."""
    # Inject the document context into the user message
    user_message_with_context = f"""Document context:
{SAMPLE_DOCUMENT}

User question: {user_question}"""
    
    # Add the user message to history
    messages.append({"role": "user", "content": user_message_with_context})
    
    # Call Claude
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0.2,
        system=system_prompt,
        messages=messages
    )
    
    # Extract and clean the response
    response_text = response.content[0].text
    clean_json = extract_json_from_markdown(response_text)
    
    # Parse into Pydantic model (validates structure)
    try:
        answer_data = json.loads(clean_json)
        answer = DocumentAnswer(**answer_data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error parsing response: {e}")
        return None
    
    # Add to history (so next turn remembers this)
    messages.append({"role": "assistant", "content": response_text})
    
    return answer

def print_answer(answer):
    """Pretty-print a structured answer."""
    if answer is None:
        print("Failed to get answer")
        return
    
    print(f"\n{'='*60}")
    print(f"ANSWER: {answer.answer}")
    print(f"{'='*60}")
    print(f"Confidence: {answer.confidence}")
    print(f"Section: {answer.section_referenced}")
    print(f"Sources: {', '.join(answer.sources)}")
    print()

# Main chat loop
if __name__ == "__main__":
    print("DocuBot Chat with Structured Outputs")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        answer = chat(user_input)
        print_answer(answer)