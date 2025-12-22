import React, { useState, useEffect, useRef } from "react";
import "./Chatbot.css";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [welcomeAnimation, setWelcomeAnimation] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [hasUnread, setHasUnread] = useState(true);
  const messagesEndRef = useRef(null);

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([{
        sender: "bot",
        text: "👋 Hi there! I'm Allu Bot. How can I assist you with tech questions or TechAssistant information today?"
      }]);
    }
  }, [isOpen, messages.length]);

  useEffect(() => {
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

  const toggleChat = () => {
    if (!isOpen) {
      setHasUnread(false); // Clear unread indicator when opening chat
    }
    setIsOpen(!isOpen);
  };

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
      // Use the new RAG backend endpoint
      const response = await fetch('/api/ask-all-u-bot', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
      });

      if (response.ok) {
        const data = await response.json();
        const botMessage = {
          sender: "bot",
          text: data.reply || "Sorry, I couldn't process your request."
        };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        const errorMessage = {
          sender: "bot",
          text: "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment."
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Error communicating with Allu Bot:", error);
      const errorMessage = {
        sender: "bot",
        text: "Sorry, there was an error connecting to the server. Please try again later."
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Common questions suggestions
  const suggestedQuestions = [
    "Show me his recent blogs",
    "What are Althaf's skills?",
    "Tell me about his projects",
    "What DevOps tools does he use?",
    "Contact information"
  ];

  const [selectedSuggestion, setSelectedSuggestion] = useState(null);

  const handleSuggestionClick = (question) => {
    setInput(question);
    setSelectedSuggestion(question);
    // Auto submit after a slight delay for better UX
    setTimeout(() => {
      handleSubmit({ preventDefault: () => { } });
      setSelectedSuggestion(null);
    }, 300);
  };

  return (
    <div className={`chatbot-container ${welcomeAnimation ? "welcome-animation" : ""}`}>

      {/* Chatbot Icon with Unread Badge and Avatar */}
      <div style={{ position: 'relative', display: 'inline-block' }}>
        <button
          className="chatbot-toggle"
          onClick={toggleChat}
          aria-label={isOpen ? 'Close chat' : 'Open chat'}
        >
          <div className="chat-icon-container">
            <img
              src="/profile-pic.jpg"
              alt="Allu Bot"
              className="chat-toggle-avatar"
              onError={e => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
            {/* Fallback SVG if image fails */}
            <svg
              className="chat-toggle-fallback"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{ display: 'none' }}
            >
              <circle cx="12" cy="12" r="10" fill="#3b82f6" />
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="#fff" />
            </svg>
          </div>
          {/* Red unread badge */}
          {!isOpen && hasUnread && (
            <span style={{
              position: 'absolute',
              top: '-6px',
              right: '-6px',
              background: 'red',
              color: 'white',
              borderRadius: '50%',
              padding: '2px 6px',
              fontSize: '14px',
              fontWeight: 'bold',
              boxShadow: '0 0 4px rgba(0,0,0,0.2)',
              zIndex: 2
            }}>
              1
            </span>
          )}
        </button>
      </div>

      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div className="chatbot-avatar" aria-hidden="true">
              <img
                src="/profile-pic.jpg"
                alt="Allu Bot"
                onError={(e) => {
                  e.target.style.display = "none";
                  if (e.target.nextSibling) {
                    e.target.nextSibling.style.display = "block";
                  }
                }}
              />
              <svg
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{ display: "none" }}
              >
                <circle cx="12" cy="12" r="10" fill="#3b82f6" />
                <path
                  d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
                  fill="#fff"
                />
              </svg>
            </div>
            <div className="chatbot-title-container">
              <p className="chatbot-title">Allu Bot</p>
              <p className="chatbot-subtitle">Portfolio & Tech Assistant</p>
            </div>
            <button className="close-button" onClick={toggleChat} aria-label="Close chat">×</button>
          </div>

          <div className="chatbot-messages custom-scrollbar">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`chatbot-message ${msg.sender}`}
              >
                {msg.sender === "bot" && (
                  <div className="bot-avatar">
                    <img
                      src="/profile-pic.jpg"
                      alt="Allu Bot"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'block';
                      }}
                    />
                    <svg
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      width="24"
                      height="24"
                      style={{ display: 'none' }}
                    >
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor" />
                    </svg>
                  </div>
                )}
                <div className="message-content">{msg.text}</div>
                {msg.sender === "user" && (
                  <div className="user-avatar">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="currentColor" />
                    </svg>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="chatbot-message bot">
                <div className="bot-avatar">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor" />
                  </svg>
                </div>
                <div className="message-content typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}

            {/* Suggested questions - inside messages area */}
            {messages.length < 3 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(question)}
                    className="suggestion-button"
                  >
                    {question}
                  </button>
                ))}
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
              aria-label="Message input"
            />
            <button type="submit" className="send-button" aria-label="Send message">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </form>

          <div className="chatbot-footer">
            <span>Powered by AI • <a href="#" onClick={(e) => {
              e.preventDefault();
              handleSuggestionClick("How does this chatbot work?");
            }}>About this bot</a></span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chatbot;