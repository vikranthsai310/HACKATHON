import { useState } from 'react'
import ChatBot from './components/ChatBot'
import './styles/App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">🧠</span>
          <h1>HRM Decision System</h1>
        </div>
        <p className="subtitle">Hybrid AI-Powered Decision Making</p>
      </header>
      <main className="app-main">
        <ChatBot />
      </main>
      <footer className="app-footer">
        <p>LLM understands • HRM decides • Together = Safe AI</p>
      </footer>
    </div>
  )
}

export default App
