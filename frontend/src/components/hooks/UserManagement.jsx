import { useEffect, useRef } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
//CUSTOM HOOK TO ENSURE THAT USER IS SIGNED IN, THAT BROWSER RECEIVES TOKEN FROM AUTH0, AND THAT NOTHING FUNNY HAPPENS WHEN THE REQUEST IS SENT TO DATABASE
const useUserManagement = ({ user, isAuthenticated, isLoading }) => {
  const { getAccessTokenSilently } = useAuth0();
  const debounceTimeout = useRef(null);  //useRef to keep track of the timeout

  useEffect(() => {
    console.log('useUserManagement hook called');
    console.log(isAuthenticated);
    console.log(user);

    //Delay added here as auth0 was called twice, and only the later one passes a token to browser
    const delayExecution = async () => {
      if (isLoading || !isAuthenticated || !user) {
        console.log('Auth0 is still loading or user is not authenticated, skipping user management');
        return;
      }

      console.log('User is authenticated and user data is available');

      try {
        //Get auth0 access token to make sure everything is smooth, then write create user api request
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
            password: 'PASSWORD', //auth0 unfortunately doen't pass this through so I left a default, user can change this
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
            //If user already in database fields, means user created, so try to update user fields with data if it has been updated
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
