import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# The conversation history — you manage this yourself
messages = []

system_prompt = """You are a document assistant. Your role is to answer questions about documents provided by the user.

Rules:
1. Only answer using information from the provided document.
2. If the answer is not in the document, say: "I cannot find this information in the provided document."
3. Be concise and direct."""

def chat(user_message):
    """Send a message and get a response."""
    # Add the new user message to history
    messages.append({"role": "user", "content": user_message})
    
    # Call Claude with full history
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        temperature=0.2,
        system=system_prompt,
        messages=messages
    )
    
    # Extract the reply
    assistant_reply = response.content[0].text
    
    # Add assistant's reply to history (so next call remembers this)
    messages.append({"role": "assistant", "content": assistant_reply})
    
    return assistant_reply

# Main chat loop
if __name__ == "__main__":
    print("DocuBot Chat — type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        response = chat(user_input)
        print(f"DocuBot: {response}\n")