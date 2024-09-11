import React, { useState, useEffect } from 'react';

const Profilecomp = () => {
    const email = localStorage.getItem('userEmail'); 

    const [userDetails, setUserDetails] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {//Fetch profile details using email from local storage if there is an email
        if (email) {
            fetch(`http://127.0.0.1:5000/profile/${encodeURIComponent(email)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('User not found or other server error');
                    }
                    return response.json();
                })
                .then(data => {
                    setUserDetails(data);
                    setLoading(false);
                })
                .catch(error => {
                    setError(error.message);
                    setLoading(false);
                });
            
        } else {
            setError('No email found');
            setLoading(false);
        }
    }, [email]);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div style={{//These are here as there is not much, most is inhereted anyways.
            backgroundColor: '#1b1b1b',
            color: 'white',
            width: '400px',
            padding: '20px',
            marginTop: '100px',
            marginLeft: '625px',
            borderRadius: '10px',
            textAlign: 'center',
            boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)'
        }}>
            {userDetails ? (
                
                <div>
                    <img 
                    src={userDetails.pfp} 
                    alt={`${userDetails.username}'s profile`} 
                    style={{ width: '150px', height: '150px', borderRadius: '50%' }}
                    />
                    <p><strong>Username:</strong> {userDetails.username}</p>
                    <p><strong>Email:</strong> {userDetails.email}</p>
                </div>
            ) : (
                <p>User details not found.</p>
            )}
        </div>
    );
};

export default Profilecomp;
