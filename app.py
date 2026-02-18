import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

st.set_page_config(page_title="Bridge17 Agentic AI Engine", layout="wide")

st.title("🤖 Bridge17 - Agentic Partnership Intelligence System")
st.markdown("Multi-Agent AI evaluating NGO-Government-CSR-Supplier collaboration.")

# Load data
with open("ngos.json") as f:
    ngos = json.load(f)

with open("csr.json") as f:
    csr_data = json.load(f)

with open("suppliers.json") as f:
    suppliers = json.load(f)

# Convert to DataFrame
ngos_df = pd.DataFrame(ngos)

# Sidebar Filters
st.sidebar.header("🔎 Filter Options")
selected_state = st.sidebar.selectbox("Select State", ngos_df["state"].unique())
selected_focus = st.sidebar.selectbox("Select Sector", ngos_df["focus"].unique())

filtered_ngos = [ngo for ngo in ngos if ngo["state"] == selected_state and ngo["focus"] == selected_focus]

results = []

for ngo in filtered_ngos:
    
    ngo_score, risk, ngo_reason = ngo_agent(ngo)
    csr_score, csr_amount, csr_reason = csr_agent(ngo, csr_data)
    supplier_score, supplier_name, supplier_reason = supplier_agent(ngo, suppliers)
    
    final_score = decision_agent(ngo_score, csr_score, supplier_score)
    
    results.append({
        "NGO": ngo["name"],
        "Final Score": final_score,
        "Risk Level": risk,
        "CSR Available": csr_amount,
        "Supplier": supplier_name,
        "NGO Agent Reasoning": ngo_reason,
        "CSR Agent Reasoning": csr_reason,
        "Supplier Agent Reasoning": supplier_reason
    })

if results:
    df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)

    st.subheader("📊 Ranked Partnership Recommendations")
    st.dataframe(df)

    st.subheader("🏆 Top Recommendation")

    top = df.iloc[0]
    st.success(f"Top NGO: {top['NGO']} with Score {top['Final Score']}")

    # Score Breakdown Visualization
    st.subheader("📈 Score Breakdown")

    breakdown_data = {
        "Component": ["NGO Strength", "CSR Opportunity", "Supplier Reliability"],
        "Score": [
            ngo_score,
            csr_score,
            supplier_score
        ]
    }

    breakdown_df = pd.DataFrame(breakdown_data)
    st.bar_chart(breakdown_df.set_index("Component"))

    # Agent Reasoning
    st.subheader("🧠 Agent Reasoning Explanation")
    st.write(top["NGO Agent Reasoning"])
    st.write(top["CSR Agent Reasoning"])
    st.write(top["Supplier Agent Reasoning"])

else:
    st.warning("No NGOs found for selected filters.")
