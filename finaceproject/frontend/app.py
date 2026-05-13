"""
Streamlit Frontend Dashboard
AI Financial Intelligence Platform
"""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import os

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page config
st.set_page_config(
    page_title="Financial Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .risk-high { color: #d32f2f; }
    .risk-medium { color: #f57c00; }
    .risk-low { color: #388e3c; }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []
if "current_doc" not in st.session_state:
    st.session_state.current_doc = None


def check_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except:
        return False


def upload_document(file):
    """Upload and analyze a document"""
    if file is None:
        st.error("Please select a file")
        return
    
    files = {"file": (file.name, file)}
    try:
        with st.spinner("Analyzing document..."):
            response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.current_doc = file.name
            st.session_state.uploaded_docs.append(file.name)
            return data
        else:
            st.error(f"Upload failed: {response.json()}")
            return None
    except Exception as e:
        st.error(f"Error uploading document: {e}")
        return None


def get_document_summary(doc_id):
    """Fetch document summary from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/document/{doc_id}")
        if response.status_code == 200:
            return response.json()["data"]
        else:
            st.error(f"Error fetching document: {response.json()}")
            return None
    except Exception as e:
        st.error(f"Error fetching document: {e}")
        return None


def get_documents_list():
    """Fetch list of uploaded documents"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            return response.json()["documents"]
        else:
            return []
    except:
        return []


def compare_documents(doc1, doc2):
    """Compare two documents"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/compare",
            params={"doc1_id": doc1, "doc2_id": doc2}
        )
        if response.status_code == 200:
            return response.json()["comparison"]
        else:
            st.error(f"Comparison failed: {response.json()}")
            return None
    except Exception as e:
        st.error(f"Error comparing documents: {e}")
        return None


def ask_question(query, use_openai=False):
    """Ask question to QA system"""
    try:
        payload = {"query": query, "use_openai": use_openai}
        response = requests.post(
            f"{API_BASE_URL}/question",
            json=payload
        )
        if response.status_code == 200:
            return response.json()["data"]
        else:
            st.error(f"Question failed: {response.json()}")
            return None
    except Exception as e:
        st.error(f"Error asking question: {e}")
        return None


# Main app
def main():
    st.title("📊 AI Financial Intelligence Platform")
    st.markdown("*Analyze financial documents and extract actionable insights*")
    
    # Check API health
    if not check_api_health():
        st.error("⚠️ Backend API is not running. Please start the backend with: `python -m uvicorn backend.main:app --reload`")
        return
    
    st.success("✅ Backend API is connected")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["📁 Upload & Analyze", "📊 Dashboard", "🔍 Compare Reports", "❓ Ask Questions", "⚙️ Settings"]
        )
    
    # Page: Upload & Analyze
    if page == "📁 Upload & Analyze":
        st.header("Upload Financial Documents")
        st.markdown("Upload PDF files (annual reports, earnings calls, financial statements)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            if uploaded_file and st.button("Analyze Document", key="analyze"):
                result = upload_document(uploaded_file)
                if result:
                    st.success("✅ Document analyzed successfully!")
                    
                    # Display analysis
                    analysis = result.get("analysis", {})
                    
                    with st.expander("📈 Financial Metrics", expanded=True):
                        metrics = analysis.get("metrics", {})
                        cols = st.columns(4)
                        metric_items = list(metrics.items())
                        for i, (name, value) in enumerate(metric_items):
                            with cols[i % 4]:
                                st.metric(name.replace("_", " ").title(), value or "N/A")
                    
                    with st.expander("📊 Financial Ratios"):
                        ratios = analysis.get("ratios", {})
                        ratio_data = {}
                        for name, value in ratios.items():
                            if value:
                                ratio_data[name.replace("_", " ").title()] = f"{value:.2f}"
                        if ratio_data:
                            df = pd.DataFrame(ratio_data.items(), columns=["Ratio", "Value"])
                            st.dataframe(df, use_container_width=True)
                    
                    with st.expander("⚠️ Risk Assessment"):
                        risk = analysis.get("risk_report", {})
                        risk_level = risk.get("overall_risk_level", "N/A")
                        
                        level_color = {
                            "HIGH": "🔴",
                            "MEDIUM": "🟡",
                            "LOW": "🟢"
                        }
                        st.markdown(f"### {level_color.get(risk_level, '⚪')} {risk_level} RISK")
                        
                        st.write("**Risk Categories:**")
                        risk_cats = risk.get("risk_categories", {})
                        for cat, score in risk_cats.items():
                            st.write(f"- {cat}: {score:.2f}")
                        
                        st.write("**Top Risks:**")
                        for risk_item in risk.get("top_risks", [])[:5]:
                            st.write(f"- {risk_item['text'][:100]}... (confidence: {risk_item['confidence']:.2f})")
        
        with col2:
            st.subheader("Recent Documents")
            docs = get_documents_list()
            if docs:
                for doc in docs:
                    if st.button(f"📄 {doc}", key=f"select_{doc}"):
                        st.session_state.current_doc = doc
                        st.rerun()
            else:
                st.info("No documents uploaded yet")
    
    # Page: Dashboard
    elif page == "📊 Dashboard":
        st.header("Financial Dashboard")
        
        docs = get_documents_list()
        if not docs:
            st.warning("No documents uploaded. Please upload documents first.")
            return
        
        selected_doc = st.selectbox("Select Document", docs)
        
        if selected_doc:
            summary = get_document_summary(selected_doc)
            if summary:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Pages", summary["pages"])
                with col2:
                    st.metric("Chunks", summary["chunks"])
                with col3:
                    st.metric(
                        "Risk Level",
                        summary["risk_level"],
                        delta=None,
                        delta_color="off"
                    )
                with col4:
                    st.info(f"Uploaded: {selected_doc}")
                
                # Chart: Metrics over time (mock)
                st.subheader("Key Financial Metrics")
                metrics = summary.get("metrics", {})
                
                # Create sample chart
                metric_names = []
                metric_values = []
                for name, value in metrics.items():
                    if value:
                        try:
                            metric_names.append(name.replace("_", " ").title())
                            metric_values.append(float(value))
                        except:
                            pass
                
                if metric_names:
                    fig = px.bar(
                        x=metric_names[:6],
                        y=metric_values[:6],
                        title="Financial Metrics",
                        labels={"x": "Metric", "y": "Value"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # Page: Compare Reports
    elif page == "🔍 Compare Reports":
        st.header("Compare Financial Reports")
        
        docs = get_documents_list()
        if len(docs) < 2:
            st.warning("Need at least 2 documents to compare")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            doc1 = st.selectbox("Select First Document", docs, key="compare_doc1")
        with col2:
            doc2 = st.selectbox("Select Second Document", docs, key="compare_doc2", index=min(1, len(docs)-1))
        
        if doc1 and doc2 and doc1 != doc2:
            if st.button("Compare"):
                comparison = compare_documents(doc1, doc2)
                if comparison:
                    st.subheader("Comparison Results")
                    
                    # Create comparison table
                    comparison_data = []
                    metrics = comparison.get("metrics", {})
                    for metric, data in metrics.items():
                        comparison_data.append({
                            "Metric": metric.replace("_", " ").title(),
                            doc1: data.get(doc1, "N/A"),
                            doc2: data.get(doc2, "N/A"),
                            "Change %": f"{data.get('percentage_change', 0):.2f}%" if data.get('percentage_change') else "N/A",
                            "Trend": data.get("trend", "N/A")
                        })
                    
                    if comparison_data:
                        df = pd.DataFrame(comparison_data)
                        st.dataframe(df, use_container_width=True)
    
    # Page: Ask Questions
    elif page == "❓ Ask Questions":
        st.header("Financial Q&A System")
        
        docs = get_documents_list()
        if not docs:
            st.warning("No documents uploaded. Please upload documents first.")
            return
        
        st.write(f"💾 {len(docs)} document(s) available for Q&A")
        
        use_openai = st.checkbox("Use OpenAI (requires API key)", value=False)
        
        query = st.text_input("Ask a question about your financial documents:")
        
        if st.button("Get Answer"):
            if query:
                response = ask_question(query, use_openai=use_openai)
                if response:
                    st.subheader("Answer")
                    st.write(response["answer"])
                    
                    st.subheader(f"Confidence: {response['confidence']:.2f}")
                    
                    if response["sources"]:
                        st.subheader("Source Documents")
                        for i, source in enumerate(response["sources"][:3]):
                            with st.expander(f"Source {i+1} (Score: {source['score']:.2f})"):
                                st.write(source["text"])
            else:
                st.warning("Please enter a question")
    
    # Page: Settings
    elif page == "⚙️ Settings":
        st.header("Settings")
        
        st.subheader("Backend Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            api_url = st.text_input("API Base URL", value=API_BASE_URL)
            if api_url != API_BASE_URL:
                st.info("API URL would be updated (requires restart)")
        
        with col2:
            st.info("✅ Backend connected at: " + API_BASE_URL)
        
        st.subheader("Document Information")
        docs = get_documents_list()
        if docs:
            st.write(f"Total documents: {len(docs)}")
            for doc in docs:
                st.write(f"- {doc}")


if __name__ == "__main__":
    main()
