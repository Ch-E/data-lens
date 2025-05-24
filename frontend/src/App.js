import React, { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    { sender: "system", text: "Welcome to DataLens! Ask me about your transaction data." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setLoading(true);
    setInput("");
    try {
      const res = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      setMessages((msgs) => [...msgs, { sender: "bot", text: data.response }]);
    } catch {
      setMessages((msgs) => [...msgs, { sender: "bot", text: "Error contacting backend." }]);
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <aside className="sidebar">
        <h2>DataLens</h2>
        <div className="sidebar-footer">Powered by LLM + SQL</div>
      </aside>
      <main className="chat-main">
        <div className="chat-header">DataLens Chat</div>
        <div className="chat-window">
          {messages.map((msg, i) => (
            <div key={i} className={`msg ${msg.sender}`}>
              <span>{msg.text}</span>
            </div>
          ))}
          {loading && <div className="msg bot">Thinking...</div>}
        </div>
        <form className="chat-input" onSubmit={sendMessage}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question about transactions..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>Send</button>
        </form>
      </main>
    </div>
  );
}

export default App;
