import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import './Citations.css'
//Basically the same as citation page, but change api call for summary
function Summary() {
  const location = useLocation();
  const [paperLink, setPaperLink] = useState('');
  const [summaryResult, setSummaryResult] = useState('');

  useEffect(() => {
    if (location.state && location.state.node) {
      setPaperLink(location.state.node);
      console.log(paperLink)
    }
  }, [location.state]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!paperLink) {
      alert('Please enter a paper link.');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/summary/${encodeURIComponent(paperLink)}`);
      const summaryText = await response.text();
      setSummaryResult(summaryText);
    } catch (error) {
      console.error('Error fetching summary:', error);
      setSummaryResult('An error occurred while fetching the summary - paper must be added first.');
    }
  };

  return (
    <div>
      <h2>Generate Summary</h2>
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
          <button type="submit">Generate Summary</button>
        </div>
      </form>
      {summaryResult && (
        <div>
          <h3>Your Summary:</h3>
          <textarea
            value={summaryResult}
            readOnly
            rows="10"
            style={{ width: '100%' }}
          />
        </div>
      )}
    </div>
  );
}

export default Summary;
