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

    # Select Supplier to View Details
    st.subheader("🔍 View Supplier Details")

    supplier_names = df["Supplier"].unique()
    selected_supplier = st.selectbox("Select Supplier", supplier_names)

    if selected_supplier != "No Supplier Found":
        supplier_info = next(
            (sup for sup in suppliers if sup["name"] == selected_supplier),
            None
        )

        if supplier_info:
            st.markdown("### 🏢 Supplier Information")
            st.write(f"**Name:** {supplier_info['name']}")
            st.write(f"**State:** {supplier_info['state']}")
            st.write(f"**Sector:** {supplier_info['sector']}")
            st.write(f"**Reliability Score:** {supplier_info['reliability']}")

            # Visual reliability bar
            st.progress(supplier_info["reliability"])

    else:
        st.info("No supplier matched for this NGO.")

    # Top Recommendation
    st.subheader("🏆 Top Recommendation")

    top = df.iloc[0]
    st.success(f"Top NGO: {top['NGO']} with Score {top['Final Score']}")

else:
    st.warning("No NGOs found for selected filters.")
