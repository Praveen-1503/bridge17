import streamlit as st
import json
import pandas as pd
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Bridge17 Agentic AI Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- CUSTOM CSS -----------------
st.markdown("""
<style>
/* Page background gradient */
body, .main {
    background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Title styling */
h1, h2, h3 {
    font-family: 'Montserrat', sans-serif;
    color: #1f2937;
}

/* Sidebar styling */
.css-1d391kg {
    background: linear-gradient(to bottom, #4ade80, #22c55e);
    color: white;
}

/* Table styling */
.stDataFrame th {
    background-color: #10b981 !important;
    color: white !important;
    font-size: 16px;
}
.stDataFrame td {
    font-size: 15px;
    padding: 10px !important;
}

/* Card hover effect */
.card {
    border-radius: 15px;
    background-color: #fef3c7;
    padding: 15px;
    margin-bottom: 10px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

/* Button styling */
.stButton>button {
    background-color: #10b981;
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 8px 15px;
    margin: 5px;
}
.stButton>button:hover {
    background-color: #059669;
}

/* Highlight top recommendation */
.top-card {
    border-radius: 20px;
    background-color: #fef9c3;
    padding: 20px;
    margin: 15px 0;
    border: 2px solid #facc15;
}
</style>
""", unsafe_allow_html=True)

# ----------------- TITLE -----------------
st.title("🤖 Bridge17 - Agentic Partnership Intelligence System")
st.markdown("<h3 style='color:#047857;'>Multi-Agent AI evaluating NGO-Government-CSR-Supplier collaboration</h3>", unsafe_allow_html=True)

# ----------------- LOAD DATA -----------------
with open("ngos.json") as f:
    ngos = json.load(f)

with open("csr.json") as f:
    csr_data = json.load(f)

with open("suppliers.json") as f:
    suppliers = json.load(f)

ngos_df = pd.DataFrame(ngos)

# ----------------- SIDEBAR -----------------
st.sidebar.header("🔎 Filter Options")
selected_state = st.sidebar.selectbox("Select State", ngos_df["state"].unique())
selected_focus = st.sidebar.selectbox("Select Sector", ngos_df["focus"].unique())

filtered_ngos = [ngo for ngo in ngos if ngo["state"] == selected_state and ngo["focus"] == selected_focus]

# ----------------- MAIN LOGIC -----------------
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
        "Details": ngo  # full details for popup
    })

if results:
    df = pd.DataFrame(results).sort_values(by="Final Score", ascending=False)
    
    st.subheader("📊 Ranked Partnership Recommendations")
    
    # Display each NGO as a card
    for idx, row in df.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="card">
                <h4 style='color:#065f46; cursor:pointer;'>{row['NGO']}</h4>
                <p><b>Final Score:</b> {row['Final Score']} &nbsp; | &nbsp; <b>Risk:</b> {row['Risk Level']}</p>
                <p><b>CSR Available:</b> ₹{row['CSR Available']}</p>
                <p><b>Supplier:</b> {row['Supplier']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"View Details - {row['NGO']}"):
                ngo = row["Details"]
                st.markdown("<div class='top-card'>", unsafe_allow_html=True)
                st.markdown(f"<h3>{ngo['name']} - Details</h3>", unsafe_allow_html=True)
                st.markdown(f"<p><b>ID:</b> {ngo['ngo_id']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><b>State:</b> {ngo['state']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><b>Focus:</b> {ngo['focus']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><b>Certified:</b> {'Yes' if ngo['certified'] else 'No'}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><b>Trustee Contact:</b> {ngo['trustee_contact']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p><b>About:</b> {ngo['about']}</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.button("Back to List")
else:
    st.warning("No NGOs found for selected filters.")
