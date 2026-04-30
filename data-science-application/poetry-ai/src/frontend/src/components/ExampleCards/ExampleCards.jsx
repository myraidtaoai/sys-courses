import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { exampleCards, sampleConversations, poetryTerms } from '../../data/exampleCards';
import './ExampleCards.css';

const TYPE_LABELS = {
  poet: 'Poet',
  poem: 'Poem',
  classification: 'Classify',
  recommendation: 'Recommend',
};

/**
 * ExampleCards component - Shows sample interactions and use cases
 */
const ExampleCards = ({ onCardClick, onClose }) => {
  const [activeTab, setActiveTab] = useState('cards');

  const handleCardClick = (card) => {
    if (onCardClick) {
      onCardClick(card.query || card.poemExcerpt);
    }
  };

  return (
    <div className="example-cards">
      <button className="example-cards__close-btn" onClick={onClose} title="Close">✕</button>

      <div className="example-cards__hero">
        <span className="example-cards__hero-icon">📚</span>
        <h2 className="example-cards__hero-title">Poetry AI Assistant</h2>
        <p className="example-cards__hero-subtitle">Ask about poets, analyze poems, classify &amp; discover</p>
      </div>

      <div className="example-cards__tabs">
        {['cards', 'conversations', 'terms'].map((tab) => (
          <button
            key={tab}
            className={`example-cards__tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'cards' ? '✦ Examples' : tab === 'conversations' ? '💬 Chats' : '📖 Terms'}
          </button>
        ))}
      </div>

      <div className="example-cards__content">
        {activeTab === 'cards' && (
          <div className="example-cards__grid">
            {exampleCards.map((card) => (
              <div
                key={card.id}
                className={`example-card example-card--${card.type}`}
                onClick={() => handleCardClick(card)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && handleCardClick(card)}
              >
                <div className="example-card__header">
                  <div className="example-card__icon-wrap">{card.icon}</div>
                  <h3 className="example-card__title">{card.title}</h3>
                  <span className="example-card__type-badge">{TYPE_LABELS[card.type]}</span>
                </div>
                <p className="example-card__preview">{card.preview}</p>
                <p className="example-card__query">"{card.query || card.poemExcerpt}"</p>
                <span className="example-card__cta">Click to ask →</span>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'conversations' && (
          <div className="example-conversations">
            {sampleConversations.map((conversation) => (
              <div key={conversation.id} className="example-conversation">
                <h3 className="example-conversation__title">{conversation.title}</h3>
                <div className="example-conversation__messages">
                  {conversation.messages.map((msg, idx) => (
                    <div key={idx} className={`example-message example-message--${msg.role}`}>
                      <div className="example-message__avatar">
                        {msg.role === 'user' ? '🧑‍💻' : msg.role === 'bot' ? '🤖' : 'ℹ️'}
                      </div>
                      <div className="example-message__bubble">
                        <p>{msg.content}</p>
                        <span className="example-message__time">
                          {msg.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'terms' && (
          <div className="example-terms__grid">
            {poetryTerms.map((item, idx) => (
              <div key={idx} className="example-term">
                <h4 className="example-term__title">{item.term}</h4>
                <p className="example-term__definition">{item.definition}</p>
                <p className="example-term__example"><em>e.g. {item.example}</em></p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

ExampleCards.propTypes = {
  onCardClick: PropTypes.func,
  onClose: PropTypes.func,
};

ExampleCards.defaultProps = {
  onCardClick: null,
  onClose: null,
};

export default ExampleCards;
