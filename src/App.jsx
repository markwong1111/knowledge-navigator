import React, { useState, useRef } from 'react';
import { Upload, FileText, Download, Loader2, X, Paperclip } from 'lucide-react';

// TODO - update to backend URL
const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [inputText, setInputText] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [graphHtml, setGraphHtml] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // Handle file selection
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = files.filter(file => {
      const ext = file.name.split('.').pop().toLowerCase();
      return ['txt', 'pdf', 'docx', 'csv'].includes(ext);
    });
    setUploadedFiles(prev => [...prev, ...validFiles]);
  };

  // Remove file from upload list
  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Generate knowledge graph
  const generateGraph = async () => {
    if (!inputText.trim() && uploadedFiles.length === 0) {
      setError('Please enter text or upload files');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const formData = new FormData();
      
      // Add text if present
      if (inputText.trim()) {
        formData.append('text', inputText);
      }

      // Add files if present
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      // Call your Python backend API
      const response = await fetch(`${API_BASE_URL}/api/generate-graph`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      
      // Set graph HTML for display
      setGraphHtml(data.html || data.graph_html);
      setGraphData(data);
      
    } catch (err) {
      setError(err.message || 'Failed to generate knowledge graph');
      console.error('Error generating graph:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  // Download graph in different formats
  const downloadGraph = (format) => {
    if (!graphData) return;

    let blob, filename;

    switch(format) {
      case 'html':
        blob = new Blob([graphData.html || graphData.graph_html], { type: 'text/html' });
        filename = 'knowledge_graph.html';
        break;
      case 'json':
        blob = new Blob([JSON.stringify(graphData, null, 2)], { type: 'application/json' });
        filename = 'knowledge_graph.json';
        break;
      default:
        return;
    }

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Handle Enter key (Shift+Enter for new line)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      generateGraph();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-white">
      {graphHtml ? (
        // Graph Display View
        <div className="flex-1 flex flex-col">
          <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800">Knowledge Graph</h2>
            <div className="flex gap-2">
              <button
                onClick={() => downloadGraph('html')}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium"
              >
                <Download size={16} />
                HTML
              </button>
              <button
                onClick={() => downloadGraph('json')}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium"
              >
                <Download size={16} />
                JSON
              </button>
              <button
                onClick={() => {
                  setGraphHtml(null);
                  setGraphData(null);
                  setInputText('');
                  setUploadedFiles([]);
                  setError(null);
                }}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium"
              >
                <X size={16} />
                New Graph
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <iframe
              srcDoc={graphHtml}
              className="w-full h-full border-0"
              title="Knowledge Graph"
            />
          </div>
        </div>
      ) : (
        // Input View - ChatGPT Style
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="px-4 py-3 border-b">
            <h1 className="text-lg font-semibold text-gray-800">Knowledge Navigator</h1>
          </div>

          {/* Main Content - Centered like ChatGPT */}
          <div className="flex-1 flex items-center justify-center p-4">
            <div className="w-full max-w-3xl">
              {/* Welcome Message */}
              {!inputText && uploadedFiles.length === 0 && (
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-semibold text-gray-800 mb-3">
                    Knowledge Navigator
                  </h2>
                  <p className="text-gray-500">
                    Upload documents or enter text to generate a knowledge graph
                  </p>
                </div>
              )}

              {/* File Upload Display */}
              {uploadedFiles.length > 0 && (
                <div className="mb-4 space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-gray-50 border border-gray-200 px-4 py-3 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <FileText size={18} className="text-gray-600" />
                        <span className="text-sm text-gray-700">{file.name}</span>
                        <span className="text-xs text-gray-500">
                          ({(file.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="text-gray-400 hover:text-red-600 transition-colors"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  {error}
                </div>
              )}

              {/* Input Box - ChatGPT Style */}
              <div className="relative">
                <div className="relative flex items-end bg-white border border-gray-300 rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Enter text or upload documents..."
                    rows={1}
                    className="flex-1 p-4 pr-24 resize-none focus:outline-none text-gray-800 max-h-64 overflow-y-auto"
                    style={{ minHeight: '56px' }}
                    disabled={isGenerating}
                  />
                  
                  <div className="absolute right-2 bottom-2 flex items-center gap-2">
                    {/* Upload Button */}
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                      disabled={isGenerating}
                      title="Attach files"
                    >
                      <Paperclip size={20} className="text-gray-600" />
                    </button>
                    
                    {/* Submit Button */}
                    <button
                      onClick={generateGraph}
                      disabled={isGenerating || (!inputText.trim() && uploadedFiles.length === 0)}
                      className="p-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                      title="Generate graph"
                    >
                      {isGenerating ? (
                        <Loader2 size={20} className="animate-spin" />
                      ) : (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M5 12h14M12 5l7 7-7 7"/>
                        </svg>
                      )}
                    </button>
                  </div>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".txt,.pdf,.docx,.csv"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>
                
                {/* Help Text */}
                <div className="mt-2 text-center text-xs text-gray-500">
                  Press Enter to submit, Shift + Enter for new line • Supports TXT, PDF, DOCX, CSV
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;