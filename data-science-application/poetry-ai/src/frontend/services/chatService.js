import apiClient from './apiClient';

export const sendChatQuery = async (query, thread_id) => {
  try {
    const response = await apiClient.post('/chat', { query, thread_id });
    return response.data;
  } catch (error) {
    console.error('Error sending chat query:', error);
    throw error.response?.data || new Error('Network error sending query.');
  }
};

export const resumeChat = async (poem_text, thread_id) => {
  try {
    const response = await apiClient.post('/resume', { poem_text, thread_id });
    return response.data;
  } catch (error) {
    console.error('Error resuming chat:', error);
    throw error.response?.data || new Error('Network error resuming chat.');
  }
};