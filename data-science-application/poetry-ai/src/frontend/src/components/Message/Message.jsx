import React from 'react';
import PropTypes from 'prop-types';
import './Message.css';

/**
 * Individual message component
 */
const Message = ({ role, content, timestamp }) => {
  const getAvatar = () => {
    switch (role) {
      case 'user':
        return '🧑‍💻';
      case 'bot':
        return '🤖';
      case 'system':
        return 'ℹ️';
      case 'error':
        return '⚠️';
      default:
        return '💬';
    }
  };

  const formatTime = (date) => {
    if (!date) return '';
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`message message--${role}`}>
      {role !== 'system' && role !== 'error' && (
        <div className="message__avatar">{getAvatar()}</div>
      )}
      <div className="message__bubble">
        <div className="message__text">{content}</div>
        {timestamp && <div className="message__time">{formatTime(timestamp)}</div>}
      </div>
    </div>
  );
};

Message.propTypes = {
  role: PropTypes.oneOf(['user', 'bot', 'system', 'error']).isRequired,
  content: PropTypes.string.isRequired,
  timestamp: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]),
};

Message.defaultProps = {
  timestamp: null,
};

export default Message;
