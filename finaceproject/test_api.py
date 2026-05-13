"""
Demo Script - Testing the AI Financial Intelligence Platform
"""
import requests
import json
import time


BASE_URL = "http://localhost:8000/api/v1"


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_health():
    """Test health endpoint"""
    print_header("Testing API Health")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_upload(pdf_path):
    """Test document upload"""
    print_header("Testing Document Upload")
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Message: {data['message']}")
        
        if "analysis" in data:
            analysis = data["analysis"]
            print(f"\n📊 Financial Metrics Extracted:")
            print(json.dumps(analysis["metrics"], indent=2))
            
            print(f"\n📈 Financial Ratios Calculated:")
            for ratio, value in analysis["ratios"].items():
                if value:
                    print(f"  {ratio}: {value:.2f}")
            
            print(f"\n⚠️ Risk Assessment:")
            risk = analysis["risk_report"]
            print(f"  Overall Risk Level: {risk['overall_risk_level']}")
            print(f"  Risk Categories Found: {len(risk['risk_categories'])}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_list_documents():
    """Test listing documents"""
    print_header("Testing List Documents")
    try:
        response = requests.get(f"{BASE_URL}/documents")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Documents: {json.dumps(data['documents'], indent=2)}")
        return response.status_code == 200, data.get("documents", [])
    except Exception as e:
        print(f"Error: {e}")
        return False, []


def test_get_document_summary(doc_id):
    """Test getting document summary"""
    print_header("Testing Get Document Summary")
    try:
        response = requests.get(f"{BASE_URL}/document/{doc_id}")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Summary: {json.dumps(data['data'], indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_compare_documents(doc1, doc2):
    """Test comparing documents"""
    print_header("Testing Document Comparison")
    try:
        response = requests.post(
            f"{BASE_URL}/compare",
            params={"doc1_id": doc1, "doc2_id": doc2}
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if "comparison" in data:
            comparison = data["comparison"]
            print(f"Comparing: {comparison['doc1']} vs {comparison['doc2']}")
            print(f"\nMetric Comparisons:")
            for metric, values in list(comparison["metrics"].items())[:5]:
                print(f"\n  {metric}:")
                print(f"    {comparison['doc1']}: {values.get(doc1)}")
                print(f"    {comparison['doc2']}: {values.get(doc2)}")
                print(f"    Change: {values.get('percentage_change', 'N/A')}%")
                print(f"    Trend: {values.get('trend', 'N/A')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_ask_question(query, use_openai=False):
    """Test Q&A endpoint"""
    print_header(f"Testing Financial Q&A")
    print(f"Query: {query}")
    try:
        payload = {"query": query, "use_openai": use_openai}
        response = requests.post(f"{BASE_URL}/question", json=payload)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if "data" in data:
            qa = data["data"]
            print(f"\n📝 Answer:")
            print(qa["answer"][:500])
            print(f"\n🎯 Confidence: {qa['confidence']:.2f}")
            
            if qa["sources"]:
                print(f"\n📚 Sources ({len(qa['sources'])}):")
                for i, source in enumerate(qa["sources"][:2]):
                    print(f"\n  Source {i+1} (Score: {source['score']:.2f}):")
                    print(f"  {source['text'][:100]}...")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_export(doc_id):
    """Test export endpoint"""
    print_header("Testing Export Analysis")
    try:
        response = requests.get(f"{BASE_URL}/export/{doc_id}?format=json")
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if "data" in data:
            export_data = json.loads(data["data"])
            print(f"Export Format: {data['format']}")
            print(f"Exported Data (first 500 chars):")
            print(json.dumps(export_data, indent=2)[:500])
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("🚀 AI Financial Intelligence Platform - Demo & Testing")
    print("="*80)
    
    # Test 1: Health check
    print("\n[1/5] Checking API Health...")
    if not test_health():
        print("\n❌ API is not running. Start it with:")
        print("   python -m uvicorn backend.main:app --reload")
        return
    
    print("\n✅ API is running!")
    
    # Test 2: Sample document upload
    print("\n[2/5] Uploading Sample Document...")
    print("Note: You need to provide a real PDF file for this test.")
    print("For testing without a PDF, the endpoints are ready to process documents.")
    
    # Test 3: List documents
    print("\n[3/5] Listing Documents...")
    success, documents = test_list_documents()
    
    if success and documents:
        doc_id = documents[0]
        
        # Test 4: Get document summary
        print("\n[4/5] Getting Document Summary...")
        test_get_document_summary(doc_id)
        
        # Test 5: Ask questions
        print("\n[5/5] Testing Q&A System...")
        sample_queries = [
            "What are the main financial metrics?",
            "What risks are mentioned in this report?",
            "How is the company's financial health?"
        ]
        
        for query in sample_queries[:1]:  # Test one query
            test_ask_question(query, use_openai=False)
    else:
        print("\n⚠️ No documents uploaded yet. Upload documents through the Streamlit UI or API.")
    
    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("\nTo use the full system:")
    print("1. Start backend: python -m uvicorn backend.main:app --reload")
    print("2. Start frontend: streamlit run frontend/app.py")
    print("3. Open http://localhost:8501 in your browser")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
