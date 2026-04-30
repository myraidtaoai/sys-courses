import React from 'react';
import PropTypes from 'prop-types';
import './Header.css';

/**
 * Application header component
 */
const Header = ({ onClearChat }) => {
  return (
    <header className="header">
      <div className="header__content">
        <div className="header__brand">
          <span className="header__icon">📚</span>
          <h1 className="header__title">Poetry AI Assistant</h1>
        </div>
        <nav className="header__nav">
          <button
            className="header__button"
            onClick={onClearChat}
            title="Clear chat history"
          >
            🗑️ Clear
          </button>
        </nav>
      </div>
    </header>
  );
};

Header.propTypes = {
  onClearChat: PropTypes.func,
};

Header.defaultProps = {
  onClearChat: () => {},
};

export default Header;
