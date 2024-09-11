import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import './Citations.css'

function Citations() {
  const location = useLocation();
  const [paperLink, setPaperLink] = useState('');
  const [citationStyle, setCitationStyle] = useState('apa');//I have to set apa here as default as this is what is selected when you click on this part of the site
  const [citationResult, setCitationResult] = useState('');
  
  useEffect(() => {
    if (location.state && location.state.node) {
      setPaperLink(location.state.node);
      console.log(paperLink)
    }
  }, [location.state]);

  const handleSubmit = async (e) => {//to ensure paper is actually entered
    e.preventDefault();
    if (!paperLink) {
      alert('Please enter a paper link.');
      return;
    }

    try {//fetch results from database for citation in given style
      const response = await fetch(`http://127.0.0.1:5000/citation/${encodeURIComponent(paperLink)}?style=${citationStyle}`);
      const citationText = await response.text();
      setCitationResult(citationText);
    } catch (error) {
      console.error('Error fetching citation:', error);
      setCitationResult('An error occurred while fetching the citation - paper must be added first.');
    }
  };

  return (
    <div>
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
          <label>
            Citation Style:
            <select
              value={citationStyle}
              onChange={(e) => setCitationStyle(e.target.value)}
            >
              <option value="apa">APA</option>
              <option value="cse">CSE</option>
              <option value="chicago">Chicago</option>
              <option value="harvard">Harvard</option>
            </select>
          </label>
        </div>
        <div>
          <button type="submit">Generate Citation</button>
        </div>
      </form>
      {citationResult && (
        <div>
          <h3>Your Citation:</h3>
          <textarea
            value={citationResult}
            readOnly
            rows="5"
            style={{ width: '100%' }}
          />
        </div>
      )}
    </div>
  );
}

export default Citations;
