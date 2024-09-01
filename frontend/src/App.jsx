import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Auth0Provider } from '@auth0/auth0-react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import About from './pages/About';
import ProtectedRoute from './ProtectedRoute';
import Graph from './pages/Graph';
import Reputation from './pages/Reputation';
import Profile from './pages/Profile';
import Citations from './pages/Citations';
import Summary from './pages/Summary';
import Admin from './pages/Admin';


function onRedirectCallback(appState) {
  window.history.replaceState(
    {},
    document.title,
    appState?.returnTo || window.location.pathname
  );
}

function App() {

  return (
    <Router>
      <Auth0Provider
        domain="dev-dic5qyxmh3023gsq.us.auth0.com"
        clientId="Mer00G3ZeV9ns6fUfkJsxXmDyxkiO3O5"
        authorizationParams={{ redirect_uri: window.location.origin }}
        onRedirectCallback={onRedirectCallback}
      >
        <Navbar />
        <Routes>
          <Route path="/about" element={<About />} />
          <Route path="/graph" element={<Graph />} />
          <Route path="/" element={<ProtectedRoute component={<Home />} />} />
          <Route path="/reputation" element={<ProtectedRoute component={<Reputation />} />} />
          <Route path="/profile" element={<ProtectedRoute component={<Profile />} />} />
          <Route path="/admin" element={<ProtectedRoute component={<Admin />} />} />
          <Route path="/citations" element={<ProtectedRoute component={<Citations />} />} />
          <Route path="/summary" element={<ProtectedRoute component={<Summary />} />} />
        </Routes>
      </Auth0Provider>
    </Router>
  );
}

export default App;
