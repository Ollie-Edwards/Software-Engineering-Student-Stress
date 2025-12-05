import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/home';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} /> 
        <Route path="/home" element={<Home />} />
        <Route path="/about" element={<h1>About</h1>} />
      </Routes>
    </Router>
  )
}

export default App
