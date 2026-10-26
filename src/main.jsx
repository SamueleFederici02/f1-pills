import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("App Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#080a0f] text-white flex flex-col items-center justify-center p-6 text-center">
          <div className="max-w-md bg-red-950/40 border border-red-500/40 rounded-2xl p-6 shadow-xl space-y-4">
            <h2 className="text-xl font-black font-f1-display text-red-500">ERRORE DI CARICAMENTO</h2>
            <p className="text-xs text-slate-300">
              Si è verificato un errore nell'applicazione:
            </p>
            <pre className="bg-black/60 p-3 rounded-lg text-left text-xs font-mono text-red-300 overflow-x-auto">
              {this.state.error?.message || String(this.state.error)}
            </pre>
            <button
              onClick={() => {
                localStorage.clear();
                window.location.reload();
              }}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold uppercase tracking-wider transition-colors"
            >
              Ricarica Pagina & Cache
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
)
