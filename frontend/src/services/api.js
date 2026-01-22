/**
 * API Service for HRM Decision System
 * 
 * Handles all communication with the backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Custom error class for API errors
 */
class APIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Make API request with error handling
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `Request failed with status ${response.status}`,
        response.status,
        errorData
      );
    }
    
    // Handle empty responses
    const text = await response.text();
    return text ? JSON.parse(text) : null;
    
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error.message || 'Network error',
      0,
      { originalError: error }
    );
  }
}

/**
 * Chat API - Send messages and get decisions
 */
export const chatAPI = {
  /**
   * Send a chat message
   */
  async sendMessage(message, userId = 'user', sessionId = null) {
    return apiRequest('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        user_id: userId,
        session_id: sessionId,
      }),
    });
  },
  
  /**
   * Get chat examples
   */
  async getExamples() {
    return apiRequest('/chat/examples');
  },
  
  /**
   * Get session history
   */
  async getSessionHistory(sessionId) {
    return apiRequest(`/session/${sessionId}/history`);
  },
  
  /**
   * Clear session
   */
  async clearSession(sessionId) {
    return apiRequest(`/session/${sessionId}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Decision API - Full decision processing
 */
export const decisionAPI = {
  /**
   * Quick decision (simplified input)
   */
  async quickDecision(message, userRole = 'admin', dryRun = true) {
    return apiRequest('/decision/quick', {
      method: 'POST',
      body: JSON.stringify({
        message,
        user_id: 'chatbot-user',
        user_role: userRole,
        dry_run: dryRun,
      }),
    });
  },
  
  /**
   * Full decision processing
   */
  async processDecision(message, userId, context = {}) {
    return apiRequest('/decision/process', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userId,
        message,
        context,
      }),
    });
  },
  
  /**
   * Get decision by ID
   */
  async getDecision(decisionId) {
    return apiRequest(`/decision/${decisionId}`);
  },
  
  /**
   * Get decision explanation
   */
  async getExplanation(decisionId) {
    return apiRequest(`/decision/${decisionId}/explain`);
  },
  
  /**
   * Get decision audit trail
   */
  async getAuditTrail(decisionId) {
    return apiRequest(`/decision/${decisionId}/audit-trail`);
  },
  
  /**
   * Get decision history
   */
  async getHistory(page = 1, pageSize = 20) {
    return apiRequest(`/decision/history/list?page=${page}&page_size=${pageSize}`);
  },
  
  /**
   * Get analytics
   */
  async getAnalytics(hours = 24) {
    return apiRequest(`/decision/analytics/summary?hours=${hours}`);
  },
  
  /**
   * Stream decision processing (SSE)
   */
  streamDecision(message, userRole = 'admin', onEvent, onError, onComplete) {
    const url = `${API_BASE_URL}/decision/stream`;
    
    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        user_id: 'chatbot-user',
        user_role: userRole,
        dry_run: true,
      }),
    })
      .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        function read() {
          reader.read().then(({ done, value }) => {
            if (done) {
              onComplete?.();
              return;
            }
            
            const text = decoder.decode(value);
            const lines = text.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  onEvent?.(data);
                } catch (e) {
                  // Ignore parse errors
                }
              }
            }
            
            read();
          });
        }
        
        read();
      })
      .catch(error => {
        onError?.(error);
      });
  },
};

/**
 * System API - Configuration and status
 */
export const systemAPI = {
  /**
   * Health check
   */
  async healthCheck() {
    return apiRequest('/health', { method: 'GET' })
      .catch(() => apiRequest('/../health', { method: 'GET' }));
  },
  
  /**
   * Get configuration status
   */
  async getConfig() {
    return apiRequest('/decision/config/status');
  },
  
  /**
   * Set dry-run mode
   */
  async setDryRunMode(enabled) {
    return apiRequest('/decision/config/dry-run', {
      method: 'POST',
      body: JSON.stringify({ enabled }),
    });
  },
  
  /**
   * Get audit summary
   */
  async getAuditSummary(hours = 24) {
    return apiRequest(`/decision/audit/summary?hours=${hours}`);
  },
};

/**
 * Utility to generate unique IDs
 */
export function generateId() {
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Format timestamp for display
 */
export function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default {
  chatAPI,
  decisionAPI,
  systemAPI,
  generateId,
  formatTimestamp,
  APIError,
};
