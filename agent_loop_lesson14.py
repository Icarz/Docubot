import anthropic
import json
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in .env file")
    exit(1)

client = anthropic.Anthropic(api_key=api_key)

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
                    "description": "What to search for (e.g., 'refund policy', 'return window')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "lookup_customer",
        "description": "Look up customer information including order date and amount",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer ID or reference number"
                }
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "calculate_refund",
        "description": "Calculate refund amount after fees",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "Original purchase amount"
                },
                "fee_percent": {
                    "type": "number",
                    "description": "Fee as decimal (e.g., 0.15 for 15%)"
                }
            },
            "required": ["amount", "fee_percent"]
        }
    }
]

def execute_tool(tool_name, tool_input):
    """Execute the actual tool and return the result."""
    if tool_name == "search_documents":
        query = tool_input["query"]
        # In real DocuBot: search ChromaDB
        if "refund" in query.lower() or "return" in query.lower():
            return "Returns within 30 days. Restocking fee: 15%. No refunds after 30 days."
        elif "exception" in query.lower():
            return "No exceptions found for extended return windows."
        else:
            return "Document found but no relevant information for this query."
    
    elif tool_name == "lookup_customer":
        customer_id = tool_input["customer_id"]
        # In real DocuBot: look up in database
        return "Order date: 45 days ago. Purchase amount: $500. Product: Software License."
    
    elif tool_name == "calculate_refund":
        amount = tool_input["amount"]
        fee_percent = tool_input["fee_percent"]
        refund = amount * (1 - fee_percent)
        return f"${refund:.2f}"
    
    return "Tool not found"

def agent_loop(user_question, max_iterations=10):
    """
    Run the agent loop with safety limits.
    
    Args:
        user_question: The user's question
        max_iterations: Maximum number of tool calls before stopping (safety limit)
    """
    messages = [{"role": "user", "content": user_question}]
    iteration = 0
    
    print(f"\n{'='*60}")
    print(f"USER: {user_question}")
    print(f"{'='*60}\n")
    
    # Main agent loop
    while iteration < max_iterations:
        iteration += 1
        print(f"[Iteration {iteration}]")
        
        # Call Claude with tools
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        
        # Collect all tool calls from this response
        tool_uses = [block for block in response.content if block.type == "tool_use"]
        
        # If no tool calls, Claude is done
        if not tool_uses:
            print(f"[Claude finished]")
            for block in response.content:
                if block.type == "text":
                    print(f"\nCLAUDE: {block.text}")
            print(f"\n✓ Completed in {iteration} iterations")
            print(f"{'='*60}\n")
            break
        
        # Add Claude's response to messages
        messages.append({"role": "assistant", "content": response.content})
        
        # Execute all tools and collect results
        tool_results = []
        for tool_use in tool_uses:
            print(f"  → Calling: {tool_use.name}()")
            print(f"     Arguments: {json.dumps(tool_use.input, indent=6)}")
            
            result = execute_tool(tool_use.name, tool_use.input)
            print(f"     Result: {result}\n")
            
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            })
        
        # Add all tool results in one user message
        messages.append({
            "role": "user",
            "content": tool_results
        })
    
    # Check if we hit the iteration limit
    if iteration >= max_iterations:
        print(f"\n⚠ SAFETY LIMIT REACHED: Hit max_iterations ({max_iterations})")
        print(f"Agent stopped to prevent runaway loops.")
        print(f"Last Claude response:")
        for block in response.content:
            if block.type == "text":
                print(f"  {block.text}")
        print(f"{'='*60}\n")

# Main execution
if __name__ == "__main__":
    # Test Case 1: Simple refund question
    print("\n\nTEST 1: Simple question (should take 1-2 iterations)")
    agent_loop("What is the refund policy?", max_iterations=10)
    
    # Test Case 2: Complex question (should take 3-4 iterations)
    print("\nTEST 2: Complex question (should take 3-4 iterations)")
    agent_loop(
        "I bought something 45 days ago for $500. Can I get a refund? If yes, how much after fees?",
        max_iterations=10
    )
    
    # Test Case 3: Very complex (might hit iteration limit)
    print("\nTEST 3: Very complex question")
    agent_loop(
        "Tell me everything about return policies, check my eligibility, calculate my exact refund, and explain step by step why that's the amount.",
        max_iterations=5  # Lower limit to show how it handles limits
    )