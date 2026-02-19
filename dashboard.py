# dashboard.py
import streamlit as st
import pandas as pd

def show_overview(ngos):
    st.markdown("## 📊 Ecosystem Overview")

    total_ngos = len(ngos)
    avg_trust = round(sum(n["trust_score"] for n in ngos) / total_ngos, 2)

    col1, col2 = st.columns(2)
    col1.metric("Total NGOs", total_ngos)
    col2.metric("Average Trust Score", avg_trust)

    df = pd.DataFrame(ngos)

    st.subheader("NGOs by State")
    st.bar_chart(df.groupby("state").size())

    st.subheader("NGOs by SDG")
    st.bar_chart(df.groupby("sdg_goal").size())
