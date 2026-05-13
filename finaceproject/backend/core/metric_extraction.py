"""
Financial Metric Extraction Module
Extracts key financial metrics from documents using NLP and LLM prompts
"""
import re
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FinancialMetricExtractor:
    """Extract financial metrics from text using pattern matching and NLP"""
    
    def __init__(self):
        # Define patterns for common financial metrics
        self.patterns = {
            "revenue": [
                r"(?:total\s+)?revenue[:\s]+\$?([\d,\.]+)\s*(?:billion|million|thousand|B|M|K)?",
                r"(?:net\s+)?sales[:\s]+\$?([\d,\.]+)\s*(?:billion|million|thousand|B|M|K)?",
                r"(?:operating|service)\s+revenue[:\s]+\$?([\d,\.]+)",
            ],
            "net_income": [
                r"(?:net\s+)?income[:\s]+\$?([\d,\.]+)\s*(?:billion|million|thousand|B|M|K)?",
                r"(?:net\s+)?earnings[:\s]+\$?([\d,\.]+)",
                r"(?:net\s+)?profit[:\s]+\$?([\d,\.]+)",
            ],
            "operating_income": [
                r"operating\s+income[:\s]+\$?([\d,\.]+)",
                r"operating\s+profit[:\s]+\$?([\d,\.]+)",
                r"EBIT[:\s]+\$?([\d,\.]+)",
            ],
            "ebitda": [
                r"EBITDA[:\s]+\$?([\d,\.]+)\s*(?:billion|million|thousand|B|M|K)?",
                r"(?:adjusted\s+)?EBITDA[:\s]+\$?([\d,\.]+)",
            ],
            "total_debt": [
                r"(?:total\s+)?debt[:\s]+\$?([\d,\.]+)\s*(?:billion|million|thousand|B|M|K)?",
                r"(?:long-term|short-term)\s+debt[:\s]+\$?([\d,\.]+)",
            ],
            "cash_flow": [
                r"(?:operating\s+)?cash\s+flow[:\s]+\$?([\d,\.]+)",
                r"free\s+cash\s+flow[:\s]+\$?([\d,\.]+)\s*(?:billion|million|thousand|B|M|K)?",
            ],
            "total_assets": [
                r"(?:total\s+)?assets[:\s]+\$?([\d,\.]+)\s*(?:billion|million|thousand|B|M|K)?",
            ],
            "total_equity": [
                r"(?:total\s+)?(?:shareholders?|stockholders?)\s+equity[:\s]+\$?([\d,\.]+)",
                r"stockholders?\s+equity[:\s]+\$?([\d,\.]+)",
            ],
        }
    
    def extract_metric_value(self, text: str, metric: str) -> Optional[str]:
        """
        Extract a specific financial metric from text using regex patterns
        """
        text_lower = text.lower()
        patterns = self.patterns.get(metric, [])
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    value = match.group(1)
                    return self.normalize_value(value)
                except:
                    continue
        
        return None
    
    def normalize_value(self, value_str: str) -> str:
        """
        Normalize numeric values (remove commas, etc.)
        """
        # Remove commas
        value_str = value_str.replace(',', '')
        # Convert to float for validation
        try:
            float(value_str)
            return value_str
        except:
            return None
    
    def extract_all_metrics(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract all available financial metrics from text
        """
        metrics = {}
        for metric_name in self.patterns.keys():
            value = self.extract_metric_value(text, metric_name)
            metrics[metric_name] = value
        
        return metrics
    
    def extract_with_context(self, chunks: List[str]) -> Dict[str, Dict]:
        """
        Extract metrics from document chunks with context
        """
        all_metrics = {}
        
        for i, chunk in enumerate(chunks):
            metrics = self.extract_all_metrics(chunk)
            for metric_name, value in metrics.items():
                if value and metric_name not in all_metrics:
                    all_metrics[metric_name] = {
                        "value": value,
                        "chunk_index": i,
                        "context": chunk[:200]  # First 200 chars as context
                    }
        
        return all_metrics
    
    def generate_extraction_summary(self, metrics: Dict) -> str:
        """
        Generate a summary of extracted metrics in JSON format
        """
        summary = {}
        for metric_name, data in metrics.items():
            if data["value"]:
                summary[metric_name] = {
                    "value": data["value"],
                    "source_context": data["context"][:100]
                }
        
        return json.dumps(summary, indent=2)
