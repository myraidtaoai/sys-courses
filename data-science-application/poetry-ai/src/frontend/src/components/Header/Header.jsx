import React from 'react';
import PropTypes from 'prop-types';
import './Header.css';

const Header = ({ onOpenSidebar, onNewChat }) => {
  return (
    <header className="header">
      <button
        className="header__menu"
        type="button"
        aria-label="Open navigation"
        onClick={onOpenSidebar}
      >
        <span />
        <span />
        <span />
      </button>

      <div className="header__brand">
        <div className="header__icon-wrap">✦</div>
        <div className="header__titles">
          <h1 className="header__title">Poetry Studio</h1>
          <span className="header__subtitle">Conversational literary analysis</span>
        </div>
      </div>

      <div className="header__actions">
        <button className="header__action" type="button" onClick={onNewChat}>
          Start New Chat
        </button>
      </div>
    </header>
  );
};

Header.propTypes = {
  onOpenSidebar: PropTypes.func,
  onNewChat: PropTypes.func,
};

Header.defaultProps = {
  onOpenSidebar: () => {},
  onNewChat: () => {},
};

export default Header;
