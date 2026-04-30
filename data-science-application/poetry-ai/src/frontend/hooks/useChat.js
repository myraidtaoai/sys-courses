import { useState, useCallback } from 'react';
import { sendChatQuery, resumeChat } from '../services/chatService';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [interruption, setInterruption] = useState(null);
  const [error, setError] = useState(null);

  const sendMessage = useCallback(async (input) => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const data = await sendChatQuery(input, threadId);
      setThreadId(data.thread_id);

      if (data.interrupted) {
        setInterruption({ active: true, type: data.next_step });
        setMessages(prev => [...prev, { role: 'system', content: data.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'bot', content: data.response }]);
      }
    } catch (err) {
      console.error("Error:", err);
      setError(err.message || "Failed to connect to server.");
      setMessages(prev => [...prev, { role: 'error', content: err.message || "Failed to connect to server." }]);
    } finally {
      setIsLoading(false);
    }
  }, [threadId]);

  const submitPoem = useCallback(async (poemInput) => {
    if (!poemInput.trim()) return;

    const userMsg = { role: 'user', content: `(Poem Input): ${poemInput.substring(0, 50)}...` };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const data = await resumeChat(poemInput, threadId);
      setMessages(prev => [...prev, { role: 'bot', content: data.response }]);
      setInterruption(null);
    } catch (err) {
      console.error("Error resuming:", err);
      setError(err.message || "Failed to process poem.");
      setMessages(prev => [...prev, { role: 'error', content: err.message || "Failed to process poem." }]);
    } finally {
      setIsLoading(false);
    }
  }, [threadId]);

  const cancelInterruption = useCallback(() => {
      setInterruption(null);
      setError(null);
      setMessages(prev => [...prev, {role: 'system', content: 'Action cancelled.'}]);
  }, []);

  return {
    messages,
    isLoading,
    interruption,
    error,
    sendMessage,
    submitPoem,
    cancelInterruption
  };
};
