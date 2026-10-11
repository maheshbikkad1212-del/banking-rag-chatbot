import re
from typing import Dict, Any, List

def process_query(raw_query: str) -> Dict[str, Any]:
    """
    Standardizes formatting, detects intent, and generates expanded query variants.
    """
    # 1. Query Normalization
    normalized = raw_query.strip()
    normalized = re.sub(r'\s+', ' ', normalized)

    # 2. Intent Detection
    q_lower = normalized.lower()
    intent = "General Banking Policy"
    confidence = 0.85

    if any(k in q_lower for k in ["saving", "savings account", "current account", "bank account", "account type", "minimum balance", "debit card", "credit card", "neft", "rtgs", "imps", "fund transfer"]):
        intent = "Bank Account & Customer Services"
        confidence = 0.95
    elif any(k in q_lower for k in ["loan", "ltv", "dti", "emi", "housing", "mortgage", "cibil", "foreclosure"]):
        intent = "Loan Eligibility & Credit Policy"
        confidence = 0.95
    elif any(k in q_lower for k in ["fd", "fixed deposit", "interest rate", "tenure", "senior citizen", "tax saver", "yield"]):
        intent = "Fixed Deposit Interest Rates"
        confidence = 0.98
    elif any(k in q_lower for k in ["kyc", "nri", "passport", "nre", "nro", "ovd", "re-verification", "proof"]):
        intent = "KYC & NRI Account Guidelines"
        confidence = 0.96
    elif any(k in q_lower for k in ["crar", "basel", "tier 1", "cet1", "lcr", "nsfr", "rwa", "capital adequacy"]):
        intent = "Regulatory Capital & Compliance"
        confidence = 0.94

    # 3. Query Expansion & Keyword Decomposition
    expansions = [normalized]
    if intent == "Bank Account & Customer Services":
        expansions.append(f"{normalized} savings account current account features minimum balance transactions interest")
    elif intent == "Fixed Deposit Interest Rates":
        expansions.append(f"{normalized} deposit rates senior citizen tenure percentage")
    elif intent == "Loan Eligibility & Credit Policy":
        expansions.append(f"{normalized} LTV ratio DTI income limits CIBIL")
    elif intent == "KYC & NRI Account Guidelines":
        expansions.append(f"{normalized} officially valid documents passport NRE NRO account")

    return {
        "raw_query": raw_query,
        "normalized_query": normalized,
        "intent": intent,
        "intent_confidence": confidence,
        "expansions": expansions
    }

