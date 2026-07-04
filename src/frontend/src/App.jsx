import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [logs, setLogs] = useState([])
  const [report, setReport] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef(null)

  useEffect(() => {
    let isMounted = true;
    let socket = null;
    let reconnectTimeout = null;

    const connect = () => {
      socket = new WebSocket('ws://127.0.0.1:8000/ws/stream');
      ws.current = socket;
      
      socket.onopen = () => {
        if (isMounted) setIsConnected(true);
      };
      
      socket.onclose = () => {
        if (isMounted) {
          setIsConnected(false);
          // Auto-reconnect after 2 seconds if connection drops
          reconnectTimeout = setTimeout(connect, 2000);
        }
      };
      
      socket.onmessage = (event) => {
        if (!isMounted) return;
        try {
          const msg = JSON.parse(event.data);
          if (['info', 'agent_update', 'error'].includes(msg.type)) {
            setLogs(prev => [...prev, `[${msg.type.toUpperCase()}] ${msg.node ? msg.node + ':' : ''} ${msg.data}`]);
          } else if (msg.type === 'final_report') {
            setReport(msg.data);
          }
        } catch (e) {
          console.error("Error parsing message", e);
        }
      };
      
      socket.onerror = (err) => {
        console.error("WebSocket Error:", err);
      };
    };

    connect();
    
    return () => {
      isMounted = false;
      clearTimeout(reconnectTimeout);
      // Only close if it's actually open to prevent the abort error
      if (socket && socket.readyState === 1) {
        socket.close();
      }
    };
  }, []);

  const startResearch = () => {
    if (ws.current && isConnected && query) {
      setLogs([])
      setReport('')
      ws.current.send(JSON.stringify({ query }))
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>Multi-Agent Research Swarm</h1>
        <span className={isConnected ? "status connected" : "status disconnected"}>
          {isConnected ? "● Swarm Online" : "○ Offline"}
        </span>
      </header>
      
      <div className="search-box">
        <input 
          type="text" 
          value={query} 
          onChange={(e) => setQuery(e.target.value)} 
          placeholder="What are the real-world limitations of RAG systems in production?"
          onKeyPress={(e) => e.key === 'Enter' && startResearch()}
        />
        <button onClick={startResearch} disabled={!isConnected || !query}>
          Start Research
        </button>
      </div>

      <div className="content-area">
        <div className="logs-panel">
          <h3>Live Agent Trace (ReAct Loop)</h3>
          <div className="logs-container">
            {logs.map((log, i) => (
              <div key={i} className={`log-entry ${log.includes('ERROR') ? 'error' : ''}`}>{log}</div>
            ))}
            {logs.length === 0 && <div className="empty-state">Waiting for task...</div>}
          </div>
        </div>
        
        <div className="report-panel">
          <h3>Final Synthesized Report</h3>
          <div className="report-content">
            {report ? (
              <pre className="markdown-render">{report}</pre>
            ) : (
              <div className="empty-state">Waiting for swarm to synthesize findings...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
