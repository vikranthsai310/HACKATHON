import React, { useState } from 'react';
import { formatTimestamp, decisionAPI } from '../services/api';
import '../styles/decision-card.css';

/**
 * DecisionCard Component
 * 
 * Displays HRM decision results with:
 * - Status indicator
 * - Summary
 * - Actions completed
 * - Expandable explanation
 * - Audit trail
 */
function DecisionCard({ decision, timestamp }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showAuditTrail, setShowAuditTrail] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  
  if (!decision) return null;
  
  const {
    decision_id,
    status,
    summary,
    actions_completed = [],
    explanation: builtInExplanation,
    confidence,
    audit_trail = {},
  } = decision;
  
  /**
   * Get status color and icon
   */
  const getStatusInfo = () => {
    switch (status) {
      case 'SUCCESS':
        return { color: 'success', icon: '✅', label: 'Approved' };
      case 'DENIED':
        return { color: 'denied', icon: '❌', label: 'Denied' };
      case 'PARTIAL':
        return { color: 'partial', icon: '⚠️', label: 'Partial' };
      case 'PENDING':
        return { color: 'pending', icon: '⏳', label: 'Pending' };
      default:
        return { color: 'default', icon: '❓', label: status };
    }
  };
  
  const statusInfo = getStatusInfo();
  
  /**
   * Get risk level badge
   */
  const getRiskBadge = () => {
    const riskLevel = audit_trail?.L1_strategic?.risk_level;
    if (!riskLevel) return null;
    
    const riskColors = {
      LOW: 'risk-low',
      MEDIUM: 'risk-medium',
      HIGH: 'risk-high',
      CRITICAL: 'risk-critical',
    };
    
    return (
      <span className={`risk-badge ${riskColors[riskLevel] || ''}`}>
        {riskLevel}
      </span>
    );
  };
  
  /**
   * Load detailed explanation
   */
  const loadExplanation = async () => {
    if (explanation || !decision_id) return;
    
    setLoadingExplanation(true);
    try {
      const data = await decisionAPI.getExplanation(decision_id);
      setExplanation(data);
    } catch (error) {
      console.error('Failed to load explanation:', error);
    }
    setLoadingExplanation(false);
  };
  
  /**
   * Render action list
   */
  const renderActions = () => {
    if (!actions_completed.length) {
      return <p className="no-actions">No actions executed</p>;
    }
    
    return (
      <ul className="action-list">
        {actions_completed.map((action, index) => (
          <li key={index} className={`action-item ${action.status?.toLowerCase()}`}>
            <span className="action-icon">
              {action.status === 'SUCCESS' ? '✓' : action.status === 'FAILED' ? '✗' : '○'}
            </span>
            <span className="action-name">{action.action}</span>
            <span className="action-status">{action.status}</span>
          </li>
        ))}
      </ul>
    );
  };
  
  /**
   * Render HRM trace
   */
  const renderHRMTrace = () => {
    const levels = [
      { key: 'L1_strategic', label: 'L1 Strategic', icon: '🎯' },
      { key: 'L2_tactical', label: 'L2 Tactical', icon: '📋' },
      { key: 'L3_operational', label: 'L3 Operational', icon: '⚡' },
    ];
    
    return (
      <div className="hrm-trace">
        {levels.map(({ key, label, icon }) => {
          const levelData = audit_trail[key];
          if (!levelData) return null;
          
          return (
            <div key={key} className="hrm-level">
              <div className="level-header">
                <span className="level-icon">{icon}</span>
                <span className="level-label">{label}</span>
              </div>
              <div className="level-content">
                {key === 'L1_strategic' && (
                  <>
                    <p><strong>Goal:</strong> {levelData.goal}</p>
                    <p><strong>Risk:</strong> {levelData.risk_level}</p>
                    <p><strong>Priority:</strong> {levelData.priority}/10</p>
                  </>
                )}
                {key === 'L2_tactical' && (
                  <>
                    <p><strong>Strategy:</strong> {levelData.strategy}</p>
                    <p><strong>Policy:</strong> {levelData.policy}</p>
                    <p><strong>Subsystem:</strong> {levelData.subsystem}</p>
                  </>
                )}
                {key === 'L3_operational' && (
                  <>
                    <p><strong>Actions:</strong> {levelData.total_actions}</p>
                    <p><strong>Successful:</strong> {levelData.successful_actions}</p>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };
  
  return (
    <div className={`decision-card ${statusInfo.color}`}>
      {/* Header */}
      <div className="decision-header">
        <div className="decision-status">
          <span className="status-icon">{statusInfo.icon}</span>
          <span className="status-label">{statusInfo.label}</span>
          {getRiskBadge()}
        </div>
        <div className="decision-meta">
          {decision_id && (
            <span className="decision-id" title={decision_id}>
              #{decision_id.slice(0, 8)}
            </span>
          )}
          {timestamp && (
            <span className="decision-time">{formatTimestamp(timestamp)}</span>
          )}
        </div>
      </div>
      
      {/* Summary */}
      <div className="decision-summary">
        <p>{summary}</p>
      </div>
      
      {/* Confidence */}
      {confidence !== undefined && (
        <div className="decision-confidence">
          <span className="confidence-label">Confidence:</span>
          <div className="confidence-bar">
            <div 
              className="confidence-fill" 
              style={{ width: `${confidence * 100}%` }}
            ></div>
          </div>
          <span className="confidence-value">{Math.round(confidence * 100)}%</span>
        </div>
      )}
      
      {/* Actions */}
      <div className="decision-actions">
        <h4>Actions</h4>
        {renderActions()}
      </div>
      
      {/* Expand/Collapse Button */}
      <button 
        className="expand-btn"
        onClick={() => {
          setIsExpanded(!isExpanded);
          if (!isExpanded) loadExplanation();
        }}
      >
        {isExpanded ? '▲ Hide Details' : '▼ Show Details'}
      </button>
      
      {/* Expanded Details */}
      {isExpanded && (
        <div className="decision-details">
          {/* Explanation */}
          <div className="detail-section">
            <h4>📖 Explanation</h4>
            {loadingExplanation ? (
              <p className="loading">Loading explanation...</p>
            ) : (
              <pre className="explanation-text">
                {explanation?.strategic_explanation || builtInExplanation || 'No explanation available'}
              </pre>
            )}
          </div>
          
          {/* HRM Trace */}
          <div className="detail-section">
            <h4>🧠 HRM Reasoning Trace</h4>
            {renderHRMTrace()}
          </div>
          
          {/* Audit Trail Toggle */}
          <button 
            className="audit-toggle"
            onClick={() => setShowAuditTrail(!showAuditTrail)}
          >
            {showAuditTrail ? '🔒 Hide Audit Trail' : '🔓 Show Audit Trail'}
          </button>
          
          {showAuditTrail && (
            <div className="audit-trail">
              <pre>{JSON.stringify(audit_trail, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DecisionCard;
