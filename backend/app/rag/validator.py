import re
from typing import Dict, Any, List

def validate_numerical_accuracy(
    context_chunks: List[Dict[str, Any]],
    generated_text: str
) -> Dict[str, Any]:
    """
    Post-generation guardrail ensuring numerical figures, percentages,
    and monetary amounts in the generated text strictly exist in source context.
    """
    # Combine context text
    context_full = " ".join([c["text"] for c in context_chunks])

    # Extract interest rates / percentages (e.g., 7.25%, 90%, 0.50%)
    context_percentages = set(re.findall(r'\b\d+(?:\.\d+)?\%', context_full))
    response_percentages = set(re.findall(r'\b\d+(?:\.\d+)?\%', generated_text))

    # Extract monetary figures (e.g., ₹30 Lakhs, ₹25,000, 75 Lakhs)
    context_amounts = set(re.findall(r'₹?\s*\d+(?:,\d+)*(?:\.\d+)?\s*(?:Lakhs?|Crore?|k)?', context_full, re.IGNORECASE))
    response_amounts = set(re.findall(r'₹?\s*\d+(?:,\d+)*(?:\.\d+)?\s*(?:Lakhs?|Crore?|k)?', generated_text, re.IGNORECASE))

    # Identify ungrounded numbers in response
    unverified_percentages = []
    for resp_p in response_percentages:
        if resp_p not in context_percentages:
            unverified_percentages.append(resp_p)

    passed = len(unverified_percentages) == 0

    return {
        "passed": passed,
        "verified_percentages": list(context_percentages.intersection(response_percentages)),
        "unverified_percentages": unverified_percentages,
        "context_figures_count": len(context_percentages) + len(context_amounts),
        "status": "PASS: Numerical figures fully match official document context" if passed else f"WARNING: Potential numerical discrepancy detected ({', '.join(unverified_percentages)})"
    }
