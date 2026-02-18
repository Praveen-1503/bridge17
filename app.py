import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="Bridge17 Agentic AI Engine", layout="wide")

# -------------------------------
# Custom CSS for Simple Aesthetic Design
# -------------------------------
st.markdown("""
<style>
/* Main page: default background, simple padding */
[data-testid="stAppViewContainer"] {
    padding: 20px;
}

/* Sidebar: soft muted lavender, lightly rounded */
[data-testid="stSidebar"] {
    background-color: #f3f0ff;
    border-radius: 8px;
    padding: 15px;
}

/* Table headers */
div[data-baseweb="table"] th {
    background-color: #d6c7ff;
    color: black;
    font-size: 15px;
}

/* Table cells */
div[data-baseweb="table"] td {
    font-size: 14px;
    color: black;
}

/* NGO cards: clean white with subtle shadow */
.ngo-card {
    border: 1px solid #e0e0e0;
    padding: 15px;
    border-radius: 10px;
    background-color: #ffffff;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}

/* Buttons style: soft violet */
.stButton>button {
    background-color: #b9a3ff;
    color: black;
    font-weight: bold;
    border-radius: 5px;
    padding: 5px 10px;
}

.stButton>button:hover {
    background-color: #9d87ff;
}

/* SDG badge: soft pastel rounded */
.sdg-badge {
    padding: 3px 7px;
    border-radius: 5px;
    font-weight: bold;
    color: black;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Title
# -------------------------------
st.markdown("<h1 style='color:#5C4BFF;'>🤖 Bridge17 - Agentic Partnership Intelligence System</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:16px; color:#333;'>Multi-Agent AI evaluating NGO-Government-CSR-Supplier collaboration.</p>", unsafe_allow_html=True)

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
# SDG Colors (Pastel Minimal)
# -------------------------------
sdg_colors = {
    "SDG 1 – No Poverty": "#FFDDDD",
    "SDG 2 – Zero Hunger": "#FFF1CC",
    "SDG 3 – Good Health & Well-being": "#DDFFDD",
    "SDG 4 – Quality Education": "#FFE6E6",
    "SDG 5 – Gender Equality": "#FFD9E6",
    "SDG 6 – Clean Water & Sanitation": "#D9EEFF",
    "SDG 7 – Affordable & Clean Energy": "#FFF8CC",
    "SDG 8 – Decent Work & Economic Growth": "#FFE0F0",
    "SDG 9 – Industry, Innovation & Infrastructure": "#FFE5CC",
    "SDG 10 – Reduced Inequalities": "#E6DDFF",
    "SDG 11 – Sustainable Cities & Communities": "#FFF5CC",
    "SDG 12 – Responsible Consumption & Production": "#EEFFDD",
    "SDG 13 – Climate Action": "#CCFFEE",
    "SDG 14 – Life Below Water": "#CCEBFF",
    "SDG 15 – Life on Land": "#E6FFCC",
    "SDG 16 – Peace, Justice & Strong Institutions": "#D9E6FF",
    "SDG 17 – Partnerships for the Goals": "#E6CCFF"
}

# -------------------------------
# Filters
# -------------------------------
states = sorted(list(set(ngo["state"] for ngo in ngos)))
sdgs = sorted(list(set(ngo["sdg_goal"] for ngo in ngos)))

selected_state = st.sidebar.selectbox("Select State", states)
selected_sdg = st.sidebar.selectbox("Select SDG Goal", sdgs)

# -------------------------------
# Filter NGOs and Run Agents
# -------------------------------
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
        "NGO Score": ngo_score,
        "CSR Score": csr_score,
        "Supplier Score": supplier_score,
        "NGO Agent Reasoning": ngo_reason,
        "CSR Agent Reasoning": csr_reason,
        "Supplier Agent Reasoning": supplier_reason,
        "NGO Details": ngo
    })

# -------------------------------
# Display Ranked Table
# -------------------------------
if results:
    results = sorted(results, key=lambda x: x["Final Score"], reverse=True)

    if "selected_ngo" not in st.session_state:
        st.session_state.selected_ngo = None

    st.subheader("📊 Ranked Partnership Recommendations")

    # Header Row
    header_cols = st.columns([2,1,1,1,1,1])
    header_cols[0].write("**NGO**")
    header_cols[1].write("**Final Score**")
    header_cols[2].write("**Risk Level**")
    header_cols[3].write("**CSR Available**")
    header_cols[4].write("**Supplier**")
    header_cols[5].write("**More Details**")

    # Rows
    for idx, row in enumerate(results):
        cols = st.columns([2,1,1,1,1,1])
        cols[0].markdown(f"**{row['NGO']}**")
        cols[1].write(row["Final Score"])
        cols[2].write(row["Risk Level"])
        cols[3].write(f"₹{row['CSR Available']}")
        cols[4].write(row["Supplier"])
        if cols[5].button("More Details", key=f"more_{row['NGO']}"):
            st.session_state.selected_ngo = row['NGO']

    # -------------------------------
    # Show Full NGO Details
    # -------------------------------
    if st.session_state.selected_ngo:
        ngo_detail = next((r["NGO Details"] for r in results if r["NGO"] == st.session_state.selected_ngo), None)
        if ngo_detail:
            sdg_color = sdg_colors.get(ngo_detail["sdg_goal"], "#cccccc")
            st.markdown(f"<div class='ngo-card'>", unsafe_allow_html=True)
            st.markdown(f"### {ngo_detail['name']}")
            st.markdown(f"**ID:** {ngo_detail['ngo_id']}")
            st.markdown(f"**State:** {ngo_detail['state']}")
            st.markdown(f"<span class='sdg-badge' style='background-color:{sdg_color};'>{ngo_detail['sdg_goal']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Certified:** {'✅ Yes' if ngo_detail['certified'] else '❌ No'}")
            st.markdown(f"**Trustee Contact:** {ngo_detail['trustee_contact']}")
            st.markdown(f"**About NGO:** {ngo_detail['about']}")
            if st.button("⬅ Back to Rankings"):
                st.session_state.selected_ngo = None
            st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------
    # Top Recommendation & Breakdown
    # -------------------------------
    top = results[0]
    st.subheader("🏆 Top Recommendation")
    st.success(f"Top NGO: {top['NGO']} with Score {top['Final Score']}")

    st.subheader("📈 Score Breakdown")
    breakdown_data = {
        "Component": ["NGO Strength", "CSR Opportunity", "Supplier Reliability"],
        "Score": [top["NGO Score"], top["CSR Score"], top["Supplier Score"]]
    }
    breakdown_df = pd.DataFrame(breakdown_data)
    st.bar_chart(breakdown_df.set_index("Component"))

    st.subheader("🧠 Agent Reasoning Explanation")
    st.write(top["NGO Agent Reasoning"])
    st.write(top["CSR Agent Reasoning"])
    st.write(top["Supplier Agent Reasoning"])

    # -------------------------------
    # CSR Allocation Chart
    # -------------------------------
    st.subheader("📊 CSR Allocation in Selected State")
    state_csr = [c for c in csr_data if c["state"] == selected_state]
    if state_csr:
        csr_df = pd.DataFrame(state_csr)
        csr_df_plot = csr_df.groupby("sdg_goal")["csr_amount"].sum().reset_index()
        st.bar_chart(csr_df_plot.set_index("sdg_goal")["csr_amount"])

else:
    st.warning("No NGOs found for selected filters.")
