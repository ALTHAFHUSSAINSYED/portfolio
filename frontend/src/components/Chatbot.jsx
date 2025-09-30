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
      // Set up enhanced local knowledge base
      const getFallbackResponse = (input) => {
        // Update conversation memory
        conversationMemory.current.questionsAsked++;
        
        // Convert input to lowercase for easier matching
        const inputLower = input.toLowerCase();
        
  // Comprehensive knowledge base about Althaf and TechAssistant
        const knowledgeBase = {
          profile: {
            name: "Althaf Hussain Syed",
            role: "Full Stack Developer & DevOps Engineer",
            summary: "Passionate about building scalable web applications and implementing efficient CI/CD pipelines",
            experience: "Over 5 years of experience in software development, cloud architecture, and DevOps practices",
            education: "Bachelor's degree in Computer Science with specialization in Software Engineering"
          },
          
          skills: {
            frontend: ["React", "Next.js", "JavaScript", "TypeScript", "HTML/CSS", "Tailwind CSS", "Material UI"],
            backend: ["Node.js", "Express", "Python", "Flask", "FastAPI", "RESTful API design"],
            database: ["MongoDB", "PostgreSQL", "MySQL", "Redis", "Database design & optimization"],
            devops: ["AWS", "Azure", "Docker", "Kubernetes", "CI/CD", "GitHub Actions", "Terraform"],
            other: ["Git", "Agile methodologies", "Testing", "System design", "Problem-solving"]
          },
          
          projects: [
            {
              name: "TechAssistant Website",
              tech: "React, Tailwind CSS, Node.js, MongoDB",
              description: "Interactive TechAssistant with chatbot integration showcasing projects and skills"
            },
            {
              name: "Cloud-based CI/CD Pipeline",
              tech: "AWS, Docker, Kubernetes, GitHub Actions",
              description: "Automated deployment workflow for microservice applications"
            },
            {
              name: "E-commerce Platform",
              tech: "Next.js, MongoDB, Stripe, Auth0",
              description: "Full-featured online store with secure payment processing"
            }
          ],
          
          contactInfo: {
            email: "Available through the contact form on the website",
            github: "ALTHAFHUSSAINSYED",
            linkedin: "Available on the TechAssistant site"
          }
        };
        
        // Define response categories with advanced pattern matching
        const responses = {
          greetings: {
            match: /^(hi|hello|hey|greetings|howdy|hola|good morning|good afternoon|good evening|hi there|hello there)/i,
            replies: [
              "Hello there! I'm Allu Bot, your friendly TechAssistant. How can I help you today?",
              "Hi! Welcome to Althaf's TechAssistant. What would you like to know about his skills or projects?",
              "Hey! Great to meet you. Feel free to ask about Althaf's work, technologies, or experience!"
            ]
          },
          
          about: {
            match: /^(who|what|tell me about|about|describe|introduce|background|info about).*(althaf|you|himself|techassistant owner|developer|creator)/i,
            replies: [
              `${knowledgeBase.profile.name} is a ${knowledgeBase.profile.role} with ${knowledgeBase.profile.experience}. ${knowledgeBase.profile.summary}.`,
              `Althaf Hussain Syed is a developer specializing in full-stack development and DevOps. He has experience with ${knowledgeBase.skills.frontend.slice(0,3).join(", ")} on the frontend and ${knowledgeBase.skills.backend.slice(0,3).join(", ")} on the backend.`
            ]
          },
          
          experience: {
            match: /^(experience|work history|background|career|job|professional)/i,
            replies: [
              `Althaf has ${knowledgeBase.profile.experience}, focusing on web development and cloud infrastructure. He's worked on various projects including ${knowledgeBase.projects[0].name} and ${knowledgeBase.projects[1].name}.`,
              `With ${knowledgeBase.profile.experience}, Althaf has developed expertise in both frontend and backend technologies, as well as cloud deployment and DevOps practices.`
            ]
          },
          
          education: {
            match: /^(education|degree|study|college|university|academic)/i,
            replies: [
              `Althaf has ${knowledgeBase.profile.education}, which provided a strong foundation for his software development career.`,
              `His educational background includes ${knowledgeBase.profile.education}, complemented by continuous learning and staying updated with industry trends.`
            ]
          },
          
          frontend: {
            match: /^(frontend|front-end|front end|ui|user interface|react|javascript|web design)/i,
            replies: [
              `For frontend development, Althaf works with ${knowledgeBase.skills.frontend.join(", ")}. His projects like ${knowledgeBase.projects[0].name} showcase his frontend skills.`,
              `Althaf's frontend stack includes ${knowledgeBase.skills.frontend.join(", ")}, with a focus on building responsive and user-friendly interfaces.`
            ]
          },
          
          backend: {
            match: /^(backend|back-end|back end|server|api|database|node|python|express)/i,
            replies: [
              `Althaf's backend expertise includes ${knowledgeBase.skills.backend.join(", ")} and database technologies like ${knowledgeBase.skills.database.slice(0,3).join(", ")}.`,
              `For backend development, Althaf uses ${knowledgeBase.skills.backend.slice(0,3).join(", ")}, designing scalable APIs and efficient database structures with ${knowledgeBase.skills.database.slice(0,3).join(", ")}.`
            ]
          },
          
          devops: {
            match: /^(devops|deployment|cloud|aws|azure|docker|kubernetes|ci\/cd|pipeline|infrastructure)/i,
            replies: [
              `Althaf has strong DevOps skills with ${knowledgeBase.skills.devops.join(", ")}. His ${knowledgeBase.projects[1].name} project demonstrates his DevOps capabilities.`,
              `In the DevOps realm, Althaf works with ${knowledgeBase.skills.devops.join(", ")}, implementing automated pipelines and cloud infrastructure.`
            ]
          },
          
          projects: {
            match: /^(projects|techassistant|work|showcase|applications|apps)/i,
            replies: [
              `Althaf's notable projects include: 1) ${knowledgeBase.projects[0].name} using ${knowledgeBase.projects[0].tech} - ${knowledgeBase.projects[0].description}, 2) ${knowledgeBase.projects[1].name} using ${knowledgeBase.projects[1].tech} - ${knowledgeBase.projects[1].description}, and 3) ${knowledgeBase.projects[2].name} using ${knowledgeBase.projects[2].tech} - ${knowledgeBase.projects[2].description}.`,
              `The TechAssistant showcases several projects including ${knowledgeBase.projects[0].name}, ${knowledgeBase.projects[1].name}, and ${knowledgeBase.projects[2].name}, demonstrating various technical skills from frontend to DevOps.`
            ]
          },
          
          contact: {
            match: /^(contact|reach|email|github|linkedin|social|get in touch)/i,
            replies: [
              `You can contact Althaf through the contact form on this website. His GitHub username is ${knowledgeBase.contactInfo.github}, and LinkedIn is available in the contact section.`,
              `For professional inquiries, please use the contact form on this website. Althaf can also be found on GitHub as ${knowledgeBase.contactInfo.github}.`
            ]
          },
          
          specificProject: {
            match: /(e-commerce|store|shop|payment)/i,
            replies: [
              `The ${knowledgeBase.projects[2].name} is built with ${knowledgeBase.projects[2].tech}. ${knowledgeBase.projects[2].description}.`,
              `Althaf developed an e-commerce platform using ${knowledgeBase.projects[2].tech}, featuring secure payments, user authentication, and product management.`
            ]
          },
          
          chatbot: {
            match: /(chatbot|chat bot|bot|ai|yourself|talking to|speaking with|assistant)/i,
            replies: [
              "I'm Allu Bot, a specialized AI assistant built for Althaf's TechAssistant website. While I have limited internet access, I can answer questions about Althaf's skills, projects, and experience.",
              "I'm a custom AI assistant for this TechAssistant. I can tell you about Althaf's work, skills, and projects, though my knowledge is primarily focused on information contained in this TechAssistant."
            ]
          },
          
          thanks: {
            match: /^(thanks|thank you|appreciate|helpful|great)/i,
            replies: [
              "You're welcome! I'm glad I could help. Feel free to ask if you have any other questions about Althaf's work or skills.",
              "Happy to help! If you need any more information about Althaf's TechAssistant or experience, just let me know.",
              "My pleasure! Is there anything else you'd like to know about Althaf's projects or technical background?"
            ]
          },
          
          default: {
            replies: [
              "I'm designed to answer questions about Althaf's TechAssistant and skills. Could you try asking something more specific about his work, projects, or technical expertise?",
              "I can tell you about Althaf's projects, skills, and experience. What specific aspect of his professional background would you like to know about?",
              "I'd be happy to help with information about Althaf's work and skills. For best results, try asking about specific technologies, projects, or areas of expertise."
            ]
          }
        };

        // Check for context-aware responses based on conversation history
        if (conversationMemory.current.questionsAsked > 1) {
          // If user has asked multiple short questions, try to be more helpful
          if (input.length < 10) {
            if (conversationMemory.current.lastTopic === "projects") {
              return { reply: `Regarding Althaf's projects, he has worked on ${knowledgeBase.projects.map(p => p.name).join(", ")}. Which one would you like to know more about?` };
            }
            if (conversationMemory.current.lastTopic === "skills") {
              return { reply: `About Althaf's skills, he specializes in frontend (${knowledgeBase.skills.frontend.slice(0,3).join(", ")}), backend (${knowledgeBase.skills.backend.slice(0,3).join(", ")}), and DevOps (${knowledgeBase.skills.devops.slice(0,3).join(", ")}). Would you like more details on any of these areas?` };
            }
          }
        }

        // Try to match input to a category
        for (const [category, data] of Object.entries(responses)) {
          if (category !== 'default' && data.match.test(inputLower)) {
            conversationMemory.current.lastTopic = category;
            conversationMemory.current.topics.add(category);
            return { reply: data.replies[Math.floor(Math.random() * data.replies.length)] };
          }
        }

        // Check for technology mentions
        const techKeywords = {
          react: "React is one of Althaf's core frontend skills. He uses it for building interactive user interfaces, including this TechAssistant website.",
          node: "Node.js is part of Althaf's backend stack, used for building scalable server-side applications and APIs.",
          python: "Python is among Althaf's backend technologies, particularly with frameworks like Flask and FastAPI for web services.",
          aws: "Althaf has experience with AWS for cloud deployment, including services like EC2, S3, Lambda, and more.",
          azure: "Azure is part of Althaf's cloud expertise, used for deploying applications and implementing DevOps practices.",
          docker: "Althaf uses Docker for containerization, ensuring consistent environments across development and production.",
          kubernetes: "Kubernetes is part of Althaf's DevOps toolkit, used for container orchestration in his cloud projects."
        };

        for (const [tech, response] of Object.entries(techKeywords)) {
          if (inputLower.includes(tech)) {
            return { reply: response };
          }
        }

        // Default response if no matches
        const defaultReplies = responses.default.replies;
        return { reply: defaultReplies[Math.floor(Math.random() * defaultReplies.length)] };
      };
      
      // Detect if the query is asking for internet information
      const requiresInternet = (query) => {
        const internetQueries = [
          /current|latest|news|today|update|recent/i,
          /weather|forecast/i,
          /stock|market|price/i,
          /search|find|look up|google/i,
          /what is|who is|tell me about/i,
          /how to|how do/i
        ];
        
        return internetQueries.some(pattern => pattern.test(query));
      };
      
      let data = null;
      let apiCallSucceeded = false;
      let foundSource = null;
      
      // Determine if we should try to get an internet-based response
      const needsInternetResponse = requiresInternet(userInput);
      console.log(`Query "${userInput}" - Needs internet access: ${needsInternetResponse}`);
      
      // Prepare the list of API endpoints to try
      const possibleBaseUrls = [
        '', // Same domain (relative URL)
        ...(apiStatus.current.activeEndpoints || []),
        'https://althaf-portfolio.onrender.com',
        'https://althaf-portfolio.vercel.app',
        'http://localhost:5000'
      ].filter((url, index, self) => self.indexOf(url) === index); // Remove duplicates
      
      // Update the API attempt counter
      apiStatus.current.attemptCount++;
      apiStatus.current.lastAttemptTime = new Date().toISOString();
      
      // Try to use the API to get a response
      for (const baseUrl of possibleBaseUrls) {
        try {
          console.log(`Attempting API call to: ${baseUrl}/api/ask-all-u-bot`);
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000); // 5-second timeout
          
          const response = await fetch(`${baseUrl}/api/ask-all-u-bot`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
              message: userInput,
              context: needsInternetResponse ? "internet_required" : "portfolio_info" 
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
      
      // If API calls failed, use local fallback system
      if (!apiCallSucceeded || !data) {
        // If internet information was requested but unavailable, inform the user
        if (needsInternetResponse) {
          data = {
            reply: "I'd like to answer that question, but I need internet access which is currently unavailable. I can tell you about Althaf's skills, projects, or experience instead."
          };
        } else {
          // Otherwise use standard local fallback
          data = getFallbackResponse(userInput);
        }
        console.log("Using local fallback system for response");
      }

      // Create the bot message, including source attribution if available
      let messageText = data.reply || "Sorry, I couldn't process your request.";
      
      // If we have a source from the internet, add attribution
  if (foundSource && foundSource !== "TechAssistant" && foundSource !== "None" && foundSource.startsWith("http")) {
        try {
          messageText += `\n\n[Source: ${new URL(foundSource).hostname}]`;
        } catch (e) {
          // If URL construction fails, just add the raw source
          messageText += `\n\n[Source: ${foundSource}]`;
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
    "What are Althaf's skills?",
    "Tell me about his projects",
    "What DevOps tools does he use?",
    "Show me his recent blogs",
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
      <button 
        className="chatbot-toggle" 
        onClick={toggleChat}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? "×" : (
          <div className="chat-icon-container">
            {hasUnread && <div className="unread-indicator">1</div>}
            <img 
              src="/profile-pic.jpg" 
              alt="Chat with Althaf" 
              className="chat-toggle-avatar"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <svg 
              viewBox="0 0 24 24" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg" 
              className="chat-toggle-fallback"
              style={{display: 'none'}}
            >
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor"/>
            </svg>
          </div>
        )}

      {/* Chatbot Icon with Unread Badge */}
      <div style={{position: 'relative', display: 'inline-block'}}>
        <button
          className={`chat-toggle-button${isOpen ? ' open' : ''}`}
          onClick={toggleChat}
          aria-label={isOpen ? 'Close chat' : 'Open chat'}
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            width="32"
            height="32"
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
            <div className="chatbot-avatar">
              {hasUnread && <div className="unread-indicator">1</div>}
              <svg 
                viewBox="0 0 24 24" 
                fill="none" 
                xmlns="http://www.w3.org/2000/svg" 
                width="24" 
                height="24"
                style={{display: 'block'}}
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z" fill="currentColor"/>
              </svg>
            </div>
            <div className="chatbot-title-container">
              <div className="chatbot-title">Allu Bot</div>
              <div className="chatbot-subtitle">Portfolio & Tech Assistant</div>
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
              <p className="suggestion-title">Try asking:</p>
              <div className="suggestion-buttons">
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
};

export default Chatbot;