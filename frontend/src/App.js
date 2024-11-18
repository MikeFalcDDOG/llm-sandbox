import React from 'react';
import Chatbot from './components/Chatbot';
import backgroundImage from './assets/camacho.jpg'
import './App.css';

function App() {
  return (
    <div className="App" style={{
      backgroundImage: `url(${backgroundImage})`, 
      backgroundSize: 'cover', // Adjust as needed
      backgroundPosition: 'center', // Adjust as needed 
      minHeight: '100vh' 
    }}>
      <h1>CAMCACHO CHAT</h1>
      <Chatbot />
    </div>
  );
}

export default App;