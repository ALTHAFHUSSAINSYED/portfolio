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
    if (isOpen && messages.length === 0) {
      setMessages([{
        sender: "bot",
        text: "👋 Hi there! I'm Allu Bot. How can I assist you with tech questions or portfolio information today?"
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
      // For testing/fallback when API is unavailable
      const fallbackResponse = {
        reply: `I understand you asked about "${userInput}", but I'm currently having trouble connecting to my knowledge base. Please try again shortly.`
      };
      
      // Try multiple possible endpoints to handle different deployment configurations
      const possibleBaseUrls = [
        '', // Same domain (relative URL)
        'https://althaf-portfolio.onrender.com',
        'https://althaf-portfolio.vercel.app',
        'http://localhost:5000'
      ];
      
      let response = null;
      let apiCallSucceeded = false;
      
      // Try each possible URL until one works
      for (const baseUrl of possibleBaseUrls) {
        try {
          console.log(`Attempting API call to: ${baseUrl}/api/ask-all-u-bot`);
          const tempResponse = await fetch(`${baseUrl}/api/ask-all-u-bot`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput }),
            credentials: 'omit', // Don't send credentials to avoid CORS issues
            signal: AbortSignal.timeout(5000) // 5 second timeout per attempt
          });
          
          if (tempResponse.ok) {
            console.log(`Successful response from: ${baseUrl}/api/ask-all-u-bot`);
            response = tempResponse;
            apiCallSucceeded = true;
            break;
          } else {
            console.log(`Failed with status ${tempResponse.status} from: ${baseUrl}/api/ask-all-u-bot`);
          }
        } catch (e) {
          console.log(`Error with ${baseUrl}/api/ask-all-u-bot:`, e.message);
          // Continue to next URL
        }
      }

      // If no API call succeeded, use fallback
      let data = fallbackResponse;
      
      if (apiCallSucceeded && response) {
        try {
          const responseText = await response.text();
          console.log('Response text:', responseText);
          
          if (responseText && responseText.trim()) {
            try {
              data = JSON.parse(responseText);
            } catch (parseError) {
              console.error("Failed to parse response as JSON:", parseError);
              // Use fallback if JSON parsing fails
              data = fallbackResponse;
            }
          } else {
            console.warn("Empty response received from server");
            data = fallbackResponse;
          }
        } catch (readError) {
          console.error("Error reading response:", readError);
          data = fallbackResponse;
        }
      }

      const botMessage = { 
        sender: "bot", 
        text: data.reply || "Sorry, I couldn't process your request." 
      };
      setMessages((prev) => [...prev, botMessage]);
      
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

  return (
    <div className={`chatbot-container ${welcomeAnimation ? "welcome-animation" : ""}`}>
      <button 
        className="chatbot-toggle" 
        onClick={toggleChat}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? "×" : "💬"}
      </button>

      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div className="chatbot-title">Allu Bot</div>
            <button className="close-button" onClick={toggleChat} aria-label="Close chat">×</button>
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