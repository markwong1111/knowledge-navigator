# Knowledge Navigator

A full-stack application for generating interactive knowledge graphs from text and documents using AI.

## Quick Start Guide

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/app/apikey))

### Installation & Setup

1. **Clone the repository**
   ```bash
   cd /knowledge-navigator
   ```

2. **Set up the Backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up the Frontend**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the Backend Server** (Terminal 1)
   ```bash
   cd backend
   source venv/bin/activate
   python server.py
   ```
   Backend runs on `http://localhost:5000`

2. **Start the Frontend** (Terminal 2)
  
   a. In the .env file, please change the `VITE_API_BASE_URL` to `http://localhost:5000`

   b. 

   ```bash
   cd frontend
   npm run dev
   ```
   Frontend runs on `http://localhost:5173`

3. **Configure API Settings**
   - Open the app in your browser (`http://localhost:5173`)
   - Click the ⚙️ Settings icon
   - Enter your Google Gemini API Key
   - Select model (recommended: `gemini-1.5-flash`)
   - Click "Save Settings"

4. **Generate a Knowledge Graph**
   - Upload files (PDF, TXT, DOCX, CSV) or enter text
   - Click "Generate Knowledge Graph"
   - Wait for the interactive graph to appear

### Project Structure

```
knowledge-navigator/
├── frontend/          # React + Vite application
│   ├── src/
│   │   ├── App.jsx           # Main application component
│   │   ├── main.jsx          # Entry point
|   |   └── Documentation.jsx # Documentaiton page
│   └── package.json
│
└── backend/           # Python Flask server
    ├── server.py      # API server
    ├── app.py         # Graph generation logic
    └── src/
        ├── llm_config.py              # LLM configuration
        ├── associational_algorithm.py # Graph creation
        ├── generate_knowledge_graph.py # Visualization
        └── file_reader.py             # File processing
```

### Troubleshooting

- **CORS errors**: Ensure both servers are running on the correct ports
- **API Key errors**: Verify your Google Gemini API key in Settings
- **Module not found**: Run `pip install -r requirements.txt` in backend
- **Port already in use**: Kill the process or change the port in server config

---

## React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh