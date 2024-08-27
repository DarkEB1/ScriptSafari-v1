import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';

const Navbar = () => {
  const { loginWithRedirect, logout, isAuthenticated } = useAuth0();

  return (
    <nav>
      <ul>
        <li>
          <Link to="/about">About</Link>
        </li>
        {isAuthenticated && (
          <>
            <li>
              <Link to="/">Home</Link>
            </li>
          </>
        )}
      </ul>
      <div>
        {!isAuthenticated ? (
          <button onClick={() => loginWithRedirect()}>Login</button>
        ) : (
          <button onClick={() => logout({ returnTo: window.location.origin })}>
            Logout
          </button>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
