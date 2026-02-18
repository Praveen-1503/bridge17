import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

st.set_page_config(page_title="Bridge17 Agentic AI Engine", layout="wide")

st.title("🤖 Bridge17 - Agentic Partnership Intelligence System")
st.markdown("Multi-Agent AI evaluating NGO-Government-CSR-Supplier collaboration.")

# -----------------------
# Load Data
# -----------------------
with open("ngos.json") as f:
    ngos = json.load(f)

with open("csr.json") as f:
    csr_data = json.load(f)

with open("suppliers.json") as f:
    suppliers = json.load(f)

ngos_df = pd.DataFrame(ngos)

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.header("🔎 Filter Options")
selected_state = st.sidebar.selectbox("Select State", ngos_df["state"].unique())
selected_focus = st.sidebar.selectbox("Select Sector", ngos_df["focus"].unique())

filtered_ngos = [
    ngo for ngo in ngos
    if ngo["state"] == selected_state and ngo["focus"] == selected_focus
]

results = []

# -----------------------
# Multi-Agent Engine
# -----------------------
for ngo in filtered_ngos:

    ngo_score, risk, ngo_reason = ngo_agent(ngo)
    csr_score, csr_amount, csr_reason = csr_agent(ngo, csr_data)
    supplier_score, supplier_name, supplier_reason = supplier_agent(ngo, suppliers)

    final_score = decision_agent(ngo_score, csr_score, supplier_score)

    results.append({
        "NGO ID": ngo.get("ngo_id", ""),
        "NGO": ngo["name"],
        "Certified": "Yes" if ngo.get("certified", False) else "No",
        "Trustee Contact": ngo.get("trustee_contact", ""),
        "About": ngo.get("about", ""),
        "Final Score": final_score,
        "NGO Score": ngo_score,
        "CSR Score": csr_score,
        "Supplier Score": supplier_score,
        "Risk Level": risk,
        "CSR Available": csr_amount,
        "Supplier": supplier_name,
        "NGO Agent Reasoning": ngo_reason,
        "CSR Agent Reasoning": csr_reason,
        "Supplier Agent Reasoning": supplier_reason
    })

# -----------------------
# Initialize session state for click
# -----------------------
if "selected_ngo" not in st.session_state:
    st.session_state.selected_ngo = None

# -----------------------
# DETAIL VIEW
# -----------------------
if st.session_state.selected_ngo:
    top = next(item for item in results if item["NGO"] == st.session_state.selected_ngo)

    st.subheader(f"📌 NGO Details: {top['NGO']}")

    st.write(f"**NGO ID:** {top['NGO ID']}")
    st.write(f"**Certified:** {top['Certified']}")
    st.write(f"**Trustee Contact:** {top['Trustee Contact']}")
    st.write(f"**About NGO:** {top['About']}")
    st.write(f"**Risk Level:** {top['Risk Level']}")
    st.write(f"**CSR Available:** ₹{top['CSR Available']}")
    st.write(f"**Supplier Partner:** {top['Supplier']}")

    st.subheader("📈 Score Breakdown")
    breakdown_df = pd.DataFrame({
        "Component": ["NGO Strength", "CSR Opportunity", "Supplier Reliability"],
        "Score": [
            top["NGO Score"],
            top["CSR Score"],
            top["Supplier Score"]
        ]
    })
    st.bar_chart(breakdown_df.set_index("Component"))

    st.subheader("🧠 Agent Reasoning")
    st.write(top["NGO Agent Reasoning"])
    st.write(top["CSR Agent Reasoning"])
    st.write(top["Supplier Agent Reasoning"])

    if st.button("⬅ Back to Rankings"):
        st.session_state.selected_ngo = None
        st.rerun()

# -----------------------
# RANKING VIEW
# -----------------------
else:
    if results:
        df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)

        st.subheader("📊 Ranked Partnership Recommendations")

        for index, row in df.iterrows():
            col1, col2 = st.columns([3, 1])

            with col1:
                # Make NGO name clickable
                if st.button(f"🔍 {row['NGO']}", key=row["NGO"]):
                    st.session_state.selected_ngo = row["NGO"]
                    st.rerun()

            with col2:
                st.write(f"⭐ {row['Final Score']}")

        st.divider()

        st.subheader("🏆 Top Recommendation")
        top = df.iloc[0]
        st.success(f"Top NGO: {top['NGO']} with Score {top['Final Score']}")
    else:
        st.warning("No NGOs found for selected filters.")
