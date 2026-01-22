import React, { useState, useEffect } from 'react';
import '../styles/input-bar.css';

/**
 * InputBar Component
 * 
 * Text input with send button and keyboard support
 */
function InputBar({ onSend, disabled, inputRef, placeholder }) {
  const [text, setText] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  
  // Focus input on mount
  useEffect(() => {
    inputRef?.current?.focus();
  }, [inputRef]);
  
  /**
   * Handle form submission
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText('');
    }
  };
  
  /**
   * Handle key press
   */
  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  /**
   * Handle text change
   */
  const handleChange = (e) => {
    setText(e.target.value);
  };
  
  return (
    <form className={`input-bar ${isFocused ? 'focused' : ''}`} onSubmit={handleSubmit}>
      <div className="input-container">
        <textarea
          ref={inputRef}
          className="message-input"
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder || 'Type your request...'}
          disabled={disabled}
          rows={1}
          autoComplete="off"
        />
        <button 
          type="submit" 
          className={`send-btn ${text.trim() && !disabled ? 'active' : ''}`}
          disabled={!text.trim() || disabled}
          title="Send message"
        >
          <span className="send-icon">➤</span>
        </button>
      </div>
      <div className="input-hints">
        <span className="hint">Press Enter to send</span>
        <span className="hint">•</span>
        <span className="hint">Shift+Enter for new line</span>
      </div>
    </form>
  );
}

export default InputBar;
