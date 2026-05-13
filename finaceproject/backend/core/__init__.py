"""Core module initialization"""
from .document_processor import DocumentProcessor
from .metric_extraction import FinancialMetricExtractor
from .ratio_calculator import FinancialRatioCalculator
from .risk_detector import RiskDetector, RiskCategory
from .document_comparator import DocumentComparator
from .rag_pipeline import RAGPipeline, EmbeddingGenerator, SimpleVectorStore

__all__ = [
    "DocumentProcessor",
    "FinancialMetricExtractor",
    "FinancialRatioCalculator",
    "RiskDetector",
    "RiskCategory",
    "DocumentComparator",
    "RAGPipeline",
    "EmbeddingGenerator",
    "SimpleVectorStore",
]
