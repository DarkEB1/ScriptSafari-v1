import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import GraphComponent from '../components/GraphComponent'; 

function Reputation() {
  const [paperLink, setPaperLink] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const [isSuccessful, setIsSuccessful] = useState(false);

  const email = localStorage.getItem('userEmail');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!paperLink) {
      alert('Please enter a paper link.');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/add-paper/${encodeURIComponent(paperLink)}?email=${encodeURIComponent(email)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (response.ok) {
        setResponseMessage("Success! View in Graph");
        setIsSuccessful(true); 
      } else {
        setResponseMessage(data.error || 'An unknown error occurred.');
        setIsSuccessful(false);
      }
    } catch (error) {
      console.error('Error adding paper:', error);
      setResponseMessage('An error occurred while adding the paper.');
      setIsSuccessful(false);
    }
  };

  return (
    <div>
      <h2>Add Paper to Reputation System</h2>
      <h3>Note: you may have to click submit twice if a server error occurs</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Paper Link:
            <input
              type="text"
              value={paperLink}
              onChange={(e) => setPaperLink(e.target.value)}
              placeholder="Enter paper link"
              required
            />
          </label>
        </div>
        <div>
          <button type="submit">Add Paper</button>
        </div>
      </form>
      {responseMessage && (
        <div>
          <h3>{isSuccessful ? 'Success' : 'Error'}:</h3>
          <p>{responseMessage}</p>
        </div>
      )}
      {isSuccessful && (
        <div>
          <GraphComponent />
        </div>
      )}
    </div>
  );
}

export default Reputation;
