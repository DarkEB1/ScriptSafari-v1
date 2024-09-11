import { useEffect, useRef } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const useUserManagement = ({ user, isAuthenticated, isLoading }) => {
  const { getAccessTokenSilently } = useAuth0();
  const debounceTimeout = useRef(null);  //useRef to keep track of the timeout

  useEffect(() => {
    console.log('useUserManagement hook called');
    console.log(isAuthenticated);
    console.log(user);

    const delayExecution = async () => {
      if (isLoading || !isAuthenticated || !user) {
        console.log('Auth0 is still loading or user is not authenticated, skipping user management');
        return;
      }

      console.log('User is authenticated and user data is available');

      try {
        const token = await getAccessTokenSilently();
        console.log('Token obtained:', token);

        const createUserResponse = await fetch('http://localhost:5000/create-user', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            email: user.email,
            password: 'PASSWORD',
            username: user.nickname,
            pfp: user.picture,
          }),
        });

        if (createUserResponse.status === 201) {
          console.log('User created successfully');
        } else {
          const existingUser = await createUserResponse.json();
          if (
            existingUser.username !== user.nickname ||
            existingUser.email !== user.email ||
            existingUser.pfp !== user.picture
          ) {
            await fetch('http://localhost:5000/update-user', {
              method: 'PUT',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                email: user.email,
                username: user.nickname,
                pfp: user.picture,
              }),
            });
            console.log('User updated successfully');
          }
        }
      } catch (error) {
        console.error('Error managing user:', error);
      }
    };

    // Debounce delayExecution
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    debounceTimeout.current = setTimeout(() => {
      delayExecution();
    }, 1500);

    // Cleanup function to clear the timeout if the component umounts or dependencies change
    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
      console.log('useUserManagement cleanup');
    };
  }, [isAuthenticated, isLoading, user, getAccessTokenSilently]);
};

export default useUserManagement;
