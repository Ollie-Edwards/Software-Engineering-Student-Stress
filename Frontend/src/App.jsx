import { BrowserRouter as Router, Routes, Route, BrowserRouter } from 'react-router-dom';
import Home from './pages/home';
import NavigationBar from './components/NavigationBar';
import React, { useState } from "react";
import MoodleTasks from './MoodleTask';

function App() {
  const [isAdding, setIsAdding] = useState(false);
  return (
    <div className="min-h-screen bg-gray-50">
      <BrowserRouter>
      <NavigationBar onAddTask={() => setIsAdding(true)} />
        <Routes>
          <Route path="/" element={<Home isAdding={isAdding} setIsAdding={setIsAdding} />} /> 
          <Route path="/home" element={<Home isAdding={isAdding} setIsAdding={setIsAdding} />} />
          <Route path="/about" element={<h1>About</h1>} />
          <Route path="/moodle" element={<MoodleTasks />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App
