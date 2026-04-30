import React from 'react';
import { Header, MessageList, InputArea } from '../components';
import { useChat } from '../hooks';
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

  return (
    <div className="app">
      <Header onClearChat={clearChat} />
      <main className="app__main">
        <div className="app__chat-container">
          <MessageList messages={messages} isLoading={isLoading} />
          <InputArea
            interruption={interruption}
            isLoading={isLoading}
            onSendMessage={sendMessage}
            onSubmitPoem={submitPoem}
            onCancel={cancelInterruption}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
