import React from 'react';
import "./App.css";
import LoginButton from "./components/LoginButton";
import "bootstrap/dist/css/bootstrap.min.css";
import { useAuth0 } from "@auth0/auth0-react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import About from './pages/About';

const App = () => {
  const { isAuthenticated } = useAuth0();

  return (
    <Router>
      <div>
        <Navbar />
        {isAuthenticated ? (
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
          </Routes>
        ):(
          <LoginButton />
        )}
      </div>
    </Router>
  );
}

export default App;
