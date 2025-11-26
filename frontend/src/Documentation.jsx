import React from 'react';
import { Book, ArrowLeft, Info, FileText, Code } from 'lucide-react';
import SettingsMenu from './components/SettingsMenu';
import { Link } from 'react-router-dom';

const Documentation = ({ onNavigate }) => {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 overflow-y-auto h-full">
      {/* Header */}
      <header className="border-b dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Book className="text-blue-600 dark:text-blue-400" size={24} />
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">
              Knowledge Navigator Docs
            </h1>
          </div>
          <Link 
            to="/"
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to App
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          {/* Sidebar Navigation */}
          <aside className="hidden md:block col-span-1">
            <nav className="sticky top-24 space-y-1">
              <a href="#getting-started" className="block px-3 py-2 text-sm font-medium rounded-md bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                Getting Started
              </a>
              <a href="#uploading" className="block px-3 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md">
                Uploading Files
              </a>
              <a href="#api-config" className="block px-3 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md">
                API Configuration
              </a>
            </nav>
          </aside>

          {/* Content Area */}
          <div className="col-span-1 md:col-span-3 space-y-12">
            
            {/* Section: Getting Started */}
            <section id="getting-started" className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b dark:border-gray-700">
                <Info className="text-blue-500" size={20} />
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Getting Started</h2>
              </div>
              <p className="leading-relaxed text-gray-600 dark:text-gray-300">
                The Knowledge Navigator allows you to convert unstructured text documents into interactive knowledge graphs. 
                Simply input text or upload files, and our system will extract entities and relationships to visualize connections.
              </p>
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-lg p-4">
                <h4 className="font-semibold text-blue-800 dark:text-blue-300 mb-2">Quick Tip</h4>
                <p className="text-sm text-blue-700 dark:text-blue-400">
                  For best results, ensure your input text has clear subjects and relationships.
                </p>
              </div>
            </section>

            {/* Section: Uploading */}
            <section id="uploading" className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b dark:border-gray-700">
                <FileText className="text-green-500" size={20} />
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Supported Formats</h2>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                We currently support the following file types for analysis:
              </p>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
                {['.TXT (Plain Text)', '.PDF (Documents)', '.DOCX (Word)', '.CSV (Data Tables)'].map((fmt) => (
                  <li key={fmt} className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="font-mono text-sm">{fmt}</span>
                  </li>
                ))}
              </ul>
            </section>

            {/* Section: API Config */}
            <section id="api-config" className="space-y-4">
              <div className="flex items-center gap-2 pb-2 border-b dark:border-gray-700">
                <Code className="text-purple-500" size={20} />
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Configuration</h2>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                You can customize the generation process via the Settings menu.
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b dark:border-gray-700">
                      <th className="py-3 pr-4 font-semibold">Parameter</th>
                      <th className="py-3 px-4 font-semibold">Description</th>
                      <th className="py-3 pl-4 font-semibold">Default</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    <tr className="border-b dark:border-gray-800">
                      <td className="py-3 pr-4 font-mono text-purple-600 dark:text-purple-400">Model Name</td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">The LLM model used for extraction</td>
                      <td className="py-3 pl-4 text-gray-500">gpt-4o</td>
                    </tr>
                    <tr className="border-b dark:border-gray-800">
                      <td className="py-3 pr-4 font-mono text-purple-600 dark:text-purple-400">Temperature</td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">Controls randomness (0.0 - 1.0)</td>
                      <td className="py-3 pl-4 text-gray-500">0.3</td>
                    </tr>
                    <tr>
                      <td className="py-3 pr-4 font-mono text-purple-600 dark:text-purple-400">Chunk Size</td>
                      <td className="py-3 px-4 text-gray-600 dark:text-gray-400">Characters per text segment</td>
                      <td className="py-3 pl-4 text-gray-500">1000</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <p className="text-gray-600 dark:text-gray-300">
                You can customize the generation process via the Settings menu.
              </p>

              <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-6">

                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  How to Get an API Key, Base URL, and Model Name (Easy Guide)
                </h3>

                <p className="text-gray-700 dark:text-gray-300">
                  To use AI models, you need three things:
                </p>

                <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 ml-4">
                  <li><strong>An API Key</strong> — this is a secret password.</li>
                  <li><strong>A Base URL</strong> — this tells the app which website access.</li>
                  <li><strong>A Model Name</strong> — this tells the app which AI to use.</li>
                </ul>

                <p className="text-gray-700 dark:text-gray-300">
                  Below are super simple steps for getting these from Google Gemini and OpenAI.
                </p>

                {/* GOOGLE GEMINI */}
                <div className="p-3 rounded-md bg-blue-50 dark:bg-blue-900/20">
                  <h4 className="font-semibold text-blue-700 dark:text-blue-300">Google Gemini</h4>

                  <h5 className="font-semibold text-blue-600 dark:text-blue-400 mt-2">1. How to Get Your API Key</h5>
                  <ol className="list-decimal list-inside text-gray-700 dark:text-gray-300 space-y-1 mt-1">
                    <li>Go to: <a href="https://aistudio.google.com" className="text-blue-600 underline" target="_blank" rel="noreferrer">aistudio.google.com</a></li>
                    <li>Sign in with your Google account.</li>
                    <li>On the left side, click <strong>API Keys</strong>.</li>
                    <li>Click <strong>Create API Key</strong>.</li>
                    <li>Copy the key — this is your Google Gemini API key.</li>
                  </ol>

                  <h5 className="font-semibold text-blue-600 dark:text-blue-400 mt-4">2. How to Get Your Base URL</h5>
                  <p className="text-gray-700 dark:text-gray-300 mt-1">
                    The base URL for Gemini is:
                  </p>
                  <pre className="bg-white dark:bg-gray-900 text-sm p-2 rounded border border-gray-200 dark:border-gray-700 mt-1">
https://generativelanguage.googleapis.com/v1beta
                  </pre>

                  <p className="text-gray-700 dark:text-gray-300 text-sm mt-2">
                    Just copy that line and paste it into the "Base URL" box in Settings.
                  </p>

                  <h5 className="font-semibold text-blue-600 dark:text-blue-400 mt-4">3. How to Find Your Model Name</h5>
                  <ol className="list-decimal list-inside text-gray-700 dark:text-gray-300 space-y-1 mt-1">
                    <li>While still on <strong>AI Studio</strong>, click on <strong>Playground</strong> or start a new chat.</li>
                    <li>At the top of the page, you will see a dropdown for the model.</li>
                    <li>Click the dropdown and look at the model name, such as <code className="font-mono text-xs">gemini-1.5-flash</code> or <code className="font-mono text-xs">gemini-1.5-pro</code>.</li>
                    <li>Copy that text exactly — that is your <strong>Model Name</strong>.</li>
                  </ol>
                  <p className="text-gray-700 dark:text-gray-300 text-sm mt-2">
                    Paste this into the "Model Name" box in Settings when you want to use Gemini.
                  </p>
                </div>

                {/* OPENAI */}
                <div className="p-3 rounded-md bg-purple-50 dark:bg-purple-900/20">
                  <h4 className="font-semibold text-purple-700 dark:text-purple-300">OpenAI</h4>

                  <h5 className="font-semibold text-purple-600 dark:text-purple-400 mt-2">1. How to Get Your API Key</h5>
                  <ol className="list-decimal list-inside text-gray-700 dark:text-gray-300 space-y-1 mt-1">
                    <li>Go to: <a href="https://platform.openai.com" className="text-purple-600 underline" target="_blank" rel="noreferrer">platform.openai.com</a></li>
                    <li>Log in or create a free account.</li>
                    <li>Click <strong>Dashboard</strong> on the left.</li>
                    <li>Click <strong>API Keys</strong>.</li>
                    <li>Press <strong>Create new secret key</strong>.</li>
                    <li>Copy the key — this is your OpenAI API key.</li>
                  </ol>

                  <h5 className="font-semibold text-purple-600 dark:text-purple-400 mt-4">2. How to Get Your Base URL</h5>
                  <p className="text-gray-700 dark:text-gray-300 mt-1">
                    The base URL for OpenAI is:
                  </p>
                  <pre className="bg-white dark:bg-gray-900 text-sm p-2 rounded border border-gray-200 dark:border-gray-700 mt-1">
https://api.openai.com/v1
                  </pre>

                  <p className="text-gray-700 dark:text-gray-300 text-sm mt-2">
                    Copy this and paste it into the "Base URL" field in your Settings.
                  </p>

                  <h5 className="font-semibold text-purple-600 dark:text-purple-400 mt-4">3. How to Find Your Model Name</h5>
                  <ol className="list-decimal list-inside text-gray-700 dark:text-gray-300 space-y-1 mt-1">
                    <li>In the OpenAI website, click on <strong>Playground</strong>.</li>
                    <li>At the top of the Playground, look for the <strong>Model</strong> dropdown.</li>
                    <li>Click it and you will see names like <code className="font-mono text-xs">gpt-4o</code> or <code className="font-mono text-xs">gpt-4o-mini</code>.</li>
                    <li>Pick the one you want and copy the name exactly.</li>
                  </ol>
                  <p className="text-gray-700 dark:text-gray-300 text-sm mt-2">
                    Paste this into the "Model Name" box in Settings when you want to use OpenAI.
                  </p>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Once you have the API key, base URL, and model name for the service you want to use, open the <strong>Settings</strong> menu inside the app and paste them in.
                </p>

              </div>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Documentation;
