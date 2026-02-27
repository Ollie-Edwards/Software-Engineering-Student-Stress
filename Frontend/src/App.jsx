import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/home';
import NavigationBar from './components/NavigationBar';
import React, { useState } from "react";

function App() {
  const [isAdding, setIsAdding] = useState(false);
  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationBar onAddTask={() => setIsAdding(true)} />
      <Router>
        <Routes>
          <Route path="/" element={<Home isAdding={isAdding} setIsAdding={setIsAdding} />} /> 
          <Route path="/home" element={<Home isAdding={isAdding} setIsAdding={setIsAdding} />} />
          <Route path="/about" element={<h1>About</h1>} />
        </Routes>
      </Router>
    </div>
  )
}

export default App
