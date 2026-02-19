# agents.py

def ngo_agent(ngo):
    trust = ngo["trust_score"]

    score = trust * 0.6

    if trust < 0.4:
        risk = "High Risk"
    elif trust < 0.7:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"

    reasoning = f"Trust Score: {trust} → {risk}"
    return score, risk, reasoning


def csr_agent(ngo, csr_data):
    matching = [
        c for c in csr_data
        if c["state"] == ngo["state"]
        and c["sdg_goal"] == ngo["sdg_goal"]
    ]

    if not matching:
        return 0, 0, "No CSR opportunity found"

    max_csr = max(c["csr_amount"] for c in csr_data)
    csr = matching[0]

    normalized = csr["csr_amount"] / max_csr
    score = normalized * 0.7

    reasoning = f"CSR Available: ₹{csr['csr_amount']} (Normalized)"
    return score, csr["csr_amount"], reasoning


def supplier_agent(ngo, suppliers):
    matching = [
        s for s in suppliers
        if s["state"] == ngo["state"]
        and s["sdg_goal"] == ngo["sdg_goal"]
    ]

    if not matching:
        return 0, "No Supplier Found", "No operational supplier available"

    best_supplier = max(matching, key=lambda x: x["reliability"])
    score = best_supplier["reliability"] * 0.5

    reasoning = f"Best Supplier: {best_supplier['name']} (Reliability {best_supplier['reliability']})"

    return score, best_supplier["name"], reasoning


def decision_agent(ngo_score, csr_score, supplier_score):
    final_score = (
        0.4 * ngo_score +
        0.35 * csr_score +
        0.25 * supplier_score
    )
    return round(final_score, 3)
