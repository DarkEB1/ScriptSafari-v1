import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Navigate, useLocation } from 'react-router-dom';

function ProtectedRoute({ component }) {
  const { isAuthenticated, isLoading } = useAuth0();
  const location = useLocation();
  //Wait till not loading, then configure authentication stuff
  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? (
    component
  ) : (
    <Navigate to="/about" state={{ returnTo: location.pathname }} />
  );
}

export default ProtectedRoute;