# agents.py
def ngo_agent(ngo):
    """
    Evaluates the NGO's trust score and assigns a risk level.
    """
    score = ngo["trust_score"] * 0.6

    if ngo["trust_score"] < 0.4:
        risk = "High Risk"
    elif ngo["trust_score"] < 0.7:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    reasoning = f"Trust Score: {ngo['trust_score']} → {risk}"

    return score, risk, reasoning


def csr_agent(ngo, csr_data):
    """
    Matches NGO with CSR funds based on state and SDG goal.
    Returns a score based on CSR amount.
    """
    for csr in csr_data:
        if ngo["state"] == csr["state"] and ngo["sdg_goal"] == csr["sdg_goal"]:
            score = (csr["csr_amount"] / 100000000) * 0.7  # scaled for scoring
            reasoning = f"CSR Available in {ngo['state']} for {csr['sdg_goal']}: ₹{csr['csr_amount']}"
            return score, csr["csr_amount"], reasoning

    return 0, 0, "No CSR opportunity found"


def supplier_agent(ngo, suppliers):
    """
    Finds a supplier in the NGO's state that matches the SDG goal.
    Returns a score based on supplier reliability.
    """
    for sup in suppliers:
        if ngo["state"] == sup["state"] and ngo["sdg_goal"] == sup["sdg_goal"]:
            score = sup["reliability"] * 0.5  # scaled for scoring
            reasoning = f"Supplier Reliability: {sup['reliability']}"
            return score, sup["name"], reasoning

    return 0, "No Supplier Found", "No operational supplier available"


def decision_agent(ngo_score, csr_score, supplier_score):
    """
    Combines scores from NGO strength, CSR opportunity, and supplier reliability.
    """
    final_score = ngo_score + csr_score + supplier_score
    return round(final_score, 2)
