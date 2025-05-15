import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleApiKeyChange = (e) => {
    setApiKey(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a PDF file');
      return;
    }
    
    if (!apiKey) {
      setError('Please enter your Gemini API key');
      return;
    }
    
    setError(null);
    setIsLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('api_key', apiKey);
    
    try {
      const response = await fetch('http://localhost:8000/api/analyze-pdf', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze PDF');
      }
      
      setAnalysis(data.result);
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Climate Action Plan Analyzer</h1>
        <p>Upload a city's Climate Action Plan (CAP) or related PDF report for analysis</p>
      </header>
      
      <main className="App-main">
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label htmlFor="api-key">Gemini API Key:</label>
            <input
              type="password"
              id="api-key"
              value={apiKey}
              onChange={handleApiKeyChange}
              placeholder="Enter your Gemini API key"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="file-upload">Select PDF File:</label>
            <input
              type="file"
              id="file-upload"
              accept=".pdf"
              onChange={handleFileChange}
              required
            />
          </div>
          
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Analyzing...' : 'Analyze PDF'}
          </button>
        </form>
        
        {error && <div className="error-message">{error}</div>}
        
        {isLoading && (
          <div className="loading">
            <p>Analyzing your document... This may take a few minutes.</p>
            <div className="spinner"></div>
          </div>
        )}
        
        {analysis && (
          <div className="analysis-results">
            <h2>Analysis Results</h2>
            <div className="results-content">
              {/* Render the analysis with proper formatting */}
              <pre>{analysis}</pre>
            </div>
          </div>
        )}
      </main>
      
      <footer className="App-footer">
        <p>Climate Action Plan Analysis Tool &copy; 2025</p>
      </footer>
    </div>
  );
}

export default App;