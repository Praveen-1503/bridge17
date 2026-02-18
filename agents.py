def ngo_agent(ngo):
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
    for csr in csr_data:
        if ngo["state"] == csr["state"] and ngo["focus"] == csr["focus"]:
            score = (csr["csr_amount"] / 100000000) * 0.7
            reasoning = f"CSR Available in {ngo['state']}: ₹{csr['csr_amount']}"
            return score, csr["csr_amount"], reasoning
    
    return 0, 0, "No CSR opportunity found"


def supplier_agent(ngo, suppliers):
    for sup in suppliers:
        if ngo["state"] == sup["state"] and ngo["focus"] == sup["sector"]:
            score = sup["reliability"] * 0.5
            reasoning = f"Supplier Reliability: {sup['reliability']}"
            return score, sup["name"], reasoning
    
    return 0, "No Supplier Found", "No operational supplier available"


def decision_agent(ngo_score, csr_score, supplier_score):
    final_score = ngo_score + csr_score + supplier_score
    return round(final_score, 2)
