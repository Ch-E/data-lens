from flask import Flask, request, jsonify
from flask_cors import CORS
from strands import Agent
from strands.models.anthropic import AnthropicModel
import os

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

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    # Use Strands agent to get a response
    response = agent(user_message)
    return jsonify({"response": str(response)})

if __name__ == "__main__":
    app.run(debug=True, port=5000) 