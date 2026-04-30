import React from 'react';
import PropTypes from 'prop-types';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose, onNewChat, onExampleClick }) => {
  return (
    <>
      <div
        className={`sidebar__overlay ${isOpen ? 'open' : ''}`}
        onClick={onClose}
      ></div>
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar__header">
          <h2 className="sidebar__title">Poetry AI</h2>
          <button className="sidebar__close-btn" onClick={onClose} aria-label="Close menu">
            &times;
          </button>
        </div>

        <button className="sidebar__new-chat" onClick={onNewChat}>
          <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New chat
        </button>

        <div className="sidebar__section">
          <h3 className="sidebar__section-title">Suggestions</h3>
          <ul className="sidebar__list">
            <li onClick={() => onExampleClick("Write a haiku about the rain")}>Haiku about the rain</li>
            <li onClick={() => onExampleClick("Analyse Robert Frost's 'The Road Not Taken'")}>Robert Frost Analysis</li>
            <li onClick={() => onExampleClick("Write a romantic poem like John Keats")}>Romantic Poem</li>
            <li onClick={() => onExampleClick("What is a sonnet? Explain with examples")}>What is a sonnet?</li>
            <li onClick={() => onExampleClick("Show me a famous poem by Emily Dickinson")}>Emily Dickinson</li>
          </ul>
        </div>

        <div className="sidebar__footer">
          <p>© 2024 Poetry AI Assistant</p>
        </div>
      </div>
    </>
  );
};

Sidebar.propTypes = {
  isOpen: PropTypes.bool,
  onClose: PropTypes.func,
  onNewChat: PropTypes.func,
  onExampleClick: PropTypes.func,
};

Sidebar.defaultProps = {
  isOpen: false,
  onClose: () => {},
  onNewChat: () => {},
  onExampleClick: () => {},
};

export default Sidebar;
