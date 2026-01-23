import React, { useState, useRef, useEffect, useCallback } from 'react';
import Message from './Message';
import DecisionCard from './DecisionCard';
import InputBar from './InputBar';
import { decisionAPI, chatAPI, generateId } from '../services/api';
import '../styles/chatbot.css';

/**
 * ChatBot Component
 * 
 * Main container for the chat interface that manages:
 * - Conversation state
 * - API communication
 * - Message rendering
 * - Decision display
 */
function ChatBot() {
  // State
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const [userRole, setUserRole] = useState('admin');
  const [streamingSteps, setStreamingSteps] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  
  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingSteps, scrollToBottom]);
  
  // Add welcome message on mount
  useEffect(() => {
    const welcomeMessage = {
      id: generateId(),
      type: 'system',
      content: `Welcome to the HRM Decision System! 👋

I'm powered by Gemini LLM and Hierarchical Reasoning Model (HRM). Ask me anything and I'll process your request using advanced AI reasoning.`,
      timestamp: new Date().toISOString(),
    };
    
    setMessages([welcomeMessage]);
  }, []);
  
  /**
   * Add a message to the conversation
   */
  const addMessage = useCallback((message) => {
    setMessages(prev => [...prev, { ...message, id: message.id || generateId() }]);
  }, []);
  
  /**
   * Handle sending a message
   */
  const handleSendMessage = async (text) => {
    if (!text.trim() || isLoading) return;
    
    // Clear any previous errors
    setError(null);
    
    // Add user message
    const userMessage = {
      id: generateId(),
      type: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    addMessage(userMessage);
    
    // Set loading state
    setIsLoading(true);
    setIsStreaming(true);
    setStreamingSteps([]);
    
    try {
      // Use streaming API for real-time updates
      let finalDecision = null;
      
      decisionAPI.streamDecision(
        text,
        userRole,
        // On event
        (data) => {
          if (data.step === 'final') {
            finalDecision = data.decision;
          } else if (data.error) {
            setError(data.error);
          } else {
            setStreamingSteps(prev => [...prev, data]);
          }
        },
        // On error
        (err) => {
          console.error('Stream error:', err);
          const errorMsg = err.message || 'Failed to process request';
          setError(errorMsg);
          setIsLoading(false);
          setIsStreaming(false);
          
          // Add error message to chat
          addMessage({
            type: 'error',
            content: `Error: ${errorMsg}`,
            timestamp: new Date().toISOString(),
          });
        },
        // On complete
        () => {
          setIsStreaming(false);
          setStreamingSteps([]);
          
          if (finalDecision) {
            // Add decision response
            const decisionMessage = {
              id: generateId(),
              type: 'decision',
              content: finalDecision,
              timestamp: new Date().toISOString(),
            };
            addMessage(decisionMessage);
          }
          
          setIsLoading(false);
        }
      );
      
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.message || 'Failed to process request');
      setIsLoading(false);
      setIsStreaming(false);
      
      // Add error message
      addMessage({
        type: 'error',
        content: `Error: ${err.message || 'Something went wrong'}`,
        timestamp: new Date().toISOString(),
      });
    }
  };
  
  /**
   * Clear conversation
   */
  const handleClearChat = () => {
    setMessages([{
      id: generateId(),
      type: 'system',
      content: 'Conversation cleared. How can I help you?',
      timestamp: new Date().toISOString(),
    }]);
    setError(null);
    setStreamingSteps([]);
  };
  
  /**
   * Render streaming progress
   */
  const renderStreamingProgress = () => {
    if (!isStreaming || streamingSteps.length === 0) return null;
    
    const stepNames = {
      1: 'Preprocessing',
      2: 'LLM Interpretation',
      3: 'HRM Conversion',
      4: 'L1 Strategic Analysis',
      5: 'L2 Tactical Planning',
      6: 'L3 Operational Execution',
      7: 'Action Execution',
    };
    
    return (
      <div className="streaming-progress">
        <div className="streaming-header">
          <span className="streaming-icon">⚡</span>
          <span>Processing your request...</span>
        </div>
        <div className="streaming-steps">
          {streamingSteps.map((step, index) => (
            <div 
              key={index} 
              className={`streaming-step ${step.status === 'completed' ? 'completed' : 'active'}`}
            >
              <span className="step-indicator">
                {step.status === 'completed' ? '✓' : '○'}
              </span>
              <span className="step-name">
                {stepNames[step.step] || step.name}
              </span>
              {step.status === 'completed' && step.intent_type && (
                <span className="step-detail">Intent: {step.intent_type}</span>
              )}
              {step.status === 'completed' && step.risk_level && (
                <span className="step-detail risk">Risk: {step.risk_level}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  return (
    <div className="chatbot">
      {/* Header with controls */}
      <div className="chatbot-header">
        <div className="header-left">
          <span className="status-indicator online"></span>
          <span className="status-text">Gemini LLM + HRM Active</span>
        </div>
        <div className="header-right">
          <button className="clear-btn" onClick={handleClearChat} title="Clear chat">
            🗑️ Clear
          </button>
        </div>
      </div>
      
      {/* Messages container */}
      <div className="chatbot-messages">
        {messages.map((message) => {
          if (message.type === 'decision') {
            return (
              <DecisionCard 
                key={message.id} 
                decision={message.content}
                timestamp={message.timestamp}
              />
            );
          }
          return (
            <Message 
              key={message.id} 
              message={message}
            />
          );
        })}
        
        {/* Streaming progress */}
        {renderStreamingProgress()}
        
        {/* Loading indicator */}
        {isLoading && !isStreaming && (
          <div className="loading-indicator">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span>Processing...</span>
          </div>
        )}
        
        {/* Error display */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input bar */}
      <InputBar 
        onSend={handleSendMessage}
        disabled={isLoading}
        inputRef={inputRef}
        placeholder={isLoading ? 'Processing...' : 'Type your request...'}
      />
    </div>
  );
}

export default ChatBot;
