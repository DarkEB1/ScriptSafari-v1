import React, { useState, useEffect } from 'react';
import { Graph } from 'react-d3-graph';
import { useNavigate } from 'react-router-dom';
import './GraphComponent.css'; 

const GraphComponent = () => {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [scores, setScores] = useState({});
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResult, setSearchResult] = useState(null); 

  const navigate = useNavigate();

  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/graph', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        let graph, scores;
        try {
          graph = JSON.parse(data.graph.replace(/'/g, '"').trim());
          scores = JSON.parse(data.scores.replace(/'/g, '"').trim());
        } catch (parseError) {
          console.error('Failed to parse graph or scores:', parseError);
          return;
        }

        const transformedGraphData = transformData(graph);
        setGraphData(transformedGraphData);
        setScores(scores);
      } catch (error) {
        console.error('Error fetching graph data:', error);
      }
    };

    fetchGraphData();
  }, []);

  const transformData = (data) => {
    const nodes = Object.keys(data).map((node) => ({
      id: node,
    }));

    const links = Object.entries(data).flatMap(([node, connections]) => {
      if (!Array.isArray(connections)) {
        console.warn(`Unexpected connections value for ${node}:`, connections);
        return [];
      }
      return connections.map((target) => ({
        source: node,
        target: target,
      }));
    });

    return { nodes, links };
  };

  const myConfig = {
    node: {
      color: 'lightblue',
      size: 400,
      fontSize: 14,
      highlightStrokeColor: 'blue',
    },
    link: {
      highlightColor: 'lightblue',
    },
    width: 800,
    height: 500,
    directed: false,
    automaticRearrangeAfterDropNode: true,
    d3: {
      gravity: -250, 
      linkLength: 120,
      linkStrength: 0.1,
    },
    panAndZoom: true,
    maxZoom: 2,
    minZoom: 0.5,
  };

  const onMouseOverNode = (nodeId) => {
    if (!selectedNode) {
      setHoveredNode(nodeId);
    }
  };

  const onMouseOutNode = () => {
    if (!selectedNode) {
      setHoveredNode(null);
    }
  };

  const onClickNode = (nodeId) => {
    setSelectedNode(nodeId);
    setHoveredNode(nodeId); // Treat click as if it's a permanent hover
    setSearchResult(null)
  };

  const handleSearch = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/get-node/${encodeURIComponent(searchQuery)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data && data.title) {
        setSearchResult(data); 
        setSelectedNode(data.title);
        setHoveredNode(data.title);
      } else {
        console.warn('Node not found');
        setSearchResult(null); 
      }
    } catch (error) {
      console.error('Error fetching node data:', error);
    }
  };

  const handleCitationClick = async () => {
    if (selectedNode) {
      setSearchQuery(selectedNode)
      console.log(selectedNode)
      try {
        const response = await fetch(`http://127.0.0.1:5000/get-node/${encodeURIComponent(searchQuery)}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        const data = await response.json();
        if (data && data.link) {
          navigate('/citations', { state: { node: data.link } });
        } else {
          console.warn('Node not found');
          setSearchResult(null); 
        }
      } catch (error) {
        console.error('Error fetching node data:', error);
      }
    }
  };

  const handleSummaryClick = async () => {
    if (selectedNode) {
      setSearchQuery(selectedNode)
      try {
        const response = await fetch(`http://127.0.0.1:5000/get-node/${encodeURIComponent(searchQuery)}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        const data = await response.json();
        if (data && data.link) {
          navigate('/summary', { state: { node: data.link } });
        } else {
          console.warn('Node not found');
          setSearchResult(null); 
        }
      } catch (error) {
        console.error('Error fetching node data:', error);
      }
      
    }
  };
  return (
    <div className="graph-container">
      <Graph
        id="graph-id"
        data={graphData}
        config={myConfig}
        onMouseOverNode={onMouseOverNode}
        onMouseOutNode={onMouseOutNode}
        onClickNode={onClickNode}
      />
      <div className="search-container">
        {searchResult && (
          <div className="search-result-panel">
            <div className="info-item">
              <strong>TITLE:</strong> {searchResult.title}
            </div>
            <div className="info-item">
              <strong>DATE:</strong> {searchResult.publication_date || 'N/A'}
            </div>
            <div className="info-item">
              <strong>AUTHOR:</strong> {searchResult.authors || 'N/A'}
            </div>
            <div className='info-item'>
              <strong>LINK:</strong> <a href={searchResult.link} target="_blank" rel="noopener noreferrer">link</a>
            </div>
          </div>
        )}
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Enter node title..."
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      {(hoveredNode || selectedNode) && (
        <div className="info-panel">
          <div className="info-item">
            <strong>TITLE:</strong> {hoveredNode || selectedNode}
          </div>
          <div className="info-item">
            <strong>REPUTATION:</strong> {scores[hoveredNode || selectedNode] || 'N/A'}
          </div>
          <button className="summary-button" onClick={handleCitationClick}>CITE</button>
          <button className="summary-button" onClick={handleSummaryClick}>SUMMARIZE</button>
        </div>
      )}
    </div>
  );
};

export default GraphComponent;
