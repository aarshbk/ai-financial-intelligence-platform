"""
Sample PDF Generator for Testing
Creates a sample financial report PDF
"""
import json


def create_sample_financial_data():
    """Create sample financial data as text"""
    
    sample_data = """
    ANNUAL FINANCIAL REPORT - 2024
    Company: TechCorp International
    Fiscal Year Ending: December 31, 2024
    
    EXECUTIVE SUMMARY
    TechCorp International delivered strong financial performance in 2024, with robust growth across all key metrics.
    
    CONSOLIDATED STATEMENTS OF OPERATIONS
    
    Total Revenue: $2,500,000,000
    Cost of Revenue: $1,200,000,000
    Gross Profit: $1,300,000,000
    
    Operating Expenses:
    Research and Development: $300,000,000
    Sales and Marketing: $250,000,000
    General and Administrative: $150,000,000
    
    Operating Income: $600,000,000
    Interest Expense: $50,000,000
    Income Before Taxes: $550,000,000
    Income Tax Expense: $110,000,000
    
    Net Income: $440,000,000
    
    CONSOLIDATED BALANCE SHEET
    
    Assets:
    Current Assets: $800,000,000
    Property and Equipment: $600,000,000
    Intangible Assets: $400,000,000
    Total Assets: $1,800,000,000
    
    Liabilities:
    Current Liabilities: $400,000,000
    Long-term Debt: $300,000,000
    Total Debt: $700,000,000
    Total Liabilities: $500,000,000
    
    Stockholders' Equity: $1,300,000,000
    
    CASH FLOW STATEMENT
    
    Operating Cash Flow: $500,000,000
    Investing Cash Flow: -$200,000,000
    Free Cash Flow: $300,000,000
    
    EBITDA: $750,000,000
    
    KEY FINANCIAL METRICS
    
    Profit Margin: 17.6%
    Operating Margin: 24.0%
    Return on Assets: 24.4%
    Return on Equity: 33.8%
    Debt-to-Equity Ratio: 0.54
    Asset Turnover: 1.39
    
    BUSINESS RISKS
    
    The company faces several risks including:
    
    1. Regulatory Risk: Increased regulatory scrutiny in key markets including Europe and Asia could impact operations and profitability. The company is closely monitoring regulatory developments.
    
    2. Market Risk: Competitive pressures in the technology sector may affect pricing and market share. Currency exchange rate fluctuations could impact international operations.
    
    3. Liquidity Risk: While the company maintains adequate liquidity, significant capital expenditures could impact working capital levels.
    
    4. Operational Risk: Dependence on key personnel and supply chain disruptions could affect operations.
    
    5. Cybersecurity Risk: As a technology company, we face ongoing cybersecurity threats and potential data breaches that could damage reputation and impact revenue.
    
    REVENUE BREAKDOWN BY SEGMENT
    
    Cloud Services: $1,200,000,000 (48%)
    Software Licensing: $800,000,000 (32%)
    Professional Services: $500,000,000 (20%)
    
    GEOGRAPHIC REVENUE DISTRIBUTION
    
    North America: $1,250,000,000 (50%)
    Europe: $750,000,000 (30%)
    Asia Pacific: $500,000,000 (20%)
    
    OUTLOOK AND GUIDANCE
    
    For 2025, we expect revenue growth of 15-20% and continued margin expansion. However, economic uncertainty and potential supply chain disruptions pose headwinds.
    
    Management believes the company is well-positioned for long-term growth despite near-term challenges.
    """
    
    return sample_data


if __name__ == "__main__":
    data = create_sample_financial_data()
    print(data)
    
    # Save to file for testing
    with open("sample_financial_data.txt", "w") as f:
        f.write(data)
    print("\nSample data saved to sample_financial_data.txt")
