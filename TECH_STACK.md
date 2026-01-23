# 🏗️ COMPLETE TECH STACK - HRM Decision System

## Overview
Hybrid AI system combining **LLM** (Large Language Model) with **HRM** (Hierarchical Reasoning Model) for advanced decision-making and puzzle-solving.

---

## 🎯 CORE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                     │
│                                                               +++++++++   │
│  React 18.2.0 | Vite 5.0.0 | JavaScript/JSX                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP/REST
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  BACKEND API (FastAPI)                          │
│                                                                  │
│  FastAPI 0.109.0 | Uvicorn 0.27.0 | Python 3.x               │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  Chat Router     │  │Decision Router│  │  Main Router     │ │
│  │  (LLM Handling)  │  │(HRM Engine)   │  │  (API Routes)    │ │
│  └──────────────────┘  └──────────────┘  └──────────────────┘ │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Preprocessor     │  │ Validator    │  │  Schema          │ │
│  │ (Data Cleaning)  │  │ (Rules Check)│  │ (Pydantic)       │ │
│  └──────────────────┘  └──────────────┘  └──────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  LLM Interpreter │ │ HRM Engine   │ │ Decision Engine  │
│ (GoogleAI/OpenAI)│ │ (Deep Learning│ │ (Logic+Rules)    │
│                  │ │ PyTorch)     │ │                  │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

---

## 📦 TECH STACK BREAKDOWN

### 1️⃣ FRONTEND STACK
**Location:** `frontend/`

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 18.2.0 | UI Library |
| **Build Tool** | Vite | 5.0.0 | Fast bundler & dev server |
| **Plugin** | @vitejs/plugin-react | 4.2.1 | JSX support |
| **Language** | JavaScript/JSX | ES2020+ | Frontend code |
| **State** | React Hooks | Native | State management |
| **HTTP** | Fetch API | Native | API communication |

**Structure:**
```
frontend/
├── src/
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # Entry point
│   ├── components/       # Reusable components
│   ├── services/         # API services
│   └── styles/           # CSS/styling
├── package.json          # Dependencies
└── vite.config.js        # Build config
```

---

### 2️⃣ BACKEND API STACK
**Location:** `backend/`

#### Core Framework
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.109.0 | Async web framework |
| **ASGI Server** | Uvicorn | 0.27.0 | ASGI server |
| **Data Validation** | Pydantic | 2.5.3 | Request/response schemas |
| **Settings** | Pydantic-settings | 2.1.0 | Config management |

#### LLM & AI Integration
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Google AI** | google-generativeai | 0.3.2 | Google Gemini API |
| **OpenAI** | openai | 1.10.0 | GPT API (optional) |
| **NLP Processing** | NLTK | 3.8.1 | Text tokenization |
| **NLP Pipeline** | spaCy | 3.7.2 | Text processing |

#### Deep Learning & HRM
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **ML Framework** | PyTorch | ≥2.0.0 | Neural networks |
| **Numerical** | NumPy | ≥1.24.0 | Array operations |
| **Build Tools** | Ninja | Latest | C++ extension builder |
| **Wheel** | Wheel | Latest | Package distribution |

#### API & Utilities
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **HTTP Client** | httpx | 0.26.0 | Async HTTP requests |
| **HTTP Client** | requests | 2.31.0 | Sync HTTP requests |
| **Form Parser** | python-multipart | 0.0.6 | Multipart form data |
| **Environment** | python-dotenv | 1.0.0 | .env file loading |
| **Config** | PyYAML | 6.0.1 | YAML parsing |
| **Logging** | python-json-logger | 2.0.7 | JSON logging |
| **Date Utils** | python-dateutil | 2.8.2 | Date/time handling |

**Backend Structure:**
```
backend/
├── app/
│   ├── main.py              # FastAPI app instance
│   ├── api/
│   │   ├── routes.py        # Main API routes
│   │   ├── chat.py          # Chat/LLM routes
│   │   ├── decision.py      # Decision/HRM routes
│   │   └── middleware.py    # Custom middleware
│   ├── core/
│   │   ├── preprocessor.py  # Data preprocessing
│   │   └── schema_validator.py  # Validation logic
│   ├── schemas/
│   │   └── request_schema.py # Request models
│   ├── utils/               # Utility functions
│   └── config.py            # Configuration
├── requirements.txt         # Python dependencies
└── tests/                   # Test suite
```

---

### 3️⃣ HRM (HIERARCHICAL REASONING MODEL) STACK
**Location:** `HRM-main/`

#### Core ML Stack
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | PyTorch | ≥2.0.0 | Neural network training |
| **Optimization** | adam-atan2 | Latest | Adam optimizer variant |
| **Tensor Ops** | einops | Latest | Einstein summation |
| **Progress Bar** | tqdm | Latest | Progress visualization |
| **Utilities** | coolname | Latest | Naming generator |
| **Config** | pydantic | Latest | Schema validation |
| **CLI** | argdantic | Latest | Argument parsing |

#### Experiment Tracking & Distributed Training
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Experiment Track** | Weights & Biases | Latest | Metric visualization |
| **Config Management** | hydra-core | Latest | Experiment configs |
| **Config Format** | omegaconf | Latest | YAML config |
| **Model Hub** | huggingface_hub | Latest | Model download/upload |

#### Attention Mechanisms
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **FlashAttention** | flash-attn | 2/3 | Optimized attention |
| **RotaryEmbedding** | Custom | In-house | Position encoding |
| **Sparse Embedding** | Custom | In-house | Efficient embeddings |

**HRM Architecture:**
```
HRM-main/
├── models/
│   ├── hrm/
│   │   └── hrm_act_v1.py    # Main HRM model (27M params)
│   ├── common.py             # Shared utilities
│   ├── layers.py             # Custom layers
│   ├── losses.py             # Loss functions
│   └── sparse_embedding.py   # Sparse embedding
├── dataset/
│   ├── build_sudoku_dataset.py     # Sudoku data
│   ├── build_arc_dataset.py        # ARC benchmark data
│   ├── build_maze_dataset.py       # Maze data
│   └── common.py                   # Dataset utils
├── config/
│   ├── cfg_pretrain.yaml           # Training config
│   └── arch/
│       └── hrm_v1.yaml             # Model arch config
├── pretrain.py              # Training script
├── evaluate.py              # Evaluation script
├── puzzle_dataset.py        # Data loader
├── puzzle_visualizer.html   # Visualization tool
└── requirements.txt         # Dependencies
```

---

## 🔗 DATA FLOW

### Request → Response Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER REQUEST (Frontend)                                  │
│    Input: Text query, puzzle, or decision problem           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ 2. API RECEIVES REQUEST (FastAPI)                          │
│    ├─ Route matching                                       │
│    ├─ Pydantic validation                                  │
│    └─ CORS verification                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼──────────────┐    ┌──────────▼──────────────┐
│ 3A. CHAT ROUTE        │    │ 3B. DECISION ROUTE      │
│ (LLM Handling)        │    │ (HRM Reasoning)         │
│                       │    │                         │
│ ├─ Preprocess input   │    │ ├─ Preprocess input     │
│ ├─ Call LLM API       │    │ ├─ Run HRM model        │
│ │  (GoogleAI/OpenAI)  │    │ ├─ Validate output      │
│ ├─ Parse response     │    │ ├─ Apply rules engine   │
│ └─ Format output      │    │ └─ Generate reasoning   │
└────────┬──────────────┘    └──────────┬──────────────┘
         │                              │
         └──────────────┬───────────────┘
                        │
         ┌──────────────▼───────────────┐
         │ 4. MERGE RESULTS             │
         │                              │
         │ ├─ Compare LLM vs HRM        │
         │ ├─ Consensus decision        │
         │ ├─ Confidence scoring        │
         │ └─ Explanation generation    │
         └──────────────┬───────────────┘
                        │
┌───────────────────────▼────────────────────────────────────┐
│ 5. RETURN RESPONSE (JSON)                                  │
│                                                             │
│ {                                                           │
│   "llm_response": "...",                                   │
│   "hrm_response": "...",                                   │
│   "consensus": "...",                                      │
│   "confidence": 0.95,                                      │
│   "reasoning": "..."                                       │
│ }                                                           │
└───────────────────────┬────────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────────┐
│ 6. FRONTEND DISPLAYS RESULT                                │
│    ├─ Render response                                      │
│    ├─ Show reasoning chain                                 │
│    └─ Interactive follow-ups                               │
└───────────────────────────────────────────────────────────┘
```

---

## 🔧 DEVELOPMENT STACK

| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.8+ | Backend language |
| **Node.js** | 18+ | Frontend tooling |
| **npm** | 9+ | Package manager |
| **Git** | Latest | Version control |
| **Docker** | Optional | Containerization |
| **pytest** | Latest | Testing framework |
| **CUDA** | 12.6 | GPU acceleration (optional) |

---

## 📊 MODEL SPECIFICATIONS

### HRM Model
```
Architecture:    Hierarchical Recurrent Neural Network
Parameters:      27 Million (highly efficient)
Framework:       PyTorch
GPU Memory:      ~2-4 GB
Training Time:   ~10 hours (RTX 4070)
Inference:       <100ms per puzzle

Hierarchical Levels:
├─ L1: Strategic Planning (Abstract reasoning)
├─ L2: Tactical Moves (Constraint solving)
└─ L3: Operational Execution (Detailed computation)

Attention:       FlashAttention 2/3 (optimized)
Position Enc:    Rotary embeddings (RoPE)
Optimization:    Adam-atan2, Weight decay

Datasets:
├─ Sudoku (extreme difficulty)
├─ ARC-AGI (general reasoning)
├─ Mazes (path planning)
└─ ConceptARC (abstraction)
```

### LLM Integration
```
Primary:  Google Gemini (google-generativeai)
Fallback: OpenAI GPT (openai)

Capabilities:
├─ Text understanding
├─ Chain-of-thought reasoning
├─ Code generation
├─ Multi-lingual support
└─ Context window: 32K-100K tokens
```

---

## 🚀 DEPLOYMENT STACK

| Environment | Tech | Status |
|------------|------|--------|
| **Development** | FastAPI + Vite dev server | ✅ Active |
| **Local Testing** | Uvicorn + npm dev | ✅ Active |
| **Production Ready** | Uvicorn + nginx | 🔄 Configured |
| **CI/CD** | pytest + custom scripts | ✅ Setup |
| **Docker** | Multi-stage builds | 🔄 Optional |

---

## 📈 TESTING STACK

| Framework | Version | Purpose |
|-----------|---------|---------|
| **pytest** | Latest | Unit & integration tests |
| **Custom Scripts** | In-house | Performance benchmarks |
| **HRM Benchmarks** | Custom | Model validation |
| **LLM Tests** | Custom | API testing |

**Test Files:**
```
backend/tests/
├── test_api.py              # API endpoint tests
├── test_functional.py       # Business logic tests
├── test_performance.py      # Performance benchmarks
├── test_phase1.py           # Phase 1 validation
└── test_system.py           # System integration tests
```

---

## 🎯 KEY FEATURES BY STACK

### Frontend
- ✅ Real-time interactive UI
- ✅ React hooks for state management
- ✅ Fast dev server with Vite HMR
- ✅ Optimized production build
- ✅ Cross-browser compatibility

### Backend API
- ✅ Async FastAPI endpoints
- ✅ Type-safe request/response validation
- ✅ CORS support for frontend
- ✅ Multiple router modules
- ✅ Health check endpoints
- ✅ Comprehensive logging

### HRM Model
- ✅ 27M parameters (efficient)
- ✅ No pre-training required
- ✅ Solves Sudoku & ARC puzzles
- ✅ Multi-level hierarchical reasoning
- ✅ Optimized with FlashAttention

### LLM Integration
- ✅ Dual API support (Google + OpenAI)
- ✅ Fallback mechanisms
- ✅ Token counting & limit handling
- ✅ Error recovery

---

## 🔗 INTEGRATION POINTS

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ REST API (JSON over HTTP)
                 │
┌────────────────▼────────────────────────────────────────┐
│                  FASTAPI BACKEND                         │
│                                                           │
│  ├─ Route: /api/v1/chat      → LLM Handler             │
│  ├─ Route: /api/v1/decision  → HRM Engine              │
│  ├─ Route: /api/v1/analyze   → Decision Logic          │
│  └─ Route: /health            → Health Check           │
└────────────────┬────────────────────────────────────────┘
                 │
      ┌──────────┴──────────┬──────────────┐
      │                     │              │
      ▼                     ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ GoogleAI API │  │ OpenAI API   │  │ HRM Model    │
│ (Gemini)     │  │ (GPT-4)      │  │ (PyTorch)    │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 📝 CONFIGURATION FILES

| File | Purpose | Format |
|------|---------|--------|
| `frontend/vite.config.js` | Vite build config | JavaScript |
| `backend/requirements.txt` | Python dependencies | pip |
| `backend/.env.example` | Environment template | .env |
| `HRM-main/config/cfg_pretrain.yaml` | HRM training config | YAML |
| `HRM-main/config/arch/hrm_v1.yaml` | Model architecture | YAML |

---

## 🎓 SUMMARY TABLE

| Layer | Technology | Version | Key Role |
|-------|-----------|---------|----------|
| **UI** | React 18 + Vite 5 | 18.2.0 + 5.0.0 | Interactive interface |
| **API** | FastAPI + Uvicorn | 0.109.0 + 0.27.0 | Request routing |
| **Data Val** | Pydantic | 2.5.3 | Type safety |
| **LLM1** | Google Generative AI | 0.3.2 | Text generation |
| **LLM2** | OpenAI | 1.10.0 | Alternative LLM |
| **NLP** | NLTK + spaCy | 3.8.1 + 3.7.2 | Text processing |
| **DL** | PyTorch | ≥2.0.0 | Neural networks |
| **HRM** | Custom (PyTorch) | 27M params | Hierarchical reasoning |
| **Attention** | FlashAttention | 2/3 | Optimized transformers |
| **Tracking** | Weights & Biases | Latest | Experiment logging |
| **Config** | Hydra + OmegaConf | Latest | Configuration mgmt |
| **Testing** | pytest | Latest | Test framework |

---

## ✨ UNIQUE ARCHITECTURE HIGHLIGHTS

1. **Hybrid Decision Making**
   - LLM for semantic understanding
   - HRM for structured reasoning
   - Consensus mechanism for final decision

2. **Efficient HRM**
   - Only 27M parameters (vs billions for LLM)
   - Trains on 1000 samples (vs millions)
   - No pre-training required

3. **Multi-tier Reasoning**
   - L1: Abstract strategic planning
   - L2: Tactical constraint solving
   - L3: Detailed operational execution

4. **Production Ready**
   - Type-safe APIs (Pydantic)
   - Async I/O (FastAPI)
   - Comprehensive logging
   - Health checks
   - CORS enabled

5. **Scalable Testing**
   - ARC puzzle benchmarks
   - Sudoku extreme difficulty
   - Maze path finding
   - Career decision analysis

---

**Generated:** January 23, 2026  
**Last Updated:** With Sudoku & Career Analysis Tests
