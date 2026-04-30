import React, { useState } from 'react';
import PropTypes from 'prop-types';
import './InputArea.css';

/**
 * Chat input area with support for interruption mode
 */
const InputArea = ({ interruption, isLoading, onSendMessage, onSubmitPoem, onCancel }) => {
  const [input, setInput] = useState('');
  const [poemInput, setPoemInput] = useState('');

  const handleSend = (e) => {
    e?.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleSubmitPoem = (e) => {
    e?.preventDefault();
    if (poemInput.trim() && !isLoading) {
      onSubmitPoem(poemInput);
      setPoemInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Interruption mode - show poem input form
  if (interruption?.active) {
    return (
      <div className="input-area">
        <form className="input-area__form input-area__form--interruption" onSubmit={handleSubmitPoem}>
          <div className="input-area__interruption-header">
            <span className="input-area__interruption-icon">📝</span>
            <span>Please provide your poem text for {interruption.type || 'processing'}</span>
          </div>
          <textarea
            className="input-area__textarea"
            value={poemInput}
            onChange={(e) => setPoemInput(e.target.value)}
            placeholder="Enter poem text here..."
            rows={4}
            disabled={isLoading}
            autoFocus
          />
          <div className="input-area__actions">
            <button
              type="button"
              className="input-area__button input-area__button--cancel"
              onClick={onCancel}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="input-area__button input-area__button--submit"
              disabled={isLoading || !poemInput.trim()}
            >
              {isLoading ? 'Processing...' : 'Submit Poem'}
            </button>
          </div>
        </form>
      </div>
    );
  }

  // Normal chat input mode
  return (
    <div className="input-area">
      <form className="input-area__form" onSubmit={handleSend}>
        <input
          type="text"
          className="input-area__input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about poets or poems, request classification..."
          disabled={isLoading}
          autoFocus
        />
        <button
          type="submit"
          className="input-area__button input-area__button--send"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? '...' : '➤'}
        </button>
      </form>
    </div>
  );
};

InputArea.propTypes = {
  interruption: PropTypes.shape({
    active: PropTypes.bool,
    type: PropTypes.string,
  }),
  isLoading: PropTypes.bool,
  onSendMessage: PropTypes.func.isRequired,
  onSubmitPoem: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
};

InputArea.defaultProps = {
  interruption: null,
  isLoading: false,
};

export default InputArea;
