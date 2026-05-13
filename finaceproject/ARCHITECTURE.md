# Architecture & System Design

## System Overview

The AI Financial Intelligence Platform is a modular, scalable system designed to process financial documents and extract actionable insights using AI/ML techniques.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (UI Layer)                 │
│                    - Document Upload                             │
│                    - Dashboard & Visualization                   │
│                    - Q&A Interface                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ HTTP REST API
             │
┌────────────▼────────────────────────────────────────────────────┐
│                  FastAPI Backend (API Layer)                     │
│  Routes: /upload, /compare, /question, /export, /documents      │
└────────────┬────────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────────┐
│              Analysis Service (Orchestration Layer)              │
│  Coordinates all analysis components and manages data flow       │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬──────────────┐
    │                 │              │              │
    ▼                 ▼              ▼              ▼
┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Document   │  │ Metric       │  │ Risk         │  │ Document     │
│ Processor  │  │ Extraction   │  │ Detector     │  │ Comparator   │
│            │  │              │  │              │  │              │
│ • Extract  │  │ • Pattern    │  │ • Keyword    │  │ • Calculate  │
│ • Clean    │  │   matching   │  │   analysis   │  │   changes    │
│ • Chunk    │  │ • NLP        │  │ • Risk       │  │ • Trends     │
└────────────┘  │   extraction │  │   scoring    │  └──────────────┘
                └──────────────┘  └──────────────┘
    │                 │              │              │
    ▼                 ▼              ▼              ▼
    PDF           Financial       Risk          Ratios
    Text          Metrics         Report        Calculator
    ────────────┬──────────────┬──────────────┐
                │              │              │
                ▼              ▼              ▼
             ┌──────────────────────────────────────┐
             │   RAG Pipeline (Q&A Engine)          │
             │                                      │
             │ • Embeddings Generator              │
             │ • Vector Store (FAISS)              │
             │ • Retrieval Engine                  │
             │ • LLM Integration (Optional)        │
             └──────────────────────────────────────┘
```

## Core Components

### 1. Document Processor (`backend/core/document_processor.py`)

**Purpose**: Extract and preprocess text from PDF documents

**Key Functions**:
- `extract_text_from_pdf()`: Extracts text from PDF files using pdfplumber
- `clean_text()`: Removes noise and normalizes text
- `chunk_text()`: Splits text into overlapping chunks for processing

**Input**: PDF file
**Output**: List of cleaned, chunked text strings with metadata

**Technologies**: pdfplumber, regex

---

### 2. Financial Metric Extraction (`backend/core/metric_extraction.py`)

**Purpose**: Extract key financial metrics using pattern matching

**Key Functions**:
- `extract_metric_value()`: Uses regex patterns to find specific metrics
- `extract_all_metrics()`: Extracts all available metrics from text
- `extract_with_context()`: Returns metrics with source context

**Extracted Metrics**:
- Revenue
- Net Income
- Operating Income
- EBITDA
- Total Debt
- Cash Flow
- Total Assets
- Total Equity

**Pattern Matching Strategy**:
```python
Patterns for Revenue:
- "Total revenue: $X billion"
- "Net sales: $X million"
- "Operating revenue: $X thousand"
```

**Technologies**: Regex, Pattern Matching

---

### 3. Financial Ratio Calculator (`backend/core/ratio_calculator.py`)

**Purpose**: Calculate financial ratios from extracted metrics

**Key Functions**:
- `calculate_profit_margin()`: Net Income / Revenue
- `calculate_operating_margin()`: Operating Income / Revenue
- `calculate_debt_to_equity()`: Total Debt / Total Equity
- `calculate_roa()`: Return on Assets
- `calculate_roe()`: Return on Equity
- `calculate_all_ratios()`: Calculate all available ratios

**Technologies**: NumPy, Mathematical calculations

---

### 4. Risk Detector (`backend/core/risk_detector.py`)

**Purpose**: Identify and classify financial risks

**Risk Categories**:
1. **Regulatory Risk**: Compliance, legal issues, government regulations
2. **Liquidity Risk**: Cash flow, funding, debt covenants
3. **Market Risk**: Competition, pricing, demand changes
4. **Operational Risk**: Systems, infrastructure, technology
5. **Supply Chain Risk**: Inventory, sourcing, logistics
6. **Credit Risk**: Default, bankruptcy, counterparty
7. **Legal Risk**: Disputes, litigation, IP issues

**Detection Method**:
1. Keyword matching for each risk category
2. Sentence-level analysis
3. Confidence scoring
4. Overall risk assessment

**Technologies**: Keyword matching, NLP

---

### 5. Document Comparator (`backend/core/document_comparator.py`)

**Purpose**: Compare metrics across multiple documents

**Key Functions**:
- `compare_metrics()`: Compare metrics between 2 documents
- `calculate_percentage_change()`: Calculate % change
- `compare_multiple_documents()`: Compare 3+ documents
- `generate_comparison_table()`: Format results

**Output**: Comparison with absolute and percentage changes, trends

**Technologies**: NumPy, Statistical calculations

---

### 6. RAG Pipeline (`backend/core/rag_pipeline.py`)

**Purpose**: Enable question-answering over financial documents

**Components**:

#### a) EmbeddingGenerator
- Uses sentence-transformers (MiniLM-L6-v2)
- Converts text to vector embeddings
- Fast, lightweight model for real-time processing

#### b) SimpleVectorStore
- Custom FAISS-based storage (simplified implementation)
- Stores document chunks and embeddings
- Performs similarity search
- Persists to/from JSON

#### c) RAGPipeline
- Orchestrates the Q&A workflow:
  1. Generate query embedding
  2. Retrieve relevant context
  3. Generate prompt with context
  4. Call LLM (optional) or generate simple answer

**Technologies**: sentence-transformers, FAISS, OpenAI API (optional)

---

### 7. Analysis Service (`backend/services/analysis_service.py`)

**Purpose**: Orchestrate all analysis components

**Key Functions**:
- `analyze_document()`: Complete analysis pipeline
- `compare_documents()`: Compare multiple documents
- `answer_question()`: Q&A system
- `export_analysis()`: Export results

**Workflow**:
```
PDF File → Extract Text → Extract Metrics → Calculate Ratios
                        ↓
                   Detect Risks → Index for Q&A → Return Results
```

---

## Data Flow

### Document Upload & Analysis

```
1. User uploads PDF
   ↓
2. Document Processor extracts text and chunks
   ↓
3. Metric Extractor finds financial metrics
   ↓
4. Ratio Calculator computes ratios
   ↓
5. Risk Detector identifies risks
   ↓
6. RAG Pipeline indexes chunks for Q&A
   ↓
7. Analysis Service combines all results
   ↓
8. API returns complete analysis
```

### Question Answering

```
1. User asks question
   ↓
2. Embedding Generator converts query to vector
   ↓
3. Vector Store retrieves top-k similar chunks
   ↓
4. Context assembled with relevant documents
   ↓
5. LLM generates answer (optional) or fallback answer
   ↓
6. Result returned with source attribution
```

---

## API Layer (`backend/routes/analysis_routes.py`)

**Base URL**: `http://localhost:8000/api/v1`

**Endpoints**:
1. `POST /upload` - Upload and analyze document
2. `GET /documents` - List all documents
3. `GET /document/{doc_id}` - Get document summary
4. `POST /compare` - Compare documents
5. `POST /question` - Ask question
6. `GET /export/{doc_id}` - Export analysis
7. `GET /health` - Health check

---

## Frontend (`frontend/app.py`)

**Framework**: Streamlit

**Pages**:
1. **📁 Upload & Analyze**: Upload documents, view analysis
2. **📊 Dashboard**: View metrics, charts, and insights
3. **🔍 Compare Reports**: Compare multiple documents
4. **❓ Ask Questions**: Q&A interface
5. **⚙️ Settings**: Configuration options

**Features**:
- Real-time visualization with Plotly
- Interactive document selection
- Expandable analysis sections
- Risk level indicators
- Source attribution for Q&A

---

## Data Models (`backend/models/schemas.py`)

```python
FinancialMetrics
├── revenue
├── net_income
├── operating_income
├── ebitda
├── total_debt
├── cash_flow
├── total_assets
└── total_equity

FinancialRatios
├── profit_margin
├── operating_margin
├── debt_to_equity
├── asset_turnover
├── roa
└── roe

RiskReport
├── risk_categories
├── top_risks
├── overall_risk_level
└── risk_count

DocumentAnalysis
├── file_name
├── pages
├── chunks_count
├── metrics
├── ratios
├── risks
└── summary
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit, Plotly, Pandas | UI & Visualization |
| **Backend** | FastAPI, Python 3.8+ | REST API |
| **NLP** | Transformers, sentence-transformers | Embeddings & NLP |
| **Vector DB** | FAISS | Similarity Search |
| **PDF** | pdfplumber, PyPDF2 | Document Processing |
| **LLM** | OpenAI API (optional) | Advanced QA |
| **Data** | NumPy, Pandas | Calculations |

---

## Performance Characteristics

| Component | Time | Notes |
|-----------|------|-------|
| PDF Extraction | 1-5s | Depends on PDF size |
| Metric Extraction | <1s | Pattern matching |
| Ratio Calculation | <1s | Simple math |
| Risk Detection | 1-2s | Keyword analysis |
| Embedding Generation | 2-5s | First call slower (model load) |
| Vector Search | <100ms | Fast similarity lookup |
| Q&A Generation | 1-5s | LLM dependent |

---

## Scalability Considerations

### Current Limitations
- In-memory document storage
- Vector store in JSON (not production-grade)
- Single-threaded processing

### Scaling Strategies
1. **Database**: Move to PostgreSQL + pgvector
2. **Vector DB**: Use Pinecone, Weaviate, or Milvus
3. **Message Queue**: Add Celery for async processing
4. **Caching**: Redis for frequently accessed documents
5. **Horizontal Scaling**: Docker containerization, Kubernetes

---

## Security Considerations

1. **File Upload**: Validate file types and size limits
2. **API**: Add authentication (JWT, OAuth2)
3. **Data**: Encrypt sensitive documents
4. **Secrets**: Store API keys securely
5. **Rate Limiting**: Prevent abuse

---

## Future Enhancements

1. **Advanced LLM**: GPT-4, Llama 2 integration
2. **Multi-language**: Support non-English documents
3. **Custom Models**: Train on financial documents
4. **Real-time Updates**: Monitor documents over time
5. **Advanced Analytics**: Predictive modeling
6. **Export Formats**: PDF, Excel, PowerPoint reports
7. **Collaboration**: Multi-user workspace
8. **Audit Trail**: Track all analysis changes

---

## Deployment Architecture

```
┌────────────────────────────────────────────┐
│         Load Balancer (Nginx)              │
└────────────┬─────────────────────┬─────────┘
             │                     │
    ┌────────▼────────┐   ┌────────▼────────┐
    │  FastAPI App 1  │   │  FastAPI App 2  │
    └────────┬────────┘   └────────┬────────┘
             │                     │
             └────────────┬────────┘
                          │
            ┌─────────────┴──────────────┐
            │                            │
    ┌───────▼─────────┐       ┌──────────▼────────┐
    │  PostgreSQL     │       │  Redis Cache      │
    │  + pgvector     │       │  + Vector DB      │
    └─────────────────┘       └───────────────────┘
```

---

## Maintenance & Monitoring

- **Logging**: Structured logging for debugging
- **Metrics**: Track API response times and errors
- **Health Checks**: Regular API availability checks
- **Updates**: Keep ML models and dependencies updated

---

**Architecture designed for scalability, maintainability, and extensibility** ✨
