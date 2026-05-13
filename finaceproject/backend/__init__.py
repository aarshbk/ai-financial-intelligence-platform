"""Backend module initialization"""
from .main import app
from .services import AnalysisService
from .core import (
    DocumentProcessor,
    FinancialMetricExtractor,
    FinancialRatioCalculator,
    RiskDetector,
)

__all__ = [
    "app",
    "AnalysisService",
    "DocumentProcessor",
    "FinancialMetricExtractor",
    "FinancialRatioCalculator",
    "RiskDetector",
]
