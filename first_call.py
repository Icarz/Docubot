import anthropic
from dotenv import load_dotenv

load_dotenv()  # loads ANTHROPIC_API_KEY from .env

client = anthropic.Anthropic()  # auto-reads the env var

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    temperature=0.2,
    system="You are a document assistant. Answer only from the provided context.",
    messages=[
        {"role": "user", "content": "What is the refund policy?"}
    ]
)


print(response.content[0].text)
print(f"\n--- usage ---")
print(f"Input tokens:  {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
print(f"Stop reason:   {response.stop_reason}") 