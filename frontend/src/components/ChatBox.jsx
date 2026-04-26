import { useState } from "react";
import axios from "axios";
import ResultTable from "./ResultTable";
import Chart from "./Chart";

const API_URL = "https://sql-data-analyst-agent.onrender.com";

export default function ChatBox() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!question.trim()) return;

    const userMessage = { role: "user", content: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/query`, { question });
      const { answer, sql, chart, row_count } = response.data;

      const agentMessage = {
        role: "agent",
        answer,
        sql,
        chart,
        row_count,
      };

      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          answer: "Something went wrong. Please try again.",
          sql: "",
          chart: {},
          row_count: 0,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-container">
      {/* Messages */}
      <div className="messages">
        {messages.length === 0 && (
          <div className="empty-state">
            Ask anything about the Northwind database
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.role === "user" ? (
              <p>{msg.content}</p>
            ) : (
              <div className="agent-response">
                <p className="answer">{msg.answer}</p>

                {msg.chart?.chartable && <Chart chart={msg.chart} />}

                {msg.row_count > 0 && (
                  <details className="sql-details">
                    <summary>View SQL</summary>
                    <pre>{msg.sql}</pre>
                  </details>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message agent">
            <p className="loading">Thinking...</p>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="input-row">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your data..."
          rows={2}
        />
        <button onClick={handleSubmit} disabled={loading}>
          {loading ? "..." : "Ask"}
        </button>
      </div>
    </div>
  );
}
