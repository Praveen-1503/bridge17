# history.py
import streamlit as st

def add_to_history(state, sdg, ngo, score):
    st.session_state.history.append({
        "state": state,
        "sdg": sdg,
        "ngo": ngo,
        "score": score
    })


def show_history():
    st.sidebar.markdown("## 🕘 Match History")

    if not st.session_state.history:
        st.sidebar.info("No history yet")
        return

    for i, record in enumerate(st.session_state.history):
        st.sidebar.write(
            f"{record['state']} | {record['sdg']} → {record['ngo']} ({record['score']})"
        )
