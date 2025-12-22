import React, { useState, useEffect, useRef } from "react";
import "./Chatbot.css";
import "./ChatbotExtras.css";
import "./ChatbotUnread.css";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [welcomeAnimation, setWelcomeAnimation] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [hasUnread, setHasUnread] = useState(true);
  const messagesEndRef = useRef(null);

  // ... (existing code)

  // Scroll to bottom only for new messages (skip initial load to keep greeting visible)
  useEffect(() => {
    if (messages.length > 1) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setShowSuggestions(false); // Hide suggestions on first interaction

    // ... (rest of handleSubmit)
  };

  // ...

  const handleSuggestionClick = (question) => {
    setShowSuggestions(false); // Hide suggestions immediately
    setInput(question);
    setSelectedSuggestion(question);
    // Auto submit after a slight delay for better UX
    setTimeout(() => {
      handleSubmit({ preventDefault: () => { } });
      setSelectedSuggestion(null);
    }, 300);
  };

  // ...

  {/* Suggested questions - visible only until interaction */ }
  {
    showSuggestions && (
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
    )
  }
  <div ref={messagesEndRef} />
          </div >

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
        </div >
      )}
    </div >
  );
}

export default Chatbot;