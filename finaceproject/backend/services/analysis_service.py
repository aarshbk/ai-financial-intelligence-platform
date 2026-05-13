"""
Analysis Service
Orchestrates all analysis components
"""
import os
import json
from typing import Dict, List, Optional, Tuple
import logging

from backend.core import (
    DocumentProcessor,
    FinancialMetricExtractor,
    FinancialRatioCalculator,
    RiskDetector,
    DocumentComparator,
    RAGPipeline,
)
from backend.models import (
    FinancialMetrics,
    FinancialRatios,
    RiskReport,
    DocumentAnalysis,
)

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service to orchestrate all analysis components"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor(chunk_size=500, overlap=50)
        self.metric_extractor = FinancialMetricExtractor()
        self.ratio_calculator = FinancialRatioCalculator()
        self.risk_detector = RiskDetector()
        self.comparator = DocumentComparator()
        self.rag_pipeline = RAGPipeline()
        
        self.uploaded_documents = {}  # Store document data in memory
        logger.info("AnalysisService initialized")
    
    def analyze_document(self, file_path: str) -> Dict:
        """
        Complete analysis of a financial document
        """
        try:
            # Step 1: Extract text from PDF
            logger.info(f"Processing document: {file_path}")
            chunks, metadata = self.doc_processor.process_document(file_path)
            
            # Join chunks for metric extraction and risk analysis
            full_text = " ".join(chunks)
            
            # Step 2: Extract financial metrics
            logger.info("Extracting financial metrics...")
            metrics_dict = self.metric_extractor.extract_all_metrics(full_text)
            
            # Step 3: Calculate financial ratios
            logger.info("Calculating financial ratios...")
            ratios_dict = self.ratio_calculator.calculate_all_ratios(metrics_dict)
            
            # Step 4: Detect risks
            logger.info("Analyzing financial risks...")
            risk_report = self.risk_detector.generate_risk_report(full_text)
            
            # Step 5: Index for RAG
            logger.info("Indexing document for Q&A...")
            self.rag_pipeline.index_documents(
                chunks,
                metadata=[{"chunk_index": i, "text_preview": chunk[:100]} 
                         for i, chunk in enumerate(chunks)]
            )
            
            # Store document data
            doc_id = metadata["file_name"]
            self.uploaded_documents[doc_id] = {
                "file_path": file_path,
                "metadata": metadata,
                "chunks": chunks,
                "full_text": full_text,
                "metrics": metrics_dict,
                "ratios": ratios_dict,
                "risk_report": risk_report
            }
            
            # Format response
            analysis = {
                "file_name": metadata["file_name"],
                "pages": metadata["pages"],
                "chunks_count": metadata["chunks_count"],
                "metrics": metrics_dict,
                "ratios": ratios_dict,
                "risk_report": risk_report,
                "summary": self._generate_summary(metrics_dict, ratios_dict, risk_report)
            }
            
            logger.info(f"Document analysis complete: {doc_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
    
    def compare_documents(self, doc1_id: str, doc2_id: str) -> Dict:
        """
        Compare metrics between two uploaded documents
        """
        if doc1_id not in self.uploaded_documents:
            raise ValueError(f"Document {doc1_id} not found")
        if doc2_id not in self.uploaded_documents:
            raise ValueError(f"Document {doc2_id} not found")
        
        doc1 = self.uploaded_documents[doc1_id]
        doc2 = self.uploaded_documents[doc2_id]
        
        comparison = self.comparator.compare_metrics(
            doc1["metrics"],
            doc2["metrics"],
            doc1_id,
            doc2_id
        )
        
        return comparison
    
    def answer_question(self, query: str, use_openai: bool = False) -> Dict:
        """
        Answer a question about uploaded documents using RAG
        """
        if not self.uploaded_documents:
            return {
                "query": query,
                "answer": "No documents have been uploaded yet. Please upload financial documents first.",
                "sources": [],
                "confidence": 0
            }
        
        response = self.rag_pipeline.answer_question(query, use_openai=use_openai)
        return response
    
    def get_document_summary(self, doc_id: str) -> Dict:
        """
        Get summary of an uploaded document
        """
        if doc_id not in self.uploaded_documents:
            raise ValueError(f"Document {doc_id} not found")
        
        doc = self.uploaded_documents[doc_id]
        return {
            "file_name": doc_id,
            "pages": doc["metadata"]["pages"],
            "chunks": doc["metadata"]["chunks_count"],
            "summary": doc.get("summary", ""),
            "metrics": doc["metrics"],
            "risk_level": doc["risk_report"]["overall_risk_level"]
        }
    
    def list_documents(self) -> List[str]:
        """List all uploaded documents"""
        return list(self.uploaded_documents.keys())
    
    def _generate_summary(self, metrics: Dict, ratios: Dict, risk_report: Dict) -> str:
        """Generate text summary of analysis"""
        summary_parts = []
        
        # Metrics summary
        if metrics.get("revenue"):
            summary_parts.append(f"Revenue: ${metrics['revenue']} ")
        if metrics.get("net_income"):
            summary_parts.append(f"Net Income: ${metrics['net_income']} ")
        
        # Ratios summary
        if ratios.get("profit_margin"):
            summary_parts.append(f"Profit Margin: {ratios['profit_margin']:.2f}% ")
        
        # Risk summary
        summary_parts.append(f"Overall Risk Level: {risk_report['overall_risk_level']}")
        
        return " | ".join(summary_parts)
    
    def export_analysis(self, doc_id: str, format: str = "json") -> str:
        """
        Export analysis results
        
        Args:
            doc_id: Document ID
            format: Export format ('json', 'csv', 'pdf')
        """
        if doc_id not in self.uploaded_documents:
            raise ValueError(f"Document {doc_id} not found")
        
        doc = self.uploaded_documents[doc_id]
        
        if format == "json":
            return json.dumps({
                "file_name": doc_id,
                "metrics": doc["metrics"],
                "ratios": doc["ratios"],
                "risk_report": doc["risk_report"],
                "summary": doc.get("summary", "")
            }, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
