import streamlit as st
import sys
import os

# 1. FIX THE IMPORT ERROR: Manually add the Backend folder to Python's path
# This looks at the current file's folder, goes up one level, and finds 'Backend'
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, "..", "Backend")
sys.path.append(backend_path)

# Now Python can see 'main_graph.py'
from main_graph import app 

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Procurement Guardian", page_icon="🛡️", layout="wide")

st.title("🛡️ Procurement Guardian AI")
st.markdown("### Intelligent Compliance & Duty Auditing System")
st.divider()

# --- SIDEBAR: LOGS ---
st.sidebar.title("🧠 Agent Reasoning")
# A placeholder to update logs dynamically
log_placeholder = st.sidebar.empty()

# --- INPUT AREA ---
user_query = st.text_input("Enter procurement request:", 
                          placeholder="e.g., I want to buy 2 Dell Laptops from Kuwait at 350 KWD each")

if st.button("Run Audit"):
    if user_query:
        with st.spinner("Processing through Agent Graph..."):
            # Prepare input exactly like your image_b1f95f.png
            initial_input = {
                "query": user_query,
                "internal_reasoning": []
            }
            
            # Execute the Backend Logic
            final_state = app.invoke(initial_input)
            
            # DISPLAY RESULTS
            st.success("Analysis Complete!")
            
            # Metrics Row
            m1, m2, m3 = st.columns(3)
            with m1:
                status = final_state.get("audit_status", "N/A")
                color = "normal" if status == "OK" else "inverse"
                st.metric("Audit Status", status, delta_color=color)
            with m2:
                base = final_state.get("total_base_cost", 0.0)
                st.metric("Base Cost", f"{base} KWD")
            with m3:
                final_cost = final_state.get("final_cost_with_duty", 0.0)
                st.metric("Final (with Duty)", f"{final_cost} KWD")

            # Final Output Report
            st.divider()
            st.subheader("📋 Official Inspection Report")
            st.write(final_state.get("final_output", "No report generated."))
            
            # Update Reasoning Log in Sidebar
            logs = final_state.get("internal_reasoning", [])
            log_placeholder.markdown("\n".join([f"- {item}" for item in logs]))
    else:
        st.error("Please enter a query first.")