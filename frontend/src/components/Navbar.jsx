import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import './Navbar.css';

const Navbar = () => {
  const { loginWithRedirect, logout, isAuthenticated, isLoading } = useAuth0();
  const location = useLocation();
  console.log(isAuthenticated)
  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <nav className="navbar">
      <div className="navbar-logo">SCRIPTSAFARI</div>
      <ul className="navbar-links">
        <li>
          <Link
            to="/about"
            className={location.pathname === '/about' ? 'active' : ''}
          >
            About
          </Link>
        </li>
        <li>
          <Link
            to="/graph"
            className={location.pathname === '/graph' ? 'active' : ''}
          >
            Graph
          </Link>
        </li>
        {isAuthenticated && (
          <>
            <li>
              <Link
                to="/"
                className={location.pathname === '/' ? 'active' : ''}
              >
                Home
              </Link>
            </li>
            <li>
              <Link
                to="/profile"
                className={location.pathname === '/profile' ? 'active' : ''}
              >
                Profile
              </Link>
            </li>
          </>
        )}
        <li>
          {!isAuthenticated ? (
            <a
              href="#login"
              onClick={() => loginWithRedirect()}
              className="auth-link"
            >
              Log In
            </a>
          ) : (
            <a
              href="#logout"
              onClick={() => logout({ returnTo: window.location.origin })}
              className="auth-link"
            >
              Log Out
            </a>
          )}
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
