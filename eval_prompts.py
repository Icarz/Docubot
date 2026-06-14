import anthropic
import json
import re
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

class DocumentAnswer(BaseModel):
    reasoning: str
    answer: str
    confidence: str
    section_referenced: str
    sources: list[str]

def extract_json_from_markdown(text):
    match = re.search(r'```(?:json)?\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

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

system_prompt = """You are a document assistant. Answer questions about documents provided by the user.

REASONING PROCESS:
1. Search the document for relevant information
2. Identify the specific section and quote
3. Evaluate your confidence in the answer
4. Explain your reasoning clearly

RULES:
1. Only use information from the provided document.
2. If the answer is not in the document, say: "I cannot find this information in the provided document."
3. Always cite which section you're referencing.

Return your response as valid JSON:
{
  "reasoning": "",
  "answer": "",
  "confidence": "",
  "section_referenced": "
",
  "sources": [""]
}"""

def get_answer(question):
    """Get a structured answer from Claude."""
    user_message = f"""Document context:
{SAMPLE_DOCUMENT}

User question: {question}"""
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0.2,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    response_text = response.content[0].text
    clean_json = extract_json_from_markdown(response_text)
    
    try:
        answer_data = json.loads(clean_json)
        return DocumentAnswer(**answer_data)
    except (json.JSONDecodeError, ValueError):
        return None

# Define test cases
# Replace the test_cases list with this:

test_cases = [
    {
        "name": "Test 1: Basic refund window",
        "question": "What is the refund window?",
        "check": lambda ans: "30" in ans.answer and ans.confidence.lower() == "high"  # ← lowercase()
    },
    {
        "name": "Test 2: Hallucination prevention",
        "question": "What is the restocking fee?",
        "check": lambda ans: (
            "cannot find" in ans.answer.lower() or 
            "not mentioned" in ans.answer.lower() or 
            "no mention" in ans.answer.lower()
        )  # ← Check for phrases, not confidence
    },
    {
        "name": "Test 3: Multi-step reasoning",
        "question": "If the return is due to a defect, do I pay shipping?",
        "check": lambda ans: "no" in ans.answer.lower() and "defect" in ans.answer.lower()
    },
    {
        "name": "Test 4: Citation accuracy",
        "question": "How long does a refund take?",
        "check": lambda ans: "5-7" in ans.answer and len(ans.sources) > 0
    }
]

# Run evals
print("Running Eval Suite for DocuBot\n")
print("=" * 60)

passed = 0
failed = 0

for test in test_cases:
    print(f"\n{test['name']}")
    print(f"Question: {test['question']}")
    
    answer = get_answer(test['question'])
    
    if answer is None:
        print(f"Result: FAIL (parsing error)")
        failed += 1
        continue
    
    passed_check = test['check'](answer)
    
    if passed_check:
        print(f"Result: PASS ✓")
        passed += 1
    else:
        print(f"Result: FAIL ✗")
        print(f"  Answer: {answer.answer}")
        print(f"  Confidence: {answer.confidence}")
        failed += 1

print(f"\n{'=' * 60}")
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print(f"Pass rate: {passed / len(test_cases) * 100:.0f}%")