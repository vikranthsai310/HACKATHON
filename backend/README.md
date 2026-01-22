# HRM Decision System - Backend

Python backend for the Hybrid Decision-Making System combining LLM interpretation with Hierarchical Reasoning Model.

## 🏗️ Architecture

```
User Input (Natural Language)
        ↓
NLP Preprocessor
        ↓
LLM Interpreter (Gemini)
        ↓
HRM Engine (Hierarchical Reasoning)
        ↓
Action Executor
        ↓
Decision Output
```

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA for GPU acceleration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

### 3. Run the Server

```bash
# Development mode with auto-reload
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Main Endpoints

### Complete Decision Pipeline
```http
POST /api/v1/decision
```
Processes a natural language request through the entire pipeline.

**Example Request:**
```json
{
  "user_id": "admin-001",
  "message": "Block all suspicious IP addresses from the last 24 hours",
  "context": {
    "user_role": "security_admin"
  }
}
```

### Component Testing Endpoints

- `POST /api/v1/preprocess` - Test NLP preprocessor
- `POST /api/v1/interpret` - Test LLM interpretation
- `POST /api/v1/hrm-input` - Generate HRM hierarchical input
- `POST /api/v1/reason` - Test HRM reasoning engine

### Monitoring & Audit

- `GET /api/v1/audit-logs` - Retrieve audit logs
- `GET /health` - Health check endpoint

## 🧪 Testing

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Complete decision request
curl -X POST "http://localhost:8000/api/v1/decision" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "message": "Block IP 192.168.1.100"
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/decision",
    json={
        "user_id": "admin-001",
        "message": "Show me all login attempts from yesterday"
    }
)

print(response.json())
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # API endpoints
│   │   └── middleware.py      # Request/response middleware
│   ├── core/
│   │   ├── preprocessor.py    # NLP preprocessing
│   │   ├── llm_interpreter.py # Gemini LLM integration
│   │   ├── hrm_engine.py      # HRM reasoning engine
│   │   ├── action_executor.py # Action execution
│   │   └── schema_validator.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── request_schema.py  # Pydantic models
│   └── utils/
├── config/
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Configuration

### Modes of Operation

The system supports multiple modes for development and testing:

1. **LLM Mode**
   - `MOCK`: Pattern-based interpretation (no API key needed)
   - `GEMINI`: Uses Gemini API for interpretation

2. **HRM Mode**
   - `SIMULATION`: Rule-based simulation (default)
   - `MODEL`: Uses actual HRM neural network (requires model weights)

3. **Executor Mode**
   - `DRY_RUN`: Simulates actions without execution (default)
   - `LIVE`: Actually executes actions (use with caution!)

Change modes via API:
```bash
# Set executor to dry-run mode
curl -X POST "http://localhost:8000/api/v1/config/executor-mode?dry_run=true"

# Check current modes
curl http://localhost:8000/api/v1/config/llm-mode
curl http://localhost:8000/api/v1/config/hrm-mode
curl http://localhost:8000/api/v1/config/executor-mode
```

## 🌟 Example Use Cases

### Security: Block Suspicious IPs
```json
{
  "user_id": "security-admin",
  "message": "Block all suspicious IP addresses from the last 24 hours"
}
```

### Access Management
```json
{
  "user_id": "manager",
  "message": "Grant user john.doe access to the analytics dashboard"
}
```

### Compliance
```json
{
  "user_id": "compliance-officer",
  "message": "Generate an audit report for the last month"
}
```

### Query
```json
{
  "user_id": "analyst",
  "message": "Show me all failed login attempts from yesterday"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   python -m app.main
   ```

2. **Gemini API errors**
   - Check your API key in `.env`
   - Verify API key at https://makersuite.google.com/app/apikey
   - System falls back to MOCK mode if API is unavailable

3. **Port already in use**
   ```bash
   # Use a different port
   uvicorn app.main:app --port 8001
   ```

## 📝 Development

### Adding New Actions

1. Add action handler to `action_executor.py`:
   ```python
   def _action_my_new_action(self, params: Dict, user_id: str) -> Dict:
       # Your implementation
       return {"status": "SUCCESS", "message": "Action completed"}
   ```

2. Register in action registry:
   ```python
   "MY_NEW_ACTION": self._action_my_new_action
   ```

### Running Tests

```bash
pytest
```

## 🔒 Security Notes

- Always use `dry_run=True` for testing
- Never commit `.env` file with real API keys
- Validate user permissions before executing actions
- Review audit logs regularly

## 📄 License

See LICENSE file in the project root.

## 🤝 Contributing

See CONTRIBUTING.md for development guidelines.
