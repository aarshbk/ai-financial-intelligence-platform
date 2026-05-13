# AI Financial Intelligence Platform 🎯

An AI-powered system that analyzes financial documents and extracts insights like a financial analyst.

## Features ✨

- 📄 **Document Upload** - Support for PDF financial reports
- 💰 **Financial Metrics Extraction** - Revenue, Net Income, EBITDA, Debt, etc.
- 📊 **Financial Ratio Analysis** - Profit Margin, ROE, Debt-to-Equity ratios
- ⚠️ **Risk Detection** - Identify regulatory, liquidity, market, and operational risks
- 🔄 **Multi-Document Comparison** - Compare metrics across reports
- 🤖 **RAG Q&A System** - Ask questions about uploaded documents
- 💳 **Payment Processing** - Accept Google Pay, PayPal, Credit Cards, Apple Pay
- 📈 **Interactive Dashboard** - Beautiful visualizations with Plotly

## Tech Stack 🛠️

**Backend:**
- FastAPI
- Python
- SQLAlchemy
- Stripe (Payments)

**Frontend:**
- Streamlit
- Plotly

**AI/NLP:**
- HuggingFace Transformers
- FAISS (Vector Database)
- pdfplumber (PDF processing)

## Quick Start 🚀

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-financial-intelligence-platform.git
cd ai-financial-intelligence-platform

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Stripe keys
```

### Running

**Terminal 1 - Backend:**
```bash
python -m uvicorn backend.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/app.py
```

Open: http://localhost:8501

## Usage 📖

1. **Upload PDF** - Go to "Upload & Analyze" page
2. **View Metrics** - See extracted financial data
3. **Analyze Risks** - Check detected risk categories
4. **Compare Reports** - Upload multiple documents to compare
5. **Ask Questions** - Use Q&A to query documents
6. **Make Payment** - Subscribe to premium features

## API Endpoints 🔌

- `POST /api/v1/upload` - Upload and analyze document
- `GET /api/v1/metrics/{doc_id}` - Get extracted metrics
- `GET /api/v1/risks/{doc_id}` - Get risk analysis
- `POST /api/v1/question` - Ask questions about documents
- `POST /api/v1/subscribe` - Create subscription

See [API Docs](http://localhost:8000/docs) for complete reference.

## Monetization 💰

- 💳 **Freemium SaaS** - Free + Premium tiers
- 📡 **API Access** - Developer and Business plans
- 📢 **Sponsored Content** - Partner advertisements
- 🤝 **Affiliate Marketing** - Earn commissions
- 🏢 **White-Label** - Resell to enterprises

## Architecture 🏗️

```
User → Streamlit UI → FastAPI Backend → Analysis Pipeline → Vector DB
                            ↓
                      Document Processing
                      Metric Extraction
                      Risk Detection
                      RAG Q&A
                      Payment Processing
```

## File Structure 📁

```
ai-financial-intelligence-platform/
├── backend/
│   ├── core/
│   │   ├── document_processor.py
│   │   ├── metric_extraction.py
│   │   ├── ratio_calculation.py
│   │   ├── risk_detection.py
│   │   ├── rag_pipeline.py
│   │   └── comparison_engine.py
│   ├── routes/
│   │   ├── documents.py
│   │   ├── analysis.py
│   │   ├── payments.py
│   │   └── auth.py
│   ├── models/
│   │   └── schemas.py
│   └── main.py
├── frontend/
│   ├── app.py
│   ├── pages/
│   │   ├── 1_📁_Upload_Analyze.py
│   │   ├── 2_📊_Dashboard.py
│   │   ├── 3_🔄_Compare.py
│   │   ├── 4_❓_Q&A.py
│   │   └── 5_💳_Pricing.py
│   └── components/
│       ├── metrics.py
│       ├── charts.py
│       └── payments.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## License 📜

MIT License - See LICENSE file for details

## Contributing 🤝

1. Fork the repository
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support 💬

- Check [QUICKSTART.md](QUICKSTART.md) for setup help
- Review [API Docs](http://localhost:8000/docs)
- Create an issue on GitHub

## Roadmap 🗺️

- [ ] SEC EDGAR integration
- [ ] Real-time company monitoring
- [ ] Sentiment analysis
- [ ] Peer comparison
- [ ] Mobile app
- [ ] Multi-language support

---

**Built with ❤️ using Python, FastAPI, and Streamlit**
