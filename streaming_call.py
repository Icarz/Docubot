import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

print("DocuBot: ", end="", flush=True)

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0.2,
    system="You are a document assistant.",
    messages=[
        {"role": "user", "content": "Summarize what a refund policy typically covers."}
    ]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

print()  # newline after stream ends