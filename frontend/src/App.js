import React, { useState, useEffect } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import DetectionFeed from './components/DetectionFeed';
import SystemStats from './components/SystemStats';

const API_URL = 'http://localhost:8000';

function App() {
  const [stats, setStats] = useState(null);
  const [streams, setStreams] = useState([]);
  const [recentDetections, setRecentDetections] = useState([]);
  const [liveData, setLiveData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    fetchStats();
    fetchStreams();
    fetchRecentDetections();

    const interval = setInterval(() => {
      fetchStats();
      fetchStreams();
      fetchRecentDetections();
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/live');

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLiveData(data);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchStreams = async () => {
    try {
      const response = await fetch(`${API_URL}/streams`);
      const data = await response.json();
      setStreams(data);
    } catch (error) {
      console.error('Error fetching streams:', error);
    }
  };

  const fetchRecentDetections = async () => {
    try {
      const response = await fetch(`${API_URL}/detections?limit=10`);
      const data = await response.json();
      setRecentDetections(data);
    } catch (error) {
      console.error('Error fetching detections:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎥 Distributed Video Analytics System</h1>
        <div className="connection-status">
          <span className={connected ? 'status-dot connected' : 'status-dot disconnected'}></span>
          {connected ? 'Live' : 'Disconnected'}
        </div>
      </header>

      <div className="container">
        <Dashboard stats={stats} liveData={liveData} />

        <div className="content-grid">
          <SystemStats stats={stats} streams={streams} liveData={liveData} />
          <DetectionFeed detections={recentDetections} liveData={liveData} />
        </div>
      </div>
    </div>
  );
}

export default App;
