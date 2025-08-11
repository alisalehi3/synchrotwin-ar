import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import './App.css';

function App() {
  const [services, setServices] = useState({});
  const [plvData, setPlvData] = useState([]);
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Check service health - using actual ports from backend
    const checkServices = async () => {
      const servicePorts = [5001, 5002, 5003, 5004, 5005]; // Updated ports
      const serviceStatus = {};

      for (const port of servicePorts) {
        try {
          const response = await axios.get(`http://localhost:${port}/api/health`, {
            timeout: 2000
          });
          serviceStatus[port] = {
            status: 'healthy',
            data: response.data
          };
        } catch (error) {
          serviceStatus[port] = {
            status: 'error',
            error: error.message
          };
        }
      }
      setServices(serviceStatus);
    };

    checkServices();
    const interval = setInterval(checkServices, 5000);

    // Connect to WebSocket
    const newSocket = io('http://localhost:5004');
    
    newSocket.on('connect', () => {
      console.log('Connected to WebSocket');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket');
      setIsConnected(false);
    });

    newSocket.on('plv_update', (data) => {
      setPlvData(prev => [...prev.slice(-19), data]);
    });

    setSocket(newSocket);

    return () => {
      clearInterval(interval);
      if (newSocket) {
        newSocket.disconnect();
      }
    };
  }, []);

  const getServiceName = (port) => {
    const names = {
      5001: 'Digital Twin',
      5002: 'AR Biofeedback',
      5003: 'Data Ingestion',
      5004: 'Notification',
      5005: 'Synchrony Analysis'
    };
    return names[port] || `Service ${port}`;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🧠 SynchroTwin-AR Dashboard</h1>
        <p>Real-time Neural Synchrony & AR Biofeedback System</p>
      </header>

      <main className="App-main">
        <div className="services-grid">
          <h2>🔧 Service Status</h2>
          <div className="services-container">
            {Object.entries(services).map(([port, service]) => (
              <div key={port} className={`service-card ${service.status}`}>
                <h3>{getServiceName(parseInt(port))}</h3>
                <p>Port: {port}</p>
                <p>Status: {service.status}</p>
                {service.status === 'healthy' && (
                  <p>Service: {service.data?.service}</p>
                )}
                {service.status === 'error' && (
                  <p className="error">Error: {service.error}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="data-section">
          <h2>📊 Real-time PLV Data</h2>
          <div className="connection-status">
            WebSocket Status: 
            <span className={isConnected ? 'connected' : 'disconnected'}>
              {isConnected ? ' Connected' : ' Disconnected'}
            </span>
          </div>
          
          <div className="plv-chart">
            {plvData.length > 0 ? (
              <div className="chart-container">
                {plvData.map((data, index) => (
                  <div key={index} className="plv-bar" 
                       style={{ height: `${data.plv * 100}%` }}>
                    <span className="plv-value">{data.plv}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p>Waiting for data...</p>
            )}
          </div>

          <div className="latest-data">
            <h3>Latest PLV Values:</h3>
            <div className="data-list">
              {plvData.slice(-5).reverse().map((data, index) => (
                <div key={index} className="data-item">
                  <span>PLV: {data.plv}</span>
                  <span>{new Date(data.timestamp).toLocaleTimeString()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
