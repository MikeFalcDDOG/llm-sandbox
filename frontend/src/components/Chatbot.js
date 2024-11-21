import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const chatBoxRef = useRef(null);

  // Default responses if API call fails
  const fallbackResponses = [
    "I’m President Camacho, and I’m here to fix everything!",
    "Don't worry; I'm gonna solve all the problems!",
    "I've got electrolytes! They’re what plants crave!",
    "Just relax. I got this, America!"
  ];

  const handleUserMessage = () => {
    if (input.trim()) {
      const userMessage = { text: input, sender: 'user' };
      setMessages([...messages, userMessage]);
      setInput('');
      handleBotResponse(userMessage.text);
    }
  };

  const handleBotResponse = async (userText) => {
    try {
      // Attempt to call the backend API
      const response = await axios.post('http://127.0.0.1:8000/chat', { message: userText });
      const botMessage = { text: response.data.reply, sender: 'bot' };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      // If API call fails, use a random fallback response
      console.error('API call failed:', error);
      const botMessage = {
        text: fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)],
        sender: 'bot',
      };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    }
  };

  // scroll to the bottom of the chatbox whenever messages update
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle Enter key press
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleUserMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-box" ref={chatBoxRef} style={{ overflowY: 'auto', maxHeight: '400px' }}>
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-message ${msg.sender === 'user' ? 'user' : 'bot'}`}
          >
            {msg.sender === 'user' ? 'You: ' : 'President Camacho: '} {msg.text}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown} // Add this line to handle the Enter key
          placeholder="Say something to President Camacho..."
        />
        <button onClick={handleUserMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chatbot;
