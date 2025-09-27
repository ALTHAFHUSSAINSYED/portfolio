import React, { useState, useEffect, useRef } from "react";
import "./Chatbot.css";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [welcomeAnimation, setWelcomeAnimation] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Initialize with welcome message
  useEffect(() => {
    setMessages([{
      sender: "bot",
      text: "👋 Hi there! I'm Allu Bot. How can I assist you with tech questions or portfolio information today?"
    }]);

    const theme = document.documentElement.getAttribute("data-theme");
    document.documentElement.style.setProperty(
      "--chat-bg-color",
      theme === "dark" ? "var(--chat-bg-color-dark)" : "var(--chat-bg-color-light)"
    );
    document.documentElement.style.setProperty(
      "--chat-text-color",
      theme === "dark" ? "var(--chat-text-color-dark)" : "var(--chat-text-color-light)"
    );

    // Trigger welcome animation on page load
    const timer = setTimeout(() => setWelcomeAnimation(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  const toggleChat = () => setIsOpen(!isOpen);

  const handleInputChange = (e) => setInput(e.target.value);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    const userInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/ask-all-u-bot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput }),
      });

      const data = await response.json();
      const botMessage = { sender: "bot", text: data.reply || "Sorry, I couldn't process your request." };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error communicating with Allu Bot:", error);
      const errorMessage = { sender: "bot", text: "Sorry, there was an error processing your request. Please try again later." };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`chatbot-container ${welcomeAnimation ? "welcome-animation" : ""}`}>
      <button className="chatbot-toggle" onClick={toggleChat}>
        {isOpen ? "Close" : "Chat with Allu Bot 🤖"}
      </button>

      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div className="chatbot-title">Allu Bot</div>
            <button className="close-button" onClick={toggleChat}>×</button>
          </div>
          <div className="chatbot-messages">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`chatbot-message ${msg.sender}`}
              >
                {msg.text}
              </div>
            ))}
            {isLoading && (
              <div className="chatbot-message bot typing-indicator">
                <span></span><span></span><span></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          <form className="chatbot-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={input}
              onChange={handleInputChange}
              placeholder="Type your message..."
              className="chatbot-input"
            />
            <button type="submit" className="send-button">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Chatbot;