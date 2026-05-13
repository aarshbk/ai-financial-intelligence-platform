"""
Financial Ratio Calculator
Calculates financial indicators based on extracted metrics
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FinancialRatioCalculator:
    """Calculate financial ratios and indicators"""
    
    def safe_divide(self, numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
        """Safely divide two numbers"""
        if numerator is None or denominator is None or denominator == 0:
            return None
        return numerator / denominator
    
    def to_float(self, value: Optional[str]) -> Optional[float]:
        """Convert string value to float"""
        if value is None:
            return None
        try:
            return float(value)
        except:
            return None
    
    def calculate_profit_margin(self, net_income: Optional[str], revenue: Optional[str]) -> Optional[float]:
        """
        Calculate profit margin: (Net Income / Revenue) * 100
        """
        net_income_val = self.to_float(net_income)
        revenue_val = self.to_float(revenue)
        
        result = self.safe_divide(net_income_val, revenue_val)
        return result * 100 if result else None
    
    def calculate_operating_margin(self, operating_income: Optional[str], revenue: Optional[str]) -> Optional[float]:
        """
        Calculate operating margin: (Operating Income / Revenue) * 100
        """
        op_income_val = self.to_float(operating_income)
        revenue_val = self.to_float(revenue)
        
        result = self.safe_divide(op_income_val, revenue_val)
        return result * 100 if result else None
    
    def calculate_debt_to_equity(self, total_debt: Optional[str], total_equity: Optional[str]) -> Optional[float]:
        """
        Calculate debt-to-equity ratio: Total Debt / Total Equity
        """
        debt_val = self.to_float(total_debt)
        equity_val = self.to_float(total_equity)
        
        return self.safe_divide(debt_val, equity_val)
    
    def calculate_asset_turnover(self, revenue: Optional[str], total_assets: Optional[str]) -> Optional[float]:
        """
        Calculate asset turnover: Revenue / Total Assets
        """
        revenue_val = self.to_float(revenue)
        assets_val = self.to_float(total_assets)
        
        return self.safe_divide(revenue_val, assets_val)
    
    def calculate_return_on_assets(self, net_income: Optional[str], total_assets: Optional[str]) -> Optional[float]:
        """
        Calculate return on assets (ROA): (Net Income / Total Assets) * 100
        """
        net_income_val = self.to_float(net_income)
        assets_val = self.to_float(total_assets)
        
        result = self.safe_divide(net_income_val, assets_val)
        return result * 100 if result else None
    
    def calculate_return_on_equity(self, net_income: Optional[str], total_equity: Optional[str]) -> Optional[float]:
        """
        Calculate return on equity (ROE): (Net Income / Total Equity) * 100
        """
        net_income_val = self.to_float(net_income)
        equity_val = self.to_float(total_equity)
        
        result = self.safe_divide(net_income_val, equity_val)
        return result * 100 if result else None
    
    def calculate_current_ratio(self, current_assets: Optional[str], current_liabilities: Optional[str]) -> Optional[float]:
        """
        Calculate current ratio: Current Assets / Current Liabilities
        """
        assets_val = self.to_float(current_assets)
        liabilities_val = self.to_float(current_liabilities)
        
        return self.safe_divide(assets_val, liabilities_val)
    
    def calculate_all_ratios(self, metrics: Dict[str, Optional[str]]) -> Dict[str, Optional[float]]:
        """
        Calculate all available ratios from extracted metrics
        """
        ratios = {
            "profit_margin": self.calculate_profit_margin(
                metrics.get("net_income"), 
                metrics.get("revenue")
            ),
            "operating_margin": self.calculate_operating_margin(
                metrics.get("operating_income"),
                metrics.get("revenue")
            ),
            "debt_to_equity": self.calculate_debt_to_equity(
                metrics.get("total_debt"),
                metrics.get("total_equity")
            ),
            "asset_turnover": self.calculate_asset_turnover(
                metrics.get("revenue"),
                metrics.get("total_assets")
            ),
            "roa": self.calculate_return_on_assets(
                metrics.get("net_income"),
                metrics.get("total_assets")
            ),
            "roe": self.calculate_return_on_equity(
                metrics.get("net_income"),
                metrics.get("total_equity")
            ),
        }
        
        return ratios
    
    def format_ratio(self, ratio: Optional[float], ratio_type: str) -> str:
        """Format ratio for display"""
        if ratio is None:
            return "N/A"
        
        if "margin" in ratio_type or "roa" in ratio_type or "roe" in ratio_type:
            return f"{ratio:.2f}%"
        else:
            return f"{ratio:.2f}"
