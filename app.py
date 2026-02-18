# app.py
import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Bridge17 - Agentic Partnership Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #f0f8ff, #e6f7ff);
        color: #333333;
        font-family: 'Segoe UI', sans-serif;
    }
    .css-1d391kg { 
        background-color: #e0f0ff !important;
    }
    .stDataFrame th {background-color:#cce6ff; color:#003366; font-weight:bold;}
    .stButton > button {
        background-color: #007acc;
        color: white;
        border-radius:5px;
    }
    </style>
""", unsafe_allow_html=True)

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
# Title
# -------------------------------
st.title("🤖 Bridge17 - Agentic Partnership Intelligence System")
st.markdown("Multi-Agent AI evaluating NGO-Corporate-SDG collaborations. Click an NGO name in the table to view details.")

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
df_ngos = pd.DataFrame(ngos)
st.sidebar.header("🔎 Filter Options")
selected_state = st.sidebar.selectbox("Select State", df_ngos["state"].unique())
selected_sdg = st.sidebar.selectbox("Select SDG Goal", df_ngos["sdg_goal"].unique())

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
# Display Recommendations
# -------------------------------
if results:
    df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)
    st.subheader("📊 Ranked Partnership Recommendations")

    # Store selected NGO in session state
    if "selected_ngo" not in st.session_state:
        st.session_state.selected_ngo = None

    # Display clickable table
    for idx, row in df.iterrows():
        sdg_color = sdg_colors.get(row["SDG Goal"], "#cccccc")
        if st.button(f"{row['NGO']} | {row['SDG Goal']}", key=row['NGO']):
            st.session_state.selected_ngo = row["NGO"]

    # Show NGO details if selected
    if st.session_state.selected_ngo:
        ngo_detail = next((r["NGO Details"] for r in results if r["NGO"] == st.session_state.selected_ngo), None)
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
        st.dataframe(df[["NGO","Final Score","Risk Level","CSR Available","Supplier","SDG Goal"]], height=400)

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
