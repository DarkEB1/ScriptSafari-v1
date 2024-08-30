import { useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

const useUserManagement = () => {
  const { user, isAuthenticated, getAccessTokenSilently } = useAuth0();

  useEffect(() => {
    const manageUser = async () => {
      if (isAuthenticated && user) {
        const username = user.email.split('@')[0];

        try {
          const token = await getAccessTokenSilently();

          const createUserResponse = await fetch('http://localhost:5000/create-user', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              email: user.email,
              password: 'PASSWORD',
              username: username,
              pfp: user.picture,
            }),
          });

          if (createUserResponse.status === 201) {
            console.log('User created successfully');
          } else {
            const existingUser = await createUserResponse.json();
            if (
              existingUser.username !== username ||
              existingUser.email !== user.email ||
              existingUser.pfp !== profilePicture
            ) {
              await fetch('http://localhost:5000/update-user', {
                method: 'PUT',
                headers: {
                  'Content-Type': 'application/json',
                  Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                  email: user.email,
                  username: username,
                  pfp: profilePicture,
                }),
              });
              console.log('User updated successfully');
            }
          }
        } catch (error) {
          console.error('Error managing user:', error);
        }
      }
    };

    manageUser();
  }, [isAuthenticated, user, getAccessTokenSilently]);
};

export default useUserManagement;
