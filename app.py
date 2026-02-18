import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

# -----------------------
# Page Config
# -----------------------
st.set_page_config(
    page_title="Bridge17 Agentic AI Engine",
    layout="wide",
    page_icon="🤝"
)

# -----------------------
# Inject Custom CSS
# -----------------------
st.markdown(
    """
    <style>
    /* Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
        background-attachment: fixed;
    }

    /* Card-like effect for metrics and dataframes */
    .stDataFrame, .stMetric, .stButton {
        border-radius: 12px;
        box-shadow: 3px 3px 15px rgba(0,0,0,0.1);
        background-color: rgba(255,255,255,0.85);
    }

    /* Hover effect for buttons */
    button:hover {
        background-color: #6c63ff !important;
        color: white !important;
        font-weight: bold;
    }

    /* Styled headers */
    h2, h3 {
        color: #3b3b98;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* Animate progress bars */
    .stProgress > div > div {
        transition: width 1s ease-in-out;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------
# Title with subtle animation
# -----------------------
st.markdown(
    """
    <h1 style='text-align:center; color:#2d3436;'>
        🤖 Bridge17 - Agentic Partnership Intelligence System
    </h1>
    <p style='text-align:center; font-size:16px; color:#636e72;'>
        Multi-Agent AI evaluating NGO-Government-CSR-Supplier collaboration for SDG-aligned partnerships.
    </p>
    """,
    unsafe_allow_html=True
)

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
        "Certified": "✅" if ngo.get("certified", False) else "❌",
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
# Session state for clicked NGO
# -----------------------
if "selected_ngo" not in st.session_state:
    st.session_state.selected_ngo = None

# -----------------------
# DETAIL VIEW
# -----------------------
if st.session_state.selected_ngo:
    top = next(item for item in results if item["NGO"] == st.session_state.selected_ngo)

    st.subheader(f"📌 NGO Details: {top['NGO']}")

    # --- Key Metrics Cards ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final Score", top["Final Score"])
    col2.metric("Risk Level", top["Risk Level"])
    col3.metric("CSR Available", f"₹{top['CSR Available']:,}")
    col4.metric("Supplier Partner", top["Supplier"])

    st.markdown("---")

    # --- Component Scores with animated progress bars ---
    st.subheader("📈 Component Scores")
    for component, score in zip(
        ["NGO Strength", "CSR Opportunity", "Supplier Reliability"],
        [top["NGO Score"], top["CSR Score"], top["Supplier Score"]]
    ):
        st.write(f"**{component}**")
        st.progress(min(score, 1.0))

    st.markdown("---")

    # --- NGO Info Section ---
    with st.expander("ℹ️ NGO Additional Details"):
        st.write(f"**NGO ID:** {top['NGO ID']}")
        st.write(f"**Certified:** {top['Certified']}")
        st.write(f"**Trustee Contact:** {top['Trustee Contact']}")
        st.write(f"**About NGO:** {top['About']}")

    # --- Agent Reasoning Section ---
    with st.expander("🧠 Agent Reasoning Explanation"):
        st.write("**NGO Agent:**", top["NGO Agent Reasoning"])
        st.write("**CSR Agent:**", top["CSR Agent Reasoning"])
        st.write("**Supplier Agent:**", top["Supplier Agent Reasoning"])

    st.markdown("---")

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
                if st.button(f"🔍 {row['NGO']}", key=row["NGO"]):
                    st.session_state.selected_ngo = row["NGO"]
                    st.rerun()
            with col2:
                # Color-coded score
                score = row["Final Score"]
                if score >= 1.5:
                    color = "green"
                elif score >= 0.8:
                    color = "orange"
                else:
                    color = "red"
                st.markdown(
                    f"<span style='color:{color}; font-weight:bold'>{score}</span>",
                    unsafe_allow_html=True
                )

        st.divider()

        st.subheader("🏆 Top Recommendation")
        top = df.iloc[0]
        st.success(f"Top NGO: {top['NGO']} with Score {top['Final Score']}")
    else:
        st.warning("No NGOs found for selected filters.")
