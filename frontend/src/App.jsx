import { useState } from 'react'
import ChatBot from './components/ChatBot'
import './styles/App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">🧠</span>
          <h1>Gemini + HRM System</h1>
        </div>
        <p className="subtitle">Gemini LLM Understanding • HRM Processing • Advanced AI Reasoning</p>
      </header>
      <main className="app-main">
        <ChatBot />
      </main>
      <footer className="app-footer">
        <p>Powered by Google Gemini & Hierarchical Reasoning Model</p>
      </footer>
    </div>
  )
}

export default App
