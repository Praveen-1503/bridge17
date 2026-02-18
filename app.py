import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="Bridge17 Agentic AI Engine", layout="wide")

# -------------------------------
# Custom CSS for professional look with Spatial Violet mainbar
# -------------------------------
st.markdown("""
<style>
/* Main page background (Spatial Violet) */
[data-testid="stAppViewContainer"] {
    background-color: #5D3FD3;  /* Spatial Violet */
    color: white;
}

/* Sidebar background (Black) */
[data-testid="stSidebar"] {
    background-color: #0a0a0a;  /* Black */
    color: white;
}

/* Table headers */
div[data-baseweb="table"] th {
    background-color: #004080;
    color: white;
    font-size: 16px;
}

/* Table cells */
div[data-baseweb="table"] td {
    font-size: 15px;
    color: white;
}

/* Card style for NGO details */
.ngo-card {
    border: 1px solid #444444;
    padding: 15px;
    border-radius: 10px;
    background-color: #3a2ea0;  /* Darker violet for cards */
    box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    margin-bottom: 15px;
}

/* Buttons style */
.stButton>button {
    background-color: #004080;
    color: white;
    font-weight: bold;
    border-radius: 5px;
    padding: 5px 10px;
}

.stButton>button:hover {
    background-color: #0066cc;
}

/* SDG badge */
.sdg-badge {
    padding: 4px 8px;
    border-radius: 5px;
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Title
# -------------------------------
st.markdown("<h1 style='color:#ffdd00;'>🤖 Bridge17 - Agentic Partnership Intelligence System</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:16px; color:white;'>Multi-Agent AI evaluating NGO-Government-CSR-Supplier collaboration.</p>", unsafe_allow_html=True)

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
# SDG Colors
# -------------------------------
sdg_colors = {
    "SDG 1 – No Poverty": "#E5243B",
    "SDG 2 – Zero Hunger": "#DDA63A",
    "SDG 3 – Good Health & Well-being": "#4C9F38",
    "SDG 4 – Quality Education": "#C5192D",
    "SDG 5 – Gender Equality": "#FF3A21",
    "SDG 6 – Clean Water & Sanitation": "#26BDE2",
    "SDG 7 – Affordable & Clean Energy": "#FCC30B",
    "SDG 8 – Decent Work & Economic Growth": "#A21942",
    "SDG 9 – Industry, Innovation & Infrastructure": "#FD6925",
    "SDG 10 – Reduced Inequalities": "#DD1367",
    "SDG 11 – Sustainable Cities & Communities": "#FD9D24",
    "SDG 12 – Responsible Consumption & Production": "#BF8B2E",
    "SDG 13 – Climate Action": "#3F7E44",
    "SDG 14 – Life Below Water": "#0A97D9",
    "SDG 15 – Life on Land": "#56C02B",
    "SDG 16 – Peace, Justice & Strong Institutions": "#00689D",
    "SDG 17 – Partnerships for the Goals": "#19486A"
}

# -------------------------------
# Filters
# -------------------------------
states = sorted(list(set(ngo["state"] for ngo in ngos)))
sdgs = sorted(list(set(ngo["sdg_goal"] for ngo in ngos)))

selected_state = st.sidebar.selectbox("Select State", states)
selected_sdg = st.sidebar.selectbox("Select SDG Goal", sdgs)

# -------------------------------
# Filter NGOs
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
        if cols[5].button("More Details", key=row['NGO']):
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
