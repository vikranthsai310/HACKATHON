import React from 'react';
import { formatTimestamp } from '../services/api';
import '../styles/message.css';

/**
 * Message Component
 * 
 * Displays individual chat messages with different styles
 * based on message type (user, system, error)
 */
function Message({ message }) {
  const { type, content, timestamp } = message;
  
  /**
   * Get CSS class based on message type
   */
  const getMessageClass = () => {
    const classes = ['message'];
    classes.push(`message-${type}`);
    return classes.join(' ');
  };
  
  /**
   * Get avatar/icon for message type
   */
  const getAvatar = () => {
    switch (type) {
      case 'user':
        return '👤';
      case 'system':
        return '🤖';
      case 'error':
        return '⚠️';
      default:
        return '💬';
    }
  };
  
  /**
   * Get sender label
   */
  const getSenderLabel = () => {
    switch (type) {
      case 'user':
        return 'You';
      case 'system':
        return 'HRM Assistant';
      case 'error':
        return 'System Error';
      default:
        return 'System';
    }
  };
  
  /**
   * Render content with markdown-like formatting
   */
  const renderContent = () => {
    // Split by newlines and process each line
    const lines = content.split('\n');
    
    return lines.map((line, index) => {
      // Bold text: **text**
      let processed = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // Bullet points
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return (
          <div 
            key={index} 
            className="message-bullet"
            dangerouslySetInnerHTML={{ __html: processed }}
          />
        );
      }
      
      // Empty lines
      if (line.trim() === '') {
        return <br key={index} />;
      }
      
      return (
        <span 
          key={index} 
          className="message-line"
          dangerouslySetInnerHTML={{ __html: processed }}
        />
      );
    });
  };
  
  return (
    <div className={getMessageClass()}>
      <div className="message-avatar">
        {getAvatar()}
      </div>
      <div className="message-content">
        <div className="message-header">
          <span className="message-sender">{getSenderLabel()}</span>
          {timestamp && (
            <span className="message-time">{formatTimestamp(timestamp)}</span>
          )}
        </div>
        <div className="message-body">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default Message;
