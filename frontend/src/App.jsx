import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Auth0Provider } from '@auth0/auth0-react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import About from './pages/About';
import ProtectedRoute from './ProtectedRoute';

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
        clientId="WsWUDvT0VtriDCaey0ZHu74mQ2Av3iUb"
        redirectUri={window.location.origin}
        onRedirectCallback={onRedirectCallback}
      >
        <Navbar />
        <Routes>
          <Route path="/about" element={<About />} />
          <Route path="/" element={<ProtectedRoute component={<Home />} />} />
        </Routes>
      </Auth0Provider>
    </Router>
  );
}

export default App;
