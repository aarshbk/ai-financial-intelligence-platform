"""
Risk Detection Module
Classifies and identifies risk statements in financial documents
"""
import re
from typing import Dict, List, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskCategory(str, Enum):
    """Risk categories in financial documents"""
    REGULATORY = "regulatory_risk"
    LIQUIDITY = "liquidity_risk"
    MARKET = "market_risk"
    OPERATIONAL = "operational_risk"
    SUPPLY_CHAIN = "supply_chain_risk"
    CREDIT = "credit_risk"
    LEGAL = "legal_risk"


class RiskDetector:
    """Detect and classify risks in financial documents"""
    
    def __init__(self):
        self.risk_keywords = {
            RiskCategory.REGULATORY: [
                "regulatory", "compliance", "regulation", "legal", "lawsuit",
                "litigation", "government", "fda", "sec", "antitrust",
                "sanctions", "embargo", "violation", "penalty", "fine"
            ],
            RiskCategory.LIQUIDITY: [
                "liquidity", "cash flow", "funding", "credit facility",
                "debt covenant", "refinancing", "solvency", "working capital",
                "short-term", "debt maturity", "cash requirement"
            ],
            RiskCategory.MARKET: [
                "market risk", "interest rate", "currency", "exchange rate",
                "commodity price", "volatility", "market condition",
                "demand", "competition", "market share", "pricing pressure"
            ],
            RiskCategory.OPERATIONAL: [
                "operational", "system failure", "infrastructure", "cyber",
                "cybersecurity", "data breach", "human error", "process",
                "efficiency", "technology", "disruption", "disaster"
            ],
            RiskCategory.SUPPLY_CHAIN: [
                "supply chain", "supplier", "inventory", "logistics",
                "transportation", "distribution", "shortage", "disruption",
                "sourcing", "raw material", "procurement"
            ],
            RiskCategory.CREDIT: [
                "credit risk", "default", "counterparty", "credit rating",
                "bankruptcy", "insolvency", "customer concentration"
            ],
            RiskCategory.LEGAL: [
                "legal", "dispute", "claim", "settlement", "arbitration",
                "contract", "intellectual property", "patent"
            ],
        }
    
    def detect_risk_category(self, text: str) -> Dict[str, float]:
        """
        Detect risk categories in text with confidence scores
        
        Returns:
            Dictionary of risk categories with confidence scores (0-1)
        """
        text_lower = text.lower()
        risk_scores = {cat: 0 for cat in RiskCategory}
        
        for category, keywords in self.risk_keywords.items():
            matches = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                matches += len(re.findall(r'\b' + keyword + r'\b', text_lower))
            
            # Normalize score (cap at 1.0)
            score = min(matches / 10, 1.0)
            risk_scores[category] = score
        
        return risk_scores
    
    def identify_risk_sentences(self, text: str, threshold: float = 0.3) -> Dict[str, List[str]]:
        """
        Identify sentences containing risks above threshold
        
        Returns:
            Dictionary mapping risk categories to sentences
        """
        sentences = re.split(r'[.!?]+', text)
        risk_sentences = {cat: [] for cat in RiskCategory}
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            sentence_scores = self.detect_risk_category(sentence)
            
            for category, score in sentence_scores.items():
                if score >= threshold:
                    risk_sentences[category].append({
                        "text": sentence.strip(),
                        "confidence": score
                    })
        
        return risk_sentences
    
    def get_top_risks(self, text: str, top_n: int = 5) -> List[Dict]:
        """
        Get top N risks from text with highest confidence scores
        """
        risk_sentences = self.identify_risk_sentences(text, threshold=0.1)
        
        all_risks = []
        for category, sentences in risk_sentences.items():
            for sentence in sentences:
                all_risks.append({
                    "category": category,
                    "text": sentence["text"],
                    "confidence": sentence["confidence"]
                })
        
        # Sort by confidence and return top N
        all_risks.sort(key=lambda x: x["confidence"], reverse=True)
        return all_risks[:top_n]
    
    def generate_risk_report(self, text: str) -> Dict:
        """
        Generate comprehensive risk report
        """
        category_scores = self.detect_risk_category(text)
        top_risks = self.get_top_risks(text, top_n=10)
        
        # Filter categories with non-zero scores
        active_risks = {
            cat: score for cat, score in category_scores.items() 
            if score > 0
        }
        
        # Sort by score
        active_risks = dict(
            sorted(active_risks.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            "risk_categories": active_risks,
            "top_risks": top_risks,
            "overall_risk_level": self._calculate_overall_risk(category_scores),
            "risk_count": len(active_risks)
        }
    
    def _calculate_overall_risk(self, category_scores: Dict) -> str:
        """
        Calculate overall risk level based on category scores
        """
        avg_score = sum(category_scores.values()) / len(category_scores)
        
        if avg_score >= 0.7:
            return "HIGH"
        elif avg_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
