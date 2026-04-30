import axios from 'axios';

// For Cloud Run deployment - we'll update this with actual backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  'http://localhost:8080/api/v1'; // Default for local development

console.log('Environment:', import.meta.env.MODE);
console.log('API Base URL:', API_BASE_URL);

export const sendMessage = async (message, audioEnabled = false, signal) => {
  try {
    console.log('Sending request to:', `${API_BASE_URL}/chat/send`);
    
    const response = await axios.post(`${API_BASE_URL}/chat/send`, {
      message: message,
      audio_enabled: audioEnabled
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
      signal,
      timeout: 60000 // 60 second timeout for Cloud Run
    });

    return response.data;
  } catch (error) {
    console.error('Error sending message:', error);
    console.error('Request config:', error.config);
    throw error;
  }
};