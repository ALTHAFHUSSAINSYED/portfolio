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
      // Set up smart fallback responses
      const getFallbackResponse = (input) => {
        // Predefined responses to common queries
        const responses = {
          greetings: {
            match: /^(hi|hello|hey|greetings|howdy|hola)/i,
            replies: [
              "Hello there! I'm Allu Bot, your friendly portfolio assistant. How can I help you today?",
              "Hi! Welcome to Althaf's portfolio. What would you like to know about his skills or projects?",
              "Hey! Great to meet you. Feel free to ask about Althaf's work, technologies, or experience!"
            ]
          },
          about: {
            match: /^(who|what|tell me about|about)/i,
            replies: [
              "I'm Allu Bot, an AI assistant for Althaf Hussain Syed's portfolio. Althaf is a skilled developer with expertise in web development, cloud technologies, and DevOps.",
              "Althaf Hussain Syed is a developer with strong skills in React, Node.js, Python, and cloud technologies. His portfolio showcases various projects demonstrating these skills."
            ]
          },
          skills: {
            match: /^(skills|technologies|tech stack|what can you|what do you know)/i,
            replies: [
              "Althaf works with React, Node.js, Python, MongoDB, AWS, Azure, and various DevOps tools. Which technology would you like to know more about?",
              "The tech stack includes: React/Next.js for frontend, Node.js/Python for backend, MongoDB/PostgreSQL for databases, and AWS/Azure for cloud deployment."
            ]
          },
          projects: {
            match: /^(projects|work|portfolio|showcase)/i,
            replies: [
              "Althaf's portfolio includes web applications, automation tools, and cloud-based solutions. You can explore the projects section on this website for details.",
              "Check out the Projects section for a showcase of work including this portfolio site, e-commerce platforms, and various technical implementations."
            ]
          },
          default: {
            replies: [
              "I'm designed to answer questions about Althaf's portfolio and skills. Could you try asking something more specific?",
              "I can tell you about Althaf's projects, skills, and experience. What would you like to know?",
              "I'd be happy to help with information about Althaf's work and skills. Could you rephrase your question?"
            ]
          }
        };

        // Try to match input to a category
        for (const [category, data] of Object.entries(responses)) {
          if (category !== 'default' && data.match.test(input)) {
            return { reply: data.replies[Math.floor(Math.random() * data.replies.length)] };
          }
        }

        // Default response if no matches
        const defaultReplies = responses.default.replies;
        return { reply: defaultReplies[Math.floor(Math.random() * defaultReplies.length)] };
      };
      
      // Try to use the API first
      let data = null;
      let apiCallSucceeded = false;
      
      // Try each possible endpoint URL
      const possibleBaseUrls = [
        '', // Same domain (relative URL)
        'https://althaf-portfolio.onrender.com',
        'https://althaf-portfolio.vercel.app',
        'http://localhost:5000'
      ];
      
      for (const baseUrl of possibleBaseUrls) {
        try {
          console.log(`Attempting API call to: ${baseUrl}/api/ask-all-u-bot`);
          const response = await fetch(`${baseUrl}/api/ask-all-u-bot`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userInput }),
            credentials: 'omit',
            signal: AbortSignal.timeout(3000) // Reduced timeout to 3 seconds
          });
          
          if (response.ok) {
            console.log(`Successful response from: ${baseUrl}/api/ask-all-u-bot`);
            const responseText = await response.text();
            console.log('Response text:', responseText);
            
            if (responseText && responseText.trim()) {
              try {
                data = JSON.parse(responseText);
                apiCallSucceeded = true;
                break; // Exit loop if we get a successful response with data
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
      
      // If API calls failed, use local fallback system
      if (!apiCallSucceeded || !data) {
        data = getFallbackResponse(userInput);
        console.log("Using local fallback system for response");
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