import React, { useRef, useEffect } from 'react';
import './MessageList.css'; // Assuming you'll create a CSS file for the component

const MessageList = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="chat-container">
      {messages.map((msg, idx) => (
        <div key={idx} className={`message ${msg.role}`}>
          <div className="avatar">{msg.role === 'user' ? '🧑‍💻' : (msg.role === 'error' ? '⚠️' : '🤖')}</div>
          <div className="content">{msg.content}</div>
        </div>
      ))}
      {isLoading && <div className="message bot"><div className="content">Thinking...</div></div>}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;