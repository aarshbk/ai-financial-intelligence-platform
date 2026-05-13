# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Install Dependencies (2 min)
```bash
cd c:\Users\aarsh\finaceproject
pip install -r requirements.txt
```

**Note**: First installation may take a few minutes as it downloads ML models.

### Step 2: Start Backend (1 min)
```bash
python -m uvicorn backend.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ API is ready at: http://localhost:8000/docs

### Step 3: Start Frontend (1 min)
Open a new terminal in the project directory:
```bash
streamlit run frontend/app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

✅ Dashboard is ready at: http://localhost:8501

### Step 4: Upload & Analyze (1 min)
1. Go to http://localhost:8501
2. Select "📁 Upload & Analyze"
3. Upload a PDF financial document
4. View extracted metrics, ratios, and risks

---

## 📊 Using the Dashboard

### 1. Upload & Analyze
- Upload any PDF (annual reports, earnings statements, etc.)
- Get instant:
  - Financial metrics (Revenue, Net Income, Debt, etc.)
  - Financial ratios (Profit Margin, ROE, Debt-to-Equity, etc.)
  - Risk assessment with categories

### 2. Financial Dashboard
- Select a document
- View key metrics
- See visualizations
- Check risk levels

### 3. Compare Reports
- Upload 2+ documents
- Compare metrics side-by-side
- See percentage changes and trends

### 4. Ask Questions
- Query documents in natural language
- Examples:
  - "What are the biggest risks?"
  - "How did revenue change?"
  - "What's the company's debt situation?"

---

## 🔌 API Usage

### Example: Upload & Analyze via API
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@annual_report.pdf"
```

### Example: Ask a Question
```bash
curl -X POST "http://localhost:8000/api/v1/question" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main risks?",
    "use_openai": false
  }'
```

See [README.md](README.md) for complete API documentation.

---

## 🐛 Troubleshooting

### "Port 8000 already in use"
```bash
# Use different port
python -m uvicorn backend.main:app --reload --port 8001
```

### "Module not found" errors
```bash
# Ensure you're in the correct directory and virtual env
pip install -r requirements.txt
```

### Streamlit not connecting to API
```bash
# Make sure backend is running (check http://localhost:8000)
# Edit API_BASE_URL in frontend/app.py if needed
```

---

## 📝 Sample Data for Testing

Generate sample financial data:
```bash
python sample_data_generator.py
```

This creates `sample_financial_data.txt` with realistic financial information.

---

## 🎯 Next Steps

1. **Upload Your Documents**: Use real financial reports for analysis
2. **Explore Features**: Try all dashboard pages and Q&A system
3. **Customize**: Modify metrics patterns in `backend/core/metric_extraction.py`
4. **Integrate**: Connect to your own systems via API
5. **Deploy**: See deployment guide for production setup

---

## 📚 Documentation

- [Full README](README.md) - Complete documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Architecture](README.md#architecture) - System design details

---

## 💡 Tips

- **Large PDFs**: Works best with 10-50 page documents
- **Quality**: OCR-scanned PDFs may need manual verification
- **Accuracy**: Results improve with standard financial document formats
- **Performance**: First document analysis takes longer (model loading)

---

## 🆘 Need Help?

1. Check the [README.md](README.md)
2. Review [API Docs](http://localhost:8000/redoc)
3. Check console output for error messages
4. Verify all dependencies are installed

---

**Enjoy analyzing financial documents! 📊**
