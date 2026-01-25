// src/components/ChatContainer.jsx - Updated
import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import AudioPlayer from './AudioPlayer';
import { sendMessage } from '../api/chat';
import './ChatContainer.css';

// Add this at the top after imports
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1';
const BACKEND_URL = API_BASE_URL.replace('/api/v1', ''); // Gets base backend URL



const ChatContainer = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;
    
    // Add user message with timestamp
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: text,
      timestamp: new Date()
    }]);
    
    setLoading(true);
    
    try {
      // Send to API and get response
      const response = await sendMessage(text);
      
      // Add assistant message
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.message,
        formattedResponse: response.formatted_response,
        timestamp: new Date()
      }]);
      
      // Set audio URL for playback if available
      if (response.audio_url) {
        setTimeout(() => {
          setCurrentAudio(`${BACKEND_URL}${response.audio_url}`);
        }, 500);
      }
    } catch (error) {
      console.error('Error getting response:', error);
      
      let errorMessage = 'Sorry, I encountered an error processing your request.';
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = '⏰ Request timed out. Please try again with a shorter query.';
      } else if (error.response) {
        // Server responded with error status
        errorMessage = `Server error: ${error.response.status}. Please try again.`;
      } else if (error.request) {
        // Network error
        errorMessage = '🌐 Network error. Please check your connection and try again.';
      }
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: errorMessage,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Handle prompt card clicks
  const handlePromptClick = (promptText) => {
    handleSendMessage(promptText);
  };

  return (
    <div className="chatgpt-container">
      {/* Header */}
      <header className="chat-header">
        <div className="header-branding">
          <div className="header-icon">⚕️</div>
          <h1>Health Informatics Agent</h1>
        </div>
        {messages.length > 0 && (
          <button className="new-chat-btn" onClick={() => setMessages([])}>
            New Chat
          </button>
        )}
      </header>

      {/* Main chat area */}
      <div className="chat-main">
        {messages.length === 0 ? (
          // Initial empty state
          <div className="chat-empty-state">
            <div className="empty-state-content">
              <div className="empty-state-icon">🩺</div>
              <h1>How can I help with patient data?</h1>
              <p>I can analyze records, summarize treatments, and visualize medical history.</p>
              <div className="example-prompts">
                <div 
                  className="prompt-card"
                  onClick={() => handlePromptClick("Show me treatment history for patient p_1001")}
                >
                  <span>Show me treatment history for patient p_1001</span>
                </div>
                <div 
                  className="prompt-card"
                  onClick={() => handlePromptClick("What are the pathology results?")}
                >
                  <span>What are the pathology results?</span>
                </div>
                <div 
                  className="prompt-card"
                  onClick={() => handlePromptClick("Get patient registration details")}
                >
                  <span>Get patient registration details</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          // Messages area
          <div className="chat-messages-area">
            <div className="messages-container">
              {messages.map((msg, index) => (
                <ChatMessage 
                  key={index}
                  role={msg.role}
                  content={msg.content}
                  formattedResponse={msg.formattedResponse}
                  isProcessing={msg.isProcessing}
                  timestamp={msg.timestamp}
                />
              ))}
              {loading && (
                <div className="message-wrapper assistant">
                  <div className="message-content assistant">
                    <div className="typing-indicator">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}
      </div>
      
      {/* Fixed input area */}
      <div className="chat-input-area">
        <div className="input-container">
          {currentAudio && (
            <div className="audio-player-wrapper">
              <AudioPlayer src={currentAudio} autoPlay={true} />
            </div>
          )}
          <ChatInput 
            onSendMessage={handleSendMessage} 
            disabled={loading} 
          />
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;