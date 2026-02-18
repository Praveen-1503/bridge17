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
selected_sdg = st.sidebar.selectbox("Select SDG Goal", ngos_df["sdg_goal"].unique())

# Filter NGOs based on SDG Goal
filtered_ngos = [ngo for ngo in ngos if ngo["state"] == selected_state and ngo["sdg_goal"] == selected_sdg]

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
        "Supplier Agent Reasoning": supplier_reason,
        "NGO Details": ngo  # Keep all details
    })

if results:
    df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)

    st.subheader("📊 Ranked Partnership Recommendations")

    # Add a "More Details" column with buttons
    if "selected_ngo" not in st.session_state:
        st.session_state.selected_ngo = None

    # Header row
    header_cols = st.columns([2,1,1,1,1,1])
    header_cols[0].write("**NGO**")
    header_cols[1].write("**Final Score**")
    header_cols[2].write("**Risk Level**")
    header_cols[3].write("**CSR Available**")
    header_cols[4].write("**Supplier**")
    header_cols[5].write("**More Details**")

    # Display each row
    for idx, row in df.iterrows():
        cols = st.columns([2,1,1,1,1,1])
        cols[0].write(f"{row['NGO']}")
        cols[1].write(row["Final Score"])
        cols[2].write(row["Risk Level"])
        cols[3].write(f"₹{row['CSR Available']}")
        cols[4].write(row["Supplier"])
        # More Details button
        if cols[5].button("More Details", key=row['NGO']):
            st.session_state.selected_ngo = row['NGO']

    # Show NGO details if selected
    if st.session_state.selected_ngo:
        ngo_detail = next((r["NGO Details"] for r in results if r["NGO"] == st.session_state.selected_ngo), None)
        if ngo_detail:
            st.subheader(f"🏛 {ngo_detail['name']} - Full Details")
            st.markdown(f"**ID:** {ngo_detail['ngo_id']}")
            st.markdown(f"**State:** {ngo_detail['state']}")
            st.markdown(f"**SDG Goal:** {ngo_detail['sdg_goal']}")
            st.markdown(f"**Certified:** {'✅ Yes' if ngo_detail['certified'] else '❌ No'}")
            st.markdown(f"**Trustee Contact:** {ngo_detail['trustee_contact']}")
            st.markdown(f"**About NGO:** {ngo_detail['about']}")
            if st.button("⬅ Back to Rankings"):
                st.session_state.selected_ngo = None

    # Highlight top NGO and score breakdown
    top = df.iloc[0]
    st.subheader("🏆 Top Recommendation")
    st.success(f"Top NGO: {top['NGO']} with Score {top['Final Score']}")

    st.subheader("📈 Score Breakdown")
    breakdown_data = {
        "Component": ["NGO Strength", "CSR Opportunity", "Supplier Reliability"],
        "Score": [
            ngo_agent(top["NGO Details"])[0],
            csr_agent(top["NGO Details"], csr_data)[0],
            supplier_agent(top["NGO Details"], suppliers)[0]
        ]
    }
    breakdown_df = pd.DataFrame(breakdown_data)
    st.bar_chart(breakdown_df.set_index("Component"))

    st.subheader("🧠 Agent Reasoning Explanation")
    st.write(top["NGO Agent Reasoning"])
    st.write(top["CSR Agent Reasoning"])
    st.write(top["Supplier Agent Reasoning"])

else:
    st.warning("No NGOs found for selected filters.")
