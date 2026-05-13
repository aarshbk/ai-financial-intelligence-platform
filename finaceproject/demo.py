"""
Quick Demo - AI Financial Intelligence Platform
Demonstrates core functionality without heavy dependencies
"""
import json
import re

# Sample financial document text
sample_financial_text = """
ANNUAL FINANCIAL REPORT - 2024

Total Revenue: $2,500,000,000
Operating Revenue: $2,300,000,000
Net Sales: $2,500,000,000

Operating Income: $600,000,000
Net Income: $440,000,000
Net Earnings: $440,000,000
EBITDA: $750,000,000

Total Assets: $1,800,000,000
Total Equity: $1,300,000,000
Stockholders' Equity: $1,300,000,000

Total Debt: $700,000,000
Long-term Debt: $500,000,000
Short-term Debt: $200,000,000

Operating Cash Flow: $500,000,000
Free Cash Flow: $300,000,000

BUSINESS RISKS:
The company faces regulatory risks due to increased government scrutiny.
Market risk arises from competitive pressures in the technology sector.
Liquidity risk exists due to significant capital expenditures planned.
Operational risks include dependence on key personnel.
Supply chain risk is present due to global sourcing.
Credit risk relates to customer concentration.
Legal disputes could impact profitability.
"""

def extract_financial_metrics(text):
    """Extract financial metrics from text"""
    patterns = {
        "revenue": [
            r"(?:total\s+)?revenue[:\s]+\$?([\d,\.]+)\s*(?:billion|million|thousand|B|M|K)?",
            r"(?:net\s+)?sales[:\s]+\$?([\d,\.]+)",
        ],
        "net_income": [
            r"(?:net\s+)?income[:\s]+\$?([\d,\.]+)",
            r"(?:net\s+)?earnings[:\s]+\$?([\d,\.]+)",
        ],
        "operating_income": [
            r"operating\s+income[:\s]+\$?([\d,\.]+)",
            r"operating\s+profit[:\s]+\$?([\d,\.]+)",
        ],
        "ebitda": [
            r"EBITDA[:\s]+\$?([\d,\.]+)",
        ],
        "total_debt": [
            r"(?:total\s+)?debt[:\s]+\$?([\d,\.]+)",
        ],
        "cash_flow": [
            r"(?:operating\s+)?cash\s+flow[:\s]+\$?([\d,\.]+)",
        ],
        "total_assets": [
            r"(?:total\s+)?assets[:\s]+\$?([\d,\.]+)",
        ],
        "total_equity": [
            r"(?:total\s+)?(?:shareholders?|stockholders?)\s+equity[:\s]+\$?([\d,\.]+)",
        ],
    }
    
    metrics = {}
    for metric_name, patterns_list in patterns.items():
        for pattern in patterns_list:
            matches = re.finditer(pattern, text.lower(), re.IGNORECASE)
            for match in matches:
                try:
                    value = match.group(1).replace(',', '')
                    float(value)
                    metrics[metric_name] = value
                    break
                except:
                    continue
            if metric_name in metrics:
                break
    
    return metrics

def calculate_ratios(metrics):
    """Calculate financial ratios"""
    ratios = {}
    
    def safe_div(num, denom):
        try:
            n = float(num) if num else None
            d = float(denom) if denom else None
            if n and d and d != 0:
                return n / d
        except:
            pass
        return None
    
    # Profit Margin
    pm = safe_div(metrics.get("net_income"), metrics.get("revenue"))
    if pm:
        ratios["profit_margin"] = pm * 100
    
    # Operating Margin
    om = safe_div(metrics.get("operating_income"), metrics.get("revenue"))
    if om:
        ratios["operating_margin"] = om * 100
    
    # Debt-to-Equity
    de = safe_div(metrics.get("total_debt"), metrics.get("total_equity"))
    if de:
        ratios["debt_to_equity"] = de
    
    # Asset Turnover
    at = safe_div(metrics.get("revenue"), metrics.get("total_assets"))
    if at:
        ratios["asset_turnover"] = at
    
    # ROA
    roa = safe_div(metrics.get("net_income"), metrics.get("total_assets"))
    if roa:
        ratios["roa"] = roa * 100
    
    # ROE
    roe = safe_div(metrics.get("net_income"), metrics.get("total_equity"))
    if roe:
        ratios["roe"] = roe * 100
    
    return ratios

def detect_risks(text):
    """Detect financial risks"""
    risk_keywords = {
        "regulatory_risk": ["regulatory", "compliance", "government", "sec", "fda"],
        "liquidity_risk": ["liquidity", "cash flow", "funding", "refinancing"],
        "market_risk": ["market", "competition", "demand", "pricing"],
        "operational_risk": ["operational", "system", "technology", "cyber"],
        "supply_chain_risk": ["supply chain", "supplier", "inventory", "sourcing"],
        "credit_risk": ["credit", "default", "bankruptcy"],
        "legal_risk": ["legal", "dispute", "litigation", "lawsuit"],
    }
    
    text_lower = text.lower()
    risks = {}
    
    for risk_type, keywords in risk_keywords.items():
        count = sum(text_lower.count(kw) for kw in keywords)
        if count > 0:
            risks[risk_type] = min(count / 10, 1.0)
    
    return risks

def main():
    print("\n" + "="*70)
    print("🚀 AI FINANCIAL INTELLIGENCE PLATFORM - DEMO")
    print("="*70 + "\n")
    
    # Step 1: Extract Metrics
    print("📊 STEP 1: EXTRACTING FINANCIAL METRICS")
    print("-" * 70)
    metrics = extract_financial_metrics(sample_financial_text)
    
    for metric, value in metrics.items():
        if value:
            print(f"  ✓ {metric.replace('_', ' ').title()}: ${value}")
    
    # Step 2: Calculate Ratios
    print("\n📈 STEP 2: CALCULATING FINANCIAL RATIOS")
    print("-" * 70)
    ratios = calculate_ratios(metrics)
    
    for ratio_name, value in ratios.items():
        if value:
            if "margin" in ratio_name or "roa" in ratio_name or "roe" in ratio_name:
                print(f"  ✓ {ratio_name.replace('_', ' ').title()}: {value:.2f}%")
            else:
                print(f"  ✓ {ratio_name.replace('_', ' ').title()}: {value:.2f}")
    
    # Step 3: Detect Risks
    print("\n⚠️  STEP 3: DETECTING FINANCIAL RISKS")
    print("-" * 70)
    risks = detect_risks(sample_financial_text)
    
    # Calculate overall risk
    avg_risk = sum(risks.values()) / len(risks) if risks else 0
    if avg_risk >= 0.7:
        risk_level = "HIGH"
    elif avg_risk >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    print(f"  Overall Risk Level: {risk_level} (Score: {avg_risk:.2f})")
    print(f"  Risk Categories Detected: {len(risks)}")
    print("\n  Risk Breakdown:")
    for risk_type, score in sorted(risks.items(), key=lambda x: x[1], reverse=True):
        print(f"    • {risk_type.replace('_', ' ').title()}: {score:.2f}")
    
    # Step 4: Comparison Example
    print("\n🔍 STEP 4: DOCUMENT COMPARISON (EXAMPLE)")
    print("-" * 70)
    
    # 2023 vs 2024 comparison
    metrics_2023 = {"revenue": "2000000000", "net_income": "360000000", "total_debt": "600000000"}
    metrics_2024 = {"revenue": "2500000000", "net_income": "440000000", "total_debt": "700000000"}
    
    print("\n  Year-over-Year Comparison (2023 vs 2024):")
    for metric in metrics_2023.keys():
        v1 = float(metrics_2023[metric])
        v2 = float(metrics_2024[metric])
        pct_change = ((v2 - v1) / v1) * 100
        trend = "📈" if pct_change > 0 else "📉" if pct_change < 0 else "→"
        print(f"    {trend} {metric.replace('_', ' ').title()}")
        print(f"       2023: ${v1:,.0f}")
        print(f"       2024: ${v2:,.0f}")
        print(f"       Change: {pct_change:+.1f}%\n")
    
    # Summary
    print("="*70)
    print("✅ ANALYSIS COMPLETE!")
    print("="*70)
    print("\n📌 This demo shows the core analysis capabilities of the platform.")
    print("\n🚀 To Run the Full Application:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Start backend: python -m uvicorn backend.main:app --reload")
    print("   3. Start frontend: streamlit run frontend/app.py")
    print("   4. Open http://localhost:8501 in your browser")
    print("\n📚 Documentation:")
    print("   • START_HERE.md - Visual project summary")
    print("   • QUICKSTART.md - 5-minute setup guide")
    print("   • README.md - Complete documentation")
    print("   • ARCHITECTURE.md - System design")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
