"""
Multi-Document Comparison Module
Compares financial metrics across multiple reports
"""
from typing import Dict, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


class DocumentComparator:
    """Compare financial metrics across multiple documents"""
    
    def __init__(self):
        pass
    
    def to_float(self, value: Optional[str]) -> Optional[float]:
        """Convert string value to float"""
        if value is None:
            return None
        try:
            return float(value)
        except:
            return None
    
    def calculate_percentage_change(self, old_value: Optional[float], new_value: Optional[float]) -> Optional[float]:
        """
        Calculate percentage change from old to new value
        
        Returns:
            Percentage change (positive for increase, negative for decrease)
        """
        if old_value is None or new_value is None or old_value == 0:
            return None
        
        change = ((new_value - old_value) / abs(old_value)) * 100
        return change
    
    def calculate_absolute_change(self, old_value: Optional[float], new_value: Optional[float]) -> Optional[float]:
        """
        Calculate absolute change from old to new value
        """
        if old_value is None or new_value is None:
            return None
        
        return new_value - old_value
    
    def compare_metrics(self, 
                       doc1_metrics: Dict[str, Optional[str]], 
                       doc2_metrics: Dict[str, Optional[str]],
                       doc1_name: str = "Document 1",
                       doc2_name: str = "Document 2") -> Dict:
        """
        Compare metrics between two documents
        """
        comparison = {
            "doc1": doc1_name,
            "doc2": doc2_name,
            "metrics": {}
        }
        
        # Compare common metrics
        all_metrics = set(doc1_metrics.keys()) | set(doc2_metrics.keys())
        
        for metric in all_metrics:
            val1 = self.to_float(doc1_metrics.get(metric))
            val2 = self.to_float(doc2_metrics.get(metric))
            
            pct_change = self.calculate_percentage_change(val1, val2)
            abs_change = self.calculate_absolute_change(val1, val2)
            
            comparison["metrics"][metric] = {
                f"{doc1_name}": val1,
                f"{doc2_name}": val2,
                "absolute_change": abs_change,
                "percentage_change": pct_change,
                "trend": self._get_trend(pct_change)
            }
        
        return comparison
    
    def _get_trend(self, pct_change: Optional[float]) -> str:
        """Get trend indicator"""
        if pct_change is None:
            return "N/A"
        elif pct_change > 5:
            return "UP"
        elif pct_change < -5:
            return "DOWN"
        else:
            return "STABLE"
    
    def compare_multiple_documents(self, 
                                   documents: List[Tuple[str, Dict[str, Optional[str]]]]) -> Dict:
        """
        Compare metrics across multiple documents
        
        Args:
            documents: List of tuples (document_name, metrics_dict)
        
        Returns:
            Comprehensive comparison report
        """
        if not documents:
            return {}
        
        report = {
            "documents": [doc[0] for doc in documents],
            "metrics_over_time": {},
            "trends": {}
        }
        
        # Get all unique metrics
        all_metrics = set()
        for _, metrics in documents:
            all_metrics.update(metrics.keys())
        
        # Track metrics over time
        for metric in all_metrics:
            values = []
            for doc_name, metrics in documents:
                val = self.to_float(metrics.get(metric))
                values.append(val)
            
            report["metrics_over_time"][metric] = values
            report["trends"][metric] = self._calculate_trend(values)
        
        return report
    
    def _calculate_trend(self, values: List[Optional[float]]) -> Dict:
        """Calculate trend for a metric across documents"""
        valid_values = [v for v in values if v is not None]
        
        if len(valid_values) < 2:
            return {
                "direction": "N/A",
                "growth_rate": None
            }
        
        # Calculate average growth rate
        growth_rates = []
        for i in range(1, len(valid_values)):
            if valid_values[i-1] != 0:
                growth = ((valid_values[i] - valid_values[i-1]) / abs(valid_values[i-1])) * 100
                growth_rates.append(growth)
        
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else None
        
        direction = "UP" if avg_growth and avg_growth > 0 else "DOWN" if avg_growth and avg_growth < 0 else "STABLE"
        
        return {
            "direction": direction,
            "average_growth_rate": avg_growth
        }
    
    def generate_comparison_table(self, 
                                 documents: List[Tuple[str, Dict[str, Optional[str]]]],
                                 key_metrics: List[str] = None) -> str:
        """
        Generate a comparison table in text format
        """
        if not documents:
            return "No documents to compare"
        
        if key_metrics is None:
            # Use common metrics
            key_metrics = ["revenue", "net_income", "total_debt", "cash_flow"]
        
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("FINANCIAL COMPARISON REPORT")
        lines.append("=" * 80 + "\n")
        
        # Table header
        header = "Metric".ljust(20)
        for doc_name, _ in documents:
            header += f"| {doc_name[:15]:15}"
        header += "| Change %"
        lines.append(header)
        lines.append("-" * 80)
        
        # Table rows
        for metric in key_metrics:
            row = metric.ljust(20)
            values = []
            for _, metrics in documents:
                val = metrics.get(metric)
                values.append(val)
                row += f"| {str(val)[:15]:15}"
            
            # Calculate percentage change if we have at least 2 values
            if len(values) >= 2:
                v1 = self.to_float(values[0])
                v2 = self.to_float(values[1])
                pct = self.calculate_percentage_change(v1, v2)
                row += f"| {pct:.2f}%" if pct else "| N/A"
            
            lines.append(row)
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
