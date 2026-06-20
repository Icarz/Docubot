import anthropic
import json
import os
from dotenv import load_dotenv

# DEBUG: Check if .env is loaded
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"DEBUG: API key loaded: {api_key[:10] if api_key else 'NOT FOUND'}...")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in .env")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)

client = anthropic.Anthropic()

# Define tools
tools = [
    {
        "name": "search_documents",
        "description": "Search the knowledge base for policy information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculate_refund",
        "description": "Calculate refund amount after fees",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Original amount"},
                "fee_percent": {"type": "number", "description": "Fee as decimal"}
            },
            "required": ["amount", "fee_percent"]
        }
    }
]

def execute_tool(tool_name, tool_input):
    """Execute the actual tool."""
    if tool_name == "search_documents":
        # In real app: search ChromaDB
        return "Returns within 30 days. Restocking fee: 15%"
    elif tool_name == "calculate_refund":
        amount = tool_input["amount"]
        fee = tool_input["fee_percent"]
        refund = amount * (1 - fee)
        return f"${refund:.2f}"
    return "Tool not found"

def agent_loop(user_question):
    """Run the agent loop: call Claude, execute tools, repeat."""
    messages = [{"role": "user", "content": user_question}]
    
    print(f"User: {user_question}\n")
    
    # Loop until Claude stops calling tools
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        # Collect ALL tool calls from this response
        tool_uses = [block for block in response.content if block.type == "tool_use"]
        
        # If no tool calls, we're done
        if not tool_uses:
            for block in response.content:
                if block.type == "text":
                    print(f"Claude: {block.text}")
            break
        
        # Add Claude's response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # Execute ALL tools and collect results
        tool_results = []
        for tool_use in tool_uses:
            print(f"Claude calls: {tool_use.name}({tool_use.input})")
            result = execute_tool(tool_use.name, tool_use.input)
            print(f"Result: {result}\n")
            
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            })
        
        # Add ALL tool results in ONE user message
        messages.append({
            "role": "user",
            "content": tool_results
        })

# Test it
if __name__ == "__main__":
    agent_loop("What would a refund be for a $100 return?")