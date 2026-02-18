# app.py
import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Bridge17 - AI Partnership Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Custom CSS for styling
# -------------------------------
st.markdown("""
    <style>
    /* Background gradient */
    .stApp {
        background: linear-gradient(to bottom right, #f0f8ff, #e6f7ff);
        color: #333333;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Sidebar styling */
    .css-1d391kg { 
        background-color: #e0f0ff !important;
    }
    /* DataFrame styling */
    .stDataFrame div.row_heading.level0 {font-weight:bold; color:#004080;}
    .stDataFrame th {background-color:#cce6ff; color:#003366;}
    /* Button styling */
    div.stButton > button:first-child {
        background-color: #007acc;
        color: white;
        border-radius:5px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Title & Description
# -------------------------------
st.title("🤖 Bridge17 - Agentic Partnership Intelligence System")
st.markdown(
    """
    Multi-Agent AI evaluating NGO-Corporate-SDG collaborations.
    Click an NGO's name in the recommendations to view details.
    """
)

# -------------------------------
# Load Data
# -------------------------------
with open("ngos.json") as f:
    ngos = json.load(f)

with open("csr.json") as f:
    csr_data = json.load(f)

with open("suppliers.json") as f:
    suppliers = json.load(f)

# -------------------------------
# Convert to DataFrame for filters
# -------------------------------
ngos_df = pd.DataFrame(ngos)

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔎 Filter Options")
selected_state = st.sidebar.selectbox("Select State", ngos_df["state"].unique())
selected_sdg = st.sidebar.selectbox("Select SDG Goal", ngos_df["sdg_goal"].unique())

# Filter NGOs
filtered_ngos = [ngo for ngo in ngos if ngo["state"] == selected_state and ngo["sdg_goal"] == selected_sdg]

# -------------------------------
# Evaluate NGOs
# -------------------------------
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
        "NGO Details": ngo  # full details for click view
    })

# -------------------------------
# Display Results
# -------------------------------
if results:
    df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)

    st.subheader("📊 Ranked Partnership Recommendations")

    # Add clickable selection
    ngo_names = df["NGO"].tolist()
    selected_ngo_name = st.selectbox("Select NGO to view details:", ["--Select--"] + ngo_names)

    if selected_ngo_name != "--Select--":
        # Show NGO details
        ngo_detail = next((r["NGO Details"] for r in results if r["NGO"] == selected_ngo_name), None)
        if ngo_detail:
            st.markdown(f"### 🏛 {ngo_detail['name']}")
            st.markdown(f"**ID:** {ngo_detail['ngo_id']}")
            st.markdown(f"**State:** {ngo_detail['state']}")
            st.markdown(f"**SDG Goal:** {ngo_detail['sdg_goal']}")
            st.markdown(f"**Certified:** {'✅ Yes' if ngo_detail['certified'] else '❌ No'}")
            st.markdown(f"**Trustee Contact:** {ngo_detail['trustee_contact']}")
            st.markdown(f"**About NGO:** {ngo_detail['about']}")
            # Back button
            if st.button("⬅ Back to Rankings"):
                selected_ngo_name = "--Select--"
    else:
        st.dataframe(df[["NGO","Final Score","Risk Level","CSR Available","Supplier"]])

        st.subheader("🏆 Top Recommendation")
        top = df.iloc[0]
        st.success(f"Top NGO: {top['NGO']} with Score {top['Final Score']}")

        st.subheader("📈 Score Breakdown")
        breakdown_data = {
            "Component": ["NGO Strength", "CSR Opportunity", "Supplier Reliability"],
            "Score": [ngo_agent(top["NGO Details"])[0],
                      csr_agent(top["NGO Details"], csr_data)[0],
                      supplier_agent(top["NGO Details"], suppliers)[0]]
        }
        breakdown_df = pd.DataFrame(breakdown_data)
        st.bar_chart(breakdown_df.set_index("Component"))

        st.subheader("🧠 Agent Reasoning Explanation")
        st.write(top["NGO Agent Reasoning"])
        st.write(top["CSR Agent Reasoning"])
        st.write(top["Supplier Agent Reasoning"])
else:
    st.warning("No NGOs found for selected filters.")
