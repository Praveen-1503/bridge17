# app.py
import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

st.set_page_config(
    page_title="Bridge17 - AI Partnership Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# Load Data
# -------------------------------
with open("ngos.json") as f:
    ngos = json.load(f)

with open("csr.json") as f:
    csr_data = json.load(f)

with open("suppliers.json") as f:
    suppliers = json.load(f)

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("🔎 Filter Options")
df_ngos = pd.DataFrame(ngos)
selected_state = st.sidebar.selectbox("Select State", df_ngos["state"].unique())
selected_sdg = st.sidebar.selectbox("Select SDG Goal", df_ngos["sdg_goal"].unique())

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
        "SDG Goal": ngo["sdg_goal"],
        "NGO Agent Reasoning": ngo_reason,
        "CSR Agent Reasoning": csr_reason,
        "Supplier Agent Reasoning": supplier_reason,
        "NGO Details": ngo
    })

# -------------------------------
# Display Table (Clickable)
# -------------------------------
if results:
    df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)
    st.subheader("📊 Ranked Partnership Recommendations")

    # Use st.markdown with HTML links to avoid extra spacing
    for idx, row in df.iterrows():
        sdg_color = sdg_colors.get(row["SDG Goal"], "#cccccc")
        ngo_link = f"<button style='background-color:#007ACC;color:white;padding:5px 10px;border-radius:5px;border:none;margin-bottom:3px;cursor:pointer'>{row['NGO']} | <span style='background-color:{sdg_color};padding:3px;border-radius:3px;color:white'>{row['SDG Goal']}</span></button>"
        if st.markdown(ngo_link, unsafe_allow_html=True):
            pass  # placeholder, HTML button not interactive, we'll handle click below

    # Use session state to store selected NGO
    if "selected_ngo" not in st.session_state:
        st.session_state.selected_ngo = None

    # Click simulation: select NGO via selectbox temporarily to show details
    selected_ngo_name = st.selectbox("Select NGO to view details (hidden dropdown for session state)", ["--None--"] + df["NGO"].tolist(), index=0)
    if selected_ngo_name != "--None--":
        ngo_detail = next((r["NGO Details"] for r in results if r["NGO"] == selected_ngo_name), None)
        if ngo_detail:
            sdg_color = sdg_colors.get(ngo_detail["sdg_goal"], "#cccccc")
            st.markdown(f"### 🏛 {ngo_detail['name']}")
            st.markdown(f"**ID:** {ngo_detail['ngo_id']}")
            st.markdown(f"**State:** {ngo_detail['state']}")
            st.markdown(
                f"<span style='background-color:{sdg_color}; color:white; padding:3px; border-radius:3px;'>{ngo_detail['sdg_goal']}</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"**Certified:** {'✅ Yes' if ngo_detail['certified'] else '❌ No'}")
            st.markdown(f"**Trustee Contact:** {ngo_detail['trustee_contact']}")
            st.markdown(f"**About NGO:** {ngo_detail['about']}")
            if st.button("⬅ Back to Rankings"):
                st.session_state.selected_ngo = None
else:
    st.warning("No NGOs found for selected filters.")
