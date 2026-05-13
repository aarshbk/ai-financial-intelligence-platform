"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class FinancialMetrics(BaseModel):
    """Financial metrics extracted from document"""
    revenue: Optional[str] = None
    net_income: Optional[str] = None
    operating_income: Optional[str] = None
    ebitda: Optional[str] = None
    total_debt: Optional[str] = None
    cash_flow: Optional[str] = None
    total_assets: Optional[str] = None
    total_equity: Optional[str] = None


class FinancialRatios(BaseModel):
    """Calculated financial ratios"""
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    asset_turnover: Optional[float] = None
    roa: Optional[float] = None
    roe: Optional[float] = None


class RiskItem(BaseModel):
    """Single risk item"""
    category: str
    text: str
    confidence: float


class RiskReport(BaseModel):
    """Financial risk report"""
    risk_categories: Dict[str, float]
    top_risks: List[RiskItem]
    overall_risk_level: str
    risk_count: int


class DocumentAnalysis(BaseModel):
    """Complete analysis of a single document"""
    file_name: str
    pages: int
    chunks_count: int
    metrics: FinancialMetrics
    ratios: FinancialRatios
    risks: RiskReport


class ComparisonMetric(BaseModel):
    """Single metric comparison"""
    metric_name: str
    doc1_value: Optional[float] = None
    doc2_value: Optional[float] = None
    absolute_change: Optional[float] = None
    percentage_change: Optional[float] = None
    trend: str


class ComparisonResult(BaseModel):
    """Comparison between two documents"""
    doc1_name: str
    doc2_name: str
    metrics: List[ComparisonMetric]


class QAQuery(BaseModel):
    """Question for QA system"""
    query: str = Field(..., min_length=1, max_length=500)
    use_openai: Optional[bool] = False


class QAResponse(BaseModel):
    """Response from QA system"""
    query: str
    answer: str
    sources: List[Dict]
    confidence: float


class UploadResponse(BaseModel):
    """Response after document upload"""
    file_name: str
    status: str
    message: str
    analysis: Optional[DocumentAnalysis] = None
