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
  const [hasUnread, setHasUnread] = useState(true);
  const messagesEndRef = useRef(null);
  
  // Conversation memory to track context - MOVED TO COMPONENT LEVEL
  const conversationMemory = useRef({
    lastTopic: null,
    questionsAsked: 0,
    topics: new Set()
  });
  
  // API status reference - MOVED TO COMPONENT LEVEL
  const apiStatus = useRef({
    attemptCount: 0,
    successCount: 0,
    lastAttemptTime: null,
    lastSuccessTime: null,
    activeEndpoints: []
  });

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([{
        sender: "bot",
  text: "👋 Hi there! I'm Allu Bot. How can I assist you with tech questions or TechAssistant information today?"
      }]);
    }
  }, [isOpen, messages.length]);

  // Load API status from localStorage
  useEffect(() => {
    try {
      const storedStatus = localStorage.getItem('alluBotApiStatus');
      if (storedStatus) {
        const parsedStatus = JSON.parse(storedStatus);
        // Only use stored data if it's recent (last 24 hours)
        if (parsedStatus.lastAttemptTime && 
            (new Date().getTime() - new Date(parsedStatus.lastAttemptTime).getTime() < 24 * 60 * 60 * 1000)) {
          apiStatus.current = parsedStatus;
        }
      }
    } catch (e) {
      console.log("Error reading API status from localStorage:", e);
    }
  }, []);

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
      let data = null;
      let apiCallSucceeded = false;
      let foundSource = null;
      
      // Prepare the list of API endpoints to try
      const possibleBaseUrls = [
        process.env.REACT_APP_BACKEND_URL || '', // Use environment variable or fallback to relative
      ].filter(Boolean); // Remove empty values
      
      // Update the API attempt counter
      apiStatus.current.attemptCount++;
      apiStatus.current.lastAttemptTime = new Date().toISOString();
      
      // Try to use the API to get a response
      for (const baseUrl of possibleBaseUrls) {
        try {
          console.log(`Attempting API call to: ${baseUrl}/api/ask-all-u-bot`);
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 15000); // Increased timeout to 15s
          
          const response = await fetch(`${baseUrl}/api/ask-all-u-bot`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
              message: userInput
            }),
            credentials: 'omit',
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          
          if (response.ok) {
            console.log(`Successful response from: ${baseUrl}/api/ask-all-u-bot`);
            const responseText = await response.text();
            
            if (responseText && responseText.trim()) {
              try {
                const responseData = JSON.parse(responseText);
                if (responseData && responseData.reply && responseData.reply.trim()) {
                  data = {
                    reply: responseData.reply
                  };
                  
                  // Store the source if available
                  if (responseData.source) {
                    foundSource = responseData.source;
                  }
                  
                  apiCallSucceeded = true;
                  
                  // Record successful endpoint
                  if (baseUrl && !apiStatus.current.activeEndpoints?.includes(baseUrl)) {
                    apiStatus.current.activeEndpoints = [
                      ...(apiStatus.current.activeEndpoints || []),
                      baseUrl
                    ];
                  }
                  
                  apiStatus.current.successCount++;
                  apiStatus.current.lastSuccessTime = new Date().toISOString();
                  break; // Exit loop if we get a successful response with data
                }
              } catch (parseError) {
                console.error("Failed to parse response as JSON:", parseError);
              }
            } else {
              console.warn("Empty response received from server");
            }
          } else {
            console.log(`Failed with status ${response.status} from: ${baseUrl}/api/ask-all-u-bot`);
          }
        } catch (e) {
          console.log(`Error with ${baseUrl}/api/ask-all-u-bot:`, e.message);
        }
      }
      
      // Save updated API status to localStorage
      try {
        localStorage.setItem('alluBotApiStatus', JSON.stringify(apiStatus.current));
      } catch (e) {
        console.log("Error saving API status to localStorage:", e);
      }
      
      // If API calls failed, show error
      if (!apiCallSucceeded || !data) {
        data = {
          reply: "I'm sorry, I'm having trouble connecting to my brain right now. Please try again in a moment."
        };
        console.log("API failed, showing error message");
      }

      // Create the bot message, including source attribution if available
      let messageText = data.reply || "Sorry, I couldn't process your request.";
      
      // If we have a source from the internet, add attribution
      if (foundSource && foundSource !== "Portfolio" && foundSource !== "None" && foundSource.startsWith("http")) {
        try {
          messageText += `\n\n[Source: ${new URL(foundSource).hostname}]`;
        } catch (e) {
          // If URL construction fails, just add the raw source
        }
      }

      const botMessage = { 
        sender: "bot", 
        text: messageText,
        hasSource: !!foundSource
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
      handleSubmit({ preventDefault: () => {} });
      setSelectedSuggestion(null);
    }, 300);
  };
  
  return (
    <div className={`chatbot-container ${welcomeAnimation ? "welcome-animation" : ""}`}>

      {/* Chatbot Icon with Unread Badge and Avatar */}
      <div style={{position: 'relative', display: 'inline-block'}}>
        <button
          className={`chat-toggle-button${isOpen ? ' open' : ''}`}
          onClick={toggleChat}
          aria-label={isOpen ? 'Close chat' : 'Open chat'}
        >
          <img
            src="/profile-pic.jpg"
            alt="Allu Bot"
            className="chat-toggle-avatar"
            style={{width: 40, height: 40, borderRadius: '50%', objectFit: 'cover', background: '#fff'}}
            onError={e => { e.target.style.display = 'none'; }}
          />
          {/* Fallback SVG if image fails */}
          <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            width="32"
            height="32"
            style={{position: 'absolute', top: 4, left: 4, display: 'none'}}
          >
            <circle cx="12" cy="12" r="10" fill="#3b82f6" />
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="#fff" />
          </svg>
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
          
          <div className="chatbot-messages">
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
                      style={{
                        width: '100%',
                        height: '100%',
                        borderRadius: '50%',
                        objectFit: 'cover'
                      }}
                      onError={(e) => {
                        // Fallback to default avatar if image fails to load
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
                      style={{display: 'none'}}
                    >
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor"/>
                    </svg>
                  </div>
                )}
                <div className="message-content">{msg.text}</div>
                {msg.sender === "user" && (
                  <div className="user-avatar">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="currentColor"/>
                    </svg>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="chatbot-message bot">
                <div className="bot-avatar">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" width="24" height="24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="message-content typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          {/* Suggested questions */}
          {messages.length < 3 && (
            <div className="chatbot-suggestions">
              <div className="suggestion-buttons">
                <div className="max-h-20 overflow-y-auto pr-1 custom-scrollbar" style={{display: 'flex', flexWrap: 'wrap', gap: '6px'}}>
                  {suggestedQuestions.map((question, index) => (
                    <button 
                      key={index}
                      onClick={() => handleSuggestionClick(question)}
                      className={`suggestion-button ${selectedSuggestion === question ? 'selected' : ''}`}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          
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
                <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
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