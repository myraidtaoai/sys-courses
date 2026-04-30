import React, { useState } from 'react';
import { Sidebar, Header, MessageList, InputArea, ExampleCards } from './components';
import { useChat } from './hooks';
import './App.css';

/**
 * Main application component
 */
function App() {
  const {
    messages,
    isLoading,
    interruption,
    sendMessage,
    submitPoem,
    cancelInterruption,
    clearChat,
  } = useChat();
  const [showExamples, setShowExamples] = useState(messages.length === 0);
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  const handleExampleCardClick = (query) => {
    setShowExamples(false);
    sendMessage(query);
    if (window.innerWidth <= 768) {
      setSidebarOpen(false);
    }
  };

  const handleNewChat = () => {
    clearChat();
    setShowExamples(true);
    if (window.innerWidth <= 768) {
      setSidebarOpen(false);
    }
  };

  const handleCloseExamples = () => setShowExamples(false);

  const isBlankState = showExamples && messages.length === 0;

  return (
    <div className="app-layout">
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={handleNewChat}
        onExampleClick={handleExampleCardClick}
      />

      <div className="main-content">
        <Header
          onOpenSidebar={() => setSidebarOpen(true)}
          onNewChat={handleNewChat}
        />

        <main className="chat-area">
          <div className={`chat-container ${isBlankState ? 'chat-container--blank' : ''}`}>
            {isBlankState ? (
              <ExampleCards
                onCardClick={handleExampleCardClick}
                onClose={handleCloseExamples}
              />
            ) : (
              <>
                <MessageList messages={messages} isLoading={isLoading} />
                <InputArea
                  interruption={interruption}
                  isLoading={isLoading}
                  onSendMessage={sendMessage}
                  onSubmitPoem={submitPoem}
                  onCancel={cancelInterruption}
                />
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
