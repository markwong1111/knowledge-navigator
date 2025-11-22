import React, { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Download, Loader2, X, Paperclip, Settings } from 'lucide-react';
import SettingsMenu from './components/SettingsMenu';

// TODO - update to backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
  const [inputText, setInputText] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [graphHtml, setGraphHtml] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [error, setError] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const fileInputRef = useRef(null);

  //settings variables
  const [apiKey, setApiKey] = useState('')
  const [baseURL, setBaseURL] = useState('')
  const [modelName, setModelName] = useState('')
  const [temp, setTemp] = useState('')

  // change chunk overlap depending on chunk size
  // overlap size should be roughly 1/20th of the chunks size
  const [chunkSize, setChunkSize] = useState('') 

  // Initialize theme on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

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

      // Add API credentials to form data
      formData.append('api_key', apiKey);
      formData.append('base_url', baseURL);
      formData.append('model_name', modelName);
      formData.append('temperature', temp);
      formData.append('chunk_size', chunkSize);
      

      // Add text if present
      if (inputText.trim()) {
        formData.append('text', inputText);
      }

      // Add files if present
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      // Call your Python backend API
      const response = await fetch(`${API_BASE_URL}/generate-graph/`, {
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
    <div className="flex flex-col h-screen bg-white dark:bg-gray-900">
      {graphHtml ? (
        // Graph Display View
        <div className="flex-1 flex flex-col">
          <div className="bg-white dark:bg-gray-900 border-b dark:border-gray-700 px-6 py-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Knowledge Graph</h2>
            <div className="flex gap-2">
              <button
                onClick={() => downloadGraph('html')}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm font-medium"
              >
                <Download size={16} />
                HTML
              </button>
              <button
                onClick={() => downloadGraph('json')}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm font-medium"
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
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm font-medium"
              >
                <X size={16} />
                New Graph
              </button>
              <button
                onClick={() => setSettingsOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg transition-colors text-sm font-medium"
              >
                <Settings size={16} />
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
        // Input View
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="px-4 py-3 border-b dark:border-gray-700 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img 
                src="https://ideaspaces.net/wp-content/uploads/2024/06/cropped-ISbluelogocircleSM-1-1.png" 
                alt="Logo" 
                className="h-8 w-8" 
              />
            </div>
            <button
              onClick={() => setSettingsOpen(true)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings size={20} className="text-gray-600 dark:text-gray-400" />
            </button>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex items-center justify-center p-4">
            <div className="w-full max-w-3xl">
              {/* Welcome Message - Hidden if error or files uploaded */}
              {!error && uploadedFiles.length === 0 && (
                <div className="text-center mb-12">
                  <h2 className="text-3xl font-semibold text-gray-800 dark:text-white mb-3">
                    Knowledge Navigator
                  </h2>
                </div>
              )}

              {/* File Upload Display */}
              {uploadedFiles.length > 0 && (
                <div className="mb-4 space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-4 py-3 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-700 dark:text-gray-300">{file.name}</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
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

              {/* Input Box */}
              <div className="relative">
                <div className="relative flex items-end">
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Enter text to generate graph..."
                    rows={Math.max(2, Math.min((inputText.split('\n').length || 0) + 1, 5))}
                    className="flex-1 resize-none focus:outline-none text-gray-800 dark:text-white bg-gray-100 dark:bg-gray-800 rounded-2xl overflow-y-auto shadow-sm hover:shadow-md transition-shadow custom-scrollbar"
                    style={{ 
                      minHeight: '88px', 
                      maxHeight: '200px', 
                      paddingTop: '16px',
                      paddingLeft: '16px',
                      paddingRight: '56px',
                      paddingBottom: '60px',
                    }}
                    disabled={isGenerating}
                    ref={(el) => {
                      if (el) el.scrollTop = el.scrollHeight;
                    }}
                  />
                                                    
                  {/* File Upload Button - Left side */}
                  <div className="absolute left-4 bottom-3">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      disabled={isGenerating}
                      className="flex items-center justify-center p-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                      title="Upload files"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 5v14M5 12h14"/>
                      </svg>
                    </button>
                  </div>

                  {/* Submit Button - Right side */}
                  <div className="absolute right-4 bottom-3">
                    <button
                      onClick={generateGraph}
                      disabled={isGenerating || (!inputText.trim() && uploadedFiles.length === 0)}
                      className="flex items-center justify-center p-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                      title="Generate graph"
                    >
                      {isGenerating ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M12 19V5M5 12l7-7 7 7"/>
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
                <div className="mt-2 text-center text-xs text-gray-500 dark:text-gray-400">
                  Press Enter to submit, Shift + Enter for new line • Supports TXT, PDF, DOCX, CSV
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

         {/* //settings variables
  const [apiKey, setApiKey] = useState('')
  const [baseURL, setBaseURL] = useState('')
  const [modelName, setModelName] = useState('')
  const [temp, setTemp] = useState('')

  // change chunk overlap depending on chunk size
  // overlap size should be roughly 1/20th of the chunks size
  const [chunkSize, setChunkSize] = useState('')  */}
      <SettingsMenu
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}

        apiKey={apiKey}
        setApiKey={setApiKey}

        baseURL={baseURL}
        setBaseURL={setBaseURL}

        modelName={modelName}
        setModelName={setModelName}

        temp={temp}
        setTemp={setTemp}

        chunkSize={chunkSize}
        setChunkSize={setChunkSize} 
      />

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
          margin-bottom: 60px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #d1d5db;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #9ca3af;
        }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #4b5563;
        }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #6b7280;
        }
      `}</style>
    </div>
  );
}

export default App;