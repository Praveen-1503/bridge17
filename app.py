# app.py
import streamlit as st
import pandas as pd

from agents import ngo_agent, csr_agent, supplier_agent, decision_agent
from auth import initialize_session, login_page
from dashboard import show_overview
from history import add_to_history, show_history
from utils import load_json

st.set_page_config(page_title="Bridge17", layout="wide")

initialize_session()

if not st.session_state.authenticated:
    login_page()
    st.stop()

# Load Data
ngos = load_json("ngos.json")
suppliers = load_json("suppliers.json")

uploaded_file = st.file_uploader("Upload CSR JSON Report", type=["json"])
if uploaded_file:
    csr_data = load_json(uploaded_file)
else:
    csr_data = load_json("csr.json")

show_overview(ngos)
show_history()

states = sorted(list(set(n["state"] for n in ngos)))
sdgs = sorted(list(set(n["sdg_goal"] for n in ngos)))

selected_state = st.selectbox("Select State", states)
selected_sdg = st.selectbox("Select SDG Goal", sdgs)

if st.button("🔍 View Matchings"):

    filtered = [
        n for n in ngos
        if n["state"] == selected_state
        and n["sdg_goal"] == selected_sdg
    ]

    results = []

    for ngo in filtered:
        ngo_score, risk, _ = ngo_agent(ngo)
        csr_score, csr_amount, _ = csr_agent(ngo, csr_data)
        supplier_score, supplier_name, _ = supplier_agent(ngo, suppliers)
        final_score = decision_agent(ngo_score, csr_score, supplier_score)

        results.append({
            "NGO": ngo["name"],
            "Score": final_score,
            "Risk": risk,
            "CSR": csr_amount,
            "Supplier": supplier_name
        })

    if results:
        results = sorted(results, key=lambda x: x["Score"], reverse=True)
        top = results[0]

        st.success(f"🏆 Top Recommendation: {top['NGO']} ({top['Score']})")

        df = pd.DataFrame(results)
        st.dataframe(df)

        add_to_history(selected_state, selected_sdg, top["NGO"], top["Score"])
    else:
        st.warning("No matching NGOs found.")
