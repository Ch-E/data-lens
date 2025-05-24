from flask import Flask, request, jsonify
from flask_cors import CORS
from strands import Agent
from strands.models.anthropic import AnthropicModel
import os
import asyncio
from mssql_mcp_server.server import app as mcp_server, list_tools, call_tool
import json

app = Flask(__name__)
CORS(app)

# Set up the Anthropic model (Claude) for Strands
model = AnthropicModel(
    client_args={
        "api_key": os.environ.get("ANTHROPIC_API_KEY", "<YOUR_API_KEY>")
    },
    max_tokens=1028,
    model_id="claude-3-7-sonnet-20250219",
    params={
        "temperature": 0.7,
    }
)
agent = Agent(model=model)

async def get_mcp_context(prompt: str) -> str:
    """Get context from MCP server for a given prompt."""
    try:
        # First, ask Claude if we need MCP context
        context_check_prompt = f"""Given the following user prompt, determine if it requires database context from our SQL Server.
        If it does, respond with 'NEED_CONTEXT' followed by a brief explanation of what context is needed.
        If it doesn't, respond with 'NO_CONTEXT' followed by a brief explanation.
        
        User prompt: {prompt}
        
        Respond in exactly this format:
        DECISION: [NEED_CONTEXT or NO_CONTEXT]
        EXPLANATION: [brief explanation]"""
        
        context_check = agent(context_check_prompt)
        response_text = str(context_check)
        
        if "NEED_CONTEXT" in response_text:
            # If we need context, execute a relevant SQL query
            # For now, we'll use a simple query to get table information
            # In a real implementation, you'd want to make this more sophisticated
            tools = await list_tools()
            if tools and tools[0].name == "execute_sql":
                # Execute a query to get table information
                result = await call_tool("execute_sql", {
                    "query": """
                    SELECT TOP 5 TABLE_NAME, TABLE_SCHEMA 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE'
                    """
                })
                if result:
                    return f"Database context:\n{result[0].text}"
        
        return ""
    except Exception as e:
        print(f"Error getting MCP context: {str(e)}")
        return ""

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    # Get MCP context if needed
    context = asyncio.run(get_mcp_context(user_message))
    
    # Prepare the final prompt with context if available
    if context:
        final_prompt = f"""Context from database:
{context}

User message: {user_message}

Please provide a response that takes into account both the database context and the user's question."""
    else:
        final_prompt = user_message
    
    # Use Strands agent to get a response
    response = agent(final_prompt)
    return jsonify({"response": str(response)})

if __name__ == "__main__":
    app.run(debug=True, port=5000) 