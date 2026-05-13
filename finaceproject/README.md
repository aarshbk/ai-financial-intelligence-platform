# AI Financial Intelligence Platform

## Overview

A comprehensive full-stack AI system that analyzes financial documents and extracts actionable insights. Acts like a mini AI financial analyst capable of processing annual reports, earnings calls, financial statements, and more.

## Features

### 1. **Document Upload System**
- Upload PDF financial reports
- Automatic text extraction using `pdfplumber`
- Text cleaning and preprocessing
- Chunking for efficient processing

### 2. **Financial Metric Extraction**
Automatically detects and extracts:
- Revenue
- Net Income
- Operating Income
- EBITDA
- Total Debt
- Cash Flow
- Total Assets
- Total Equity

Uses NLP pattern matching and context analysis for accurate extraction.

### 3. **Financial Ratio Analysis**
Calculates key indicators:
- Profit Margin
- Operating Margin
- Debt-to-Equity Ratio
- Asset Turnover
- Return on Assets (ROA)
- Return on Equity (ROE)

### 4. **Risk Detection System**
Identifies and classifies risks:
- Regulatory Risk
- Liquidity Risk
- Market Risk
- Operational Risk
- Supply Chain Risk
- Credit Risk
- Legal Risk

### 5. **Multi-Document Comparison**
Compare metrics across reports:
- Side-by-side metric comparison
- Percentage change calculations
- Trend analysis
- Year-over-year comparisons

### 6. **Financial Q&A (RAG Pipeline)**
Ask questions about documents:
- Retrieval Augmented Generation using embeddings
- FAISS-based vector storage
- LLM integration (OpenAI optional)
- Context-aware responses

### 7. **Financial Dashboard**
Interactive visualizations:
- Real-time metric display
- Charts and graphs
- Risk indicators
- Document comparison tables

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+

### AI/NLP
- **Embeddings**: sentence-transformers
- **Vector DB**: FAISS
- **LLM**: OpenAI (optional)
- **NLP**: Transformers, pattern matching

### Document Processing
- **PDF**: pdfplumber, PyPDF2

### Frontend
- **UI**: Streamlit
- **Visualization**: Plotly, Pandas

## Installation

### Prerequisites
- Python 3.8 or higher
- pip or conda

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Environment Setup
Create a `.env` file in the project root:
```env
API_HOST=0.0.0.0
API_PORT=8000
EMBEDDING_MODEL=all-MiniLM-L6-v2
OPENAI_API_KEY=your_key_here  # Optional
```

### Step 3: Create Sample Data (Optional)
```bash
python sample_data_generator.py
```

## Usage

### Start Backend
```bash
python -m uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Start Frontend
In a new terminal:
```bash
streamlit run frontend/app.py
```

The dashboard will be available at `http://localhost:8501`

## API Endpoints

### Core Analysis Endpoints

#### Upload Document
```
POST /api/v1/upload
Content-Type: multipart/form-data
Body: file (PDF)
```
**Response**: Complete analysis including metrics, ratios, and risks

#### List Documents
```
GET /api/v1/documents
```
**Response**: List of uploaded documents

#### Get Document Summary
```
GET /api/v1/document/{doc_id}
```
**Response**: Summary of document with key metrics and risk level

#### Compare Documents
```
POST /api/v1/compare?doc1_id=doc1&doc2_id=doc2
```
**Response**: Detailed comparison with percentage changes and trends

#### Ask Question
```
POST /api/v1/question
Body: {
  "query": "What are the main risks?",
  "use_openai": false
}
```
**Response**: Answer with source documents and confidence score

#### Export Analysis
```
GET /api/v1/export/{doc_id}?format=json
```
**Response**: Complete analysis in requested format

#### Health Check
```
GET /api/v1/health
```
**Response**: API status

## Project Structure

```
finaceproject/
├── backend/
│   ├── core/                    # Core analysis modules
│   │   ├── document_processor.py
│   │   ├── metric_extraction.py
│   │   ├── ratio_calculator.py
│   │   ├── risk_detector.py
│   │   ├── document_comparator.py
│   │   └── rag_pipeline.py
│   ├── models/                  # Pydantic models
│   │   └── schemas.py
│   ├── services/                # Business logic
│   │   └── analysis_service.py
│   ├── routes/                  # API routes
│   │   └── analysis_routes.py
│   ├── main.py                  # FastAPI app
│   └── __init__.py
├── frontend/
│   └── app.py                   # Streamlit dashboard
├── data/                        # Data storage
├── uploads/                     # Uploaded PDFs
├── config.py                    # Configuration
├── .env                         # Environment variables
├── requirements.txt             # Dependencies
├── README.md                    # This file
└── sample_data_generator.py     # Test data
```

## Usage Examples

### Example 1: Upload and Analyze a Report
```python
# Using API directly
import requests

with open("annual_report.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/v1/upload",
        files=files
    )
    analysis = response.json()
    print(analysis["analysis"]["metrics"])
```

### Example 2: Compare Two Reports
```python
response = requests.post(
    "http://localhost:8000/api/v1/compare",
    params={
        "doc1_id": "2023_report.pdf",
        "doc2_id": "2024_report.pdf"
    }
)
comparison = response.json()
```

### Example 3: Ask Financial Questions
```python
response = requests.post(
    "http://localhost:8000/api/v1/question",
    json={
        "query": "What are the biggest risks facing the company?",
        "use_openai": False
    }
)
qa_result = response.json()
print(qa_result["data"]["answer"])
```

## Features in Detail

### Financial Metric Extraction

The system uses regex patterns and NLP techniques to identify:
- Financial metrics in various formats ($M, $B, thousands, millions)
- Context-aware extraction
- Fallback to pattern matching if initial extraction fails

### Risk Detection

Analyzes documents for:
- Keywords related to different risk categories
- Sentence-level risk analysis
- Confidence scoring for each risk
- Overall risk assessment

### RAG Pipeline

The question-answering system:
1. Generates embeddings for document chunks
2. Stores in FAISS vector database
3. Retrieves relevant context for queries
4. Generates context-aware answers
5. Provides source attribution

## Configuration

Edit `.env` file to customize:
- API host and port
- Embedding model
- PDF chunk size
- Vector store location
- OpenAI API key (for advanced LLM features)

## Performance Considerations

- Documents are chunked into 500-word segments with 50-word overlap
- Embeddings generated using lightweight model (MiniLM-L6)
- Vector search optimized with FAISS
- Streaming responses for large documents

## Limitations & Future Enhancements

### Current Limitations
- PDF text extraction quality depends on PDF format
- LLM features require OpenAI API key
- Vector database stored in-memory (not persistent by default)

### Future Enhancements
- PostgreSQL backend for persistent storage
- Advanced LLM models (GPT-4, Llama)
- Real-time document monitoring
- Export to multiple formats (Excel, PDF reports)
- Machine learning model training for custom metrics
- Multi-language support
- Integration with financial databases
- Advanced visualization dashboards

## Troubleshooting

### Backend not starting
```bash
# Check if port 8000 is available
# Try different port: uvicorn backend.main:app --port 8001
```

### Embedding model not downloading
```bash
# Manually download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### PDF extraction failing
- Ensure PDF is not corrupted
- Check file permissions
- Try with different PDF

## Contributing

Feel free to extend the system with:
- New metric extraction patterns
- Additional risk categories
- Custom LLM integrations
- New visualization types

## License

This project is open source and available for educational and commercial use.

## Support

For issues, questions, or suggestions, please refer to the documentation or create an issue in the repository.

---

**Built with ❤️ using FastAPI, Streamlit, and Transformers**
