import React from 'react';
import './App.css';
import { useChat } from './hooks/useChat';
import MessageList from './components/MessageList';
import InputArea from './components/InputArea';

function App() {
  const {
    messages,
    isLoading,
    interruption,
    sendMessage,
    submitPoem,
    cancelInterruption
  } = useChat();

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📚 Poetry AI Assistant</h1>
      </header>
      <MessageList messages={messages} isLoading={isLoading} />

      <InputArea
        interruption={interruption}
        isLoading={isLoading}
        onSendMessage={sendMessage}
        onSubmitPoem={submitPoem}
        onCancel={cancelInterruption}
      />
    </div>
  );
}

export default App;