
import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, X, Send, Loader2, Minimize2, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      content: "Hello! I am **Allu Bot**, Althaf's AI Assistant. Ask me anything about his skills, projects, or experience!"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const suggestedQuestions = [
    "Show me his recent blogs",
    "What are Althaf's skills?",
    "Tell me about his projects",
    "What DevOps tools does he use?",
    "Contact information"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (text) => {
    if (!text.trim() || isLoading) return;

    const userMessage = text;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Use relative path for production (requires proxy in package.json for local dev)
      const response = await fetch('/api/ask-all-u-bot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });

      const data = await response.json();

      if (response.ok) {
        setMessages(prev => [...prev, { role: 'bot', content: data.reply }]);
      } else {
        setMessages(prev => [...prev, { role: 'bot', content: "I encountered a server error. Please try again later." }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', content: "Network error. Is the backend server running?" }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSend(input);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end pointer-events-none">
      <div className="pointer-events-auto">
        <AnimatePresence>
          {isOpen && !isMinimized && (
            <motion.div
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 20, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="mb-4 w-[350px] sm:w-[400px] h-[500px] bg-white/80 dark:bg-black/80 backdrop-blur-xl border border-white/20 dark:border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
            >
              {/* Header */}
              <div className="p-4 border-b border-gray-200/50 dark:border-gray-700/50 bg-white/50 dark:bg-black/50 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 bg-blue-600 rounded-lg">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">Allu Bot</h3>
                    <p className="text-xs text-green-500 font-medium flex items-center gap-1">
                      <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                      Online
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setIsMinimized(true)}
                    className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                  >
                    <Minimize2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 text-gray-500 hover:bg-red-100 hover:text-red-500 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
                {messages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    <div className={`p-2 rounded-full shrink-0 ${msg.role === 'user'
                      ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                      : 'bg-blue-600 text-white'
                      }`}>
                      {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                    </div>
                    <div className={`max-w-[80%] rounded-2xl p-3 text-sm leading-relaxed shadow-sm ${msg.role === 'user'
                      ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded-tr-none'
                      : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-gray-700 rounded-tl-none'
                      }`}>
                      {msg.role === 'bot' ? (
                        <ReactMarkdown
                          className="prose dark:prose-invert prose-sm max-w-none"
                          components={{
                            code({ node, inline, className, children, ...props }) {
                              return !inline ? (
                                <div className="bg-gray-900 text-gray-100 rounded-md p-2 my-2 overflow-x-auto text-xs font-mono">
                                  {children}
                                </div>
                              ) : (
                                <code className="bg-gray-200 dark:bg-gray-700 px-1 py-0.5 rounded text-xs font-mono" {...props}>
                                  {children}
                                </code>
                              )
                            }
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        msg.content
                      )}
                    </div>
                  </motion.div>
                ))}

                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-start gap-3"
                  >
                    <div className="p-2 bg-blue-600 rounded-full shrink-0 text-white">
                      <Bot className="w-4 h-4" />
                    </div>
                    <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 p-3 rounded-2xl rounded-tl-none flex items-center gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    </div>
                  </motion.div>
                )}

                {/* Suggested Questions (only show if few messages or last was bot) */}
                {!isLoading && messages.length === 1 && (
                  <div className="flex flex-wrap gap-2 mt-4 px-2">
                    {suggestedQuestions.map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(q)}
                        className="text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 border border-blue-100 dark:border-blue-800 px-3 py-1.5 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors text-left"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <form onSubmit={handleSubmit} className="p-4 bg-white/50 dark:bg-black/50 border-t border-gray-200/50 dark:border-gray-700/50 backdrop-blur-md">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about Althaf's skills..."
                    className="flex-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all text-gray-900 dark:text-gray-100 placeholder-gray-400"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-lg shadow-blue-500/20"
                  >
                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  </button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Toggle Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => {
            setIsOpen(true);
            setIsMinimized(false);
          }}
          className={`
            p-4 rounded-2xl shadow-2xl transition-all duration-300 group relative
            ${isOpen && !isMinimized
              ? 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 opacity-0 pointer-events-none'
              : 'bg-blue-600 text-white hover:bg-blue-700 opacity-100'
            }
          `}
        >
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-gray-900" />
          <MessageSquare className="w-6 h-6" />
        </motion.button>
      </div>
    </div>
  );
}