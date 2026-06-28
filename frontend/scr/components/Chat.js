import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import "./Chat.css";
import { FiSend, FiRefreshCw } from "react-icons/fi";
import { api } from "../api";

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your Claims Reprocessing Agent. How can I help you today? You can ask me to:\n• Reprocess a claim\n• Check claim status\n• Analyze claim details\n• Generate reports",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);
    setError("");

    try {
      const response = await api.post(`/api/chat`, {
        message: inputValue,
        history: messages,
      });

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: "bot",
        timestamp: new Date(),
        details: response.data.details,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Failed to send message. Make sure the backend is running.",
      );
      console.error("Error sending message:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([
      {
        id: 1,
        text: "Chat cleared. How can I assist you?",
        sender: "bot",
        timestamp: new Date(),
      },
    ]);
    setError("");
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Claim Reprocessing Agent</h2>
        <button
          className="clear-button"
          onClick={handleClear}
          title="Clear chat"
        >
          <FiRefreshCw size={18} />
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            <div className="message-content">
              <div className="message-text">
                {message.sender === "bot"
                  ? <ReactMarkdown>{message.text}</ReactMarkdown>
                  : message.text}
              </div>
              {message.details && (
                <div className="message-details">
                  <pre>{JSON.stringify(message.details, null, 2)}</pre>
                </div>
              )}
              <span className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <div className="input-group">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Ask about claim reprocessing, status, or analysis..."
            disabled={loading}
            className="message-input"
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !inputValue.trim()}
            className="send-button"
          >
            <FiSend size={20} />
          </button>
        </div>
        <div className="quick-actions">
          <button onClick={() => setInputValue("Check status of all claims")}>
            📋 Check Claims
          </button>
          <button onClick={() => setInputValue("Reprocess claim 1")}>
            🔄 Reprocess Claim 1
          </button>
          <button onClick={() => setInputValue("Generate claim analytics report")}>
            📊 Analytics
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
