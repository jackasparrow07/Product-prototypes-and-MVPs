import React, { useEffect, useState, useRef } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import './App.css';

function App() {
  const [transcription, setTranscription] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [useVoice, setUseVoice] = useState(false);
  const wsRef = useRef(null);
  
  const { status, startRecording, stopRecording, mediaBlobUrl } = useReactMediaRecorder({
    audio: true,
    onStop: (blobUrl, blob) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(blob);
      }
    }
  });

  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8080');

    wsRef.current.onopen = () => {
      setIsConnected(true);
      console.log('Connected to server');
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'transcription') {
        setTranscription(prev => prev + ' ' + data.text);
        
        // Only speak if voice translation is enabled
        if (useVoice) {
          const speech = new SpeechSynthesisUtterance(data.text);
          window.speechSynthesis.speak(speech);
        }
      } else if (data.type === 'error') {
        console.error('Server error:', data.message);
      }
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from server');
    };

    return () => {
      wsRef.current?.close();
    };
  }, [useVoice]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Real-time Translator</h1>
        <div className="status">
          Connection: {isConnected ? 'Connected' : 'Disconnected'}
          <br />
          Recording Status: {status}
        </div>
        
        <div className="voice-toggle">
          <label>
            <input
              type="checkbox"
              checked={useVoice}
              onChange={(e) => setUseVoice(e.target.checked)}
            />
            Enable Voice Translation
          </label>
        </div>
        
        <div className="controls">
          <button onClick={startRecording} disabled={status === 'recording'}>
            Start Recording
          </button>
          <button onClick={stopRecording} disabled={status !== 'recording'}>
            Stop Recording
          </button>
        </div>

        <div className="transcription">
          <h3>Transcription:</h3>
          <p>{transcription}</p>
        </div>
      </header>
    </div>
  );
}

export default App;
