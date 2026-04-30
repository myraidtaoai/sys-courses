import React, { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import Message from '../Message';
import './MessageList.css';

/**
 * Component to display list of chat messages
 */
const MessageList = ({ messages, isLoading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="message-list__empty">
          <div className="message-list__empty-icon">📚</div>
          <h3>Welcome to Poetry AI Assistant</h3>
          <p>Ask me about poets, poems, or request classifications and recommendations!</p>
        </div>
      ) : (
        messages.map((msg, idx) => (
          <Message
            key={idx}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
          />
        ))
      )}
      {isLoading && (
        <div className="message message--bot message--loading">
          <div className="message__avatar">🤖</div>
          <div className="message__content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

MessageList.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      role: PropTypes.string.isRequired,
      content: PropTypes.string.isRequired,
      timestamp: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
    })
  ).isRequired,
  isLoading: PropTypes.bool,
};

MessageList.defaultProps = {
  isLoading: false,
};

export default MessageList;
