# app.py
import streamlit as st
import json
from agents import ngo_agent, csr_agent, supplier_agent, decision_agent

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Bridge17 - Agentic Partnership Engine",
    layout="wide"
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
    .ngotable th {
        background-color:#cce6ff;
        color:#003366;
        font-weight:bold;
        padding: 8px;
        text-align: left;
    }
    .ngotable td {
        padding: 8px;
    }
    .ngobutton {
        background-color: #007acc;
        color: white;
        border-radius:5px;
        border:none;
        padding:5px 10px;
        cursor:pointer;
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
st.markdown("Click on an NGO name to view its details.")

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
states = sorted(list(set(ngo["state"] for ngo in ngos)))
sdgs = sorted(list(set(ngo["sdg_goal"] for ngo in ngos)))
selected_state = st.sidebar.selectbox("Select State", states)
selected_sdg = st.sidebar.selectbox("Select SDG Goal", sdgs)

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
# Display Recommendations as Table
# -------------------------------
if results:
    results = sorted(results, key=lambda x: x["Final Score"], reverse=True)
    st.subheader("📊 Ranked Partnership Recommendations")

    # Store selected NGO in session state
    if "selected_ngo" not in st.session_state:
        st.session_state.selected_ngo = None

    if st.session_state.selected_ngo is None:
        # Build HTML table
        table_html = "<table class='ngotable'>"
        table_html += "<tr><th>NGO</th><th>Final Score</th><th>Risk Level</th><th>CSR Available</th><th>Supplier</th><th>SDG Goal</th></tr>"
        for row in results:
            sdg_color = sdg_colors.get(row["SDG Goal"], "#cccccc")
            table_html += "<tr>"
            table_html += f"<td><form action='' method='post'><input type='submit' class='ngobutton' name='{row['NGO']}' value='{row['NGO']}'></form></td>"
            table_html += f"<td>{row['Final Score']}</td>"
            table_html += f"<td>{row['Risk Level']}</td>"
            table_html += f"<td>₹{row['CSR Available']}</td>"
            table_html += f"<td>{row['Supplier']}</td>"
            table_html += f"<td style='background-color:{sdg_color}; color:white; padding:3px; border-radius:3px;'>{row['SDG Goal']}</td>"
            table_html += "</tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)

        # Handle NGO selection using a selectbox as a workaround
        selected_ngo = st.selectbox("Click NGO name to view details (temporary)", ["--None--"] + [r["NGO"] for r in results])
        if selected_ngo != "--None--":
            st.session_state.selected_ngo = selected_ngo
    else:
        # Show NGO details
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
    st.warning("No NGOs found for selected filters.")
