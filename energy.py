import streamlit as st
import pandas as pd

st.set_page_config(page_title="Smart Energy Auditor", layout="wide")

# Modern Professional Dark UI CSS
st.markdown("""
    <style>
    /* Gradient Dark Background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }
    
    /* Heading Styling - Electric Blue/Cyan Glow */
    h1 { 
        color: #00d4ff !important; 
        text-align: center; 
        font-size: 3.5rem !important; 
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.6), 0 0 10px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem !important;
        letter-spacing: 2px;
    }
    
    .block-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 25px;
        padding: 3rem;
        backdrop-filter: blur(15px);
    }
    
    h2, h3 { color: #ffffff !important; }
    
    /* Button Style - Updated to Cyan */
    div.stButton > button {
        background: linear-gradient(90deg, #00d4ff, #007bff);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 2.5rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: 0.3s;
    }
    div.stButton > button:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(0, 212, 255, 0.4); }
    
    /* Metrics ko bhi cyan accent diya hai */
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ SMART HOME ENERGY AUDITOR")

# --- App Logic ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'appliance_list' not in st.session_state: st.session_state.appliance_list = []

if st.session_state.step == 1:
    st.subheader("Step 1: Historical & Solar Context")
    col1, col2 = st.columns(2)
    m1 = col1.number_input("Month 1 Units:", value=200)
    m2 = col2.number_input("Month 2 Units:", value=250)
    has_solar = st.checkbox("Do you have a Solar System installed?")
    solar_kw = st.number_input("Solar System Capacity (kW):", value=3.0) if has_solar else 0
    rate = st.number_input("Electricity Rate (₹ per Unit):", value=8.0)
    
    if st.button("Next Step ➡️"):
        st.session_state.update({'m1': m1, 'm2': m2, 'solar_kw': solar_kw, 'rate': rate, 'step': 2})
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("Step 2: Add Appliances")
    appliance_options = {"LED Bulb": 10, "Fan": 70, "TV": 80, "Cooler": 200, "Fridge": 250, "Washing Machine": 400, "AC": 1400}
    name = st.selectbox("Select Appliance", list(appliance_options.keys()))
    watts = st.number_input("Power Rating (Watts)", value=appliance_options[name])
    hours = st.slider("Daily Usage (Hours)", 0, 24, 5)
    
    if st.button("Add Appliance"):
        st.session_state.appliance_list.append({"Name": name, "Watts": watts, "Hours": hours})
    
    st.table(pd.DataFrame(st.session_state.appliance_list))
    if st.button("Next Step ➡️"):
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.subheader("Step 3: Final Analysis")
    
    # Appliance calculation
    df = pd.DataFrame(st.session_state.appliance_list)
    monthly_appliance_usage = 0
    if not df.empty:
        df_grouped = df.groupby('Name').sum().reset_index()
        df_grouped['Daily_kWh'] = (df_grouped['Watts'] * df_grouped['Hours']) / 1000
        monthly_appliance_usage = df_grouped['Daily_kWh'].sum() * 30
    
    # Historical + Solar Logic
    avg_historical = (st.session_state.m1 + st.session_state.m2) / 2
    solar_monthly_production = st.session_state.solar_kw * 4 * 30 
    
    total_estimated_usage = monthly_appliance_usage + avg_historical
    net_units = max(0, total_estimated_usage - solar_monthly_production)
    est_bill = net_units * st.session_state.rate
    
    # Results Display
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Load", f"{total_estimated_usage:.2f} kWh")
    c2.metric("Solar Gen", f"{solar_monthly_production:.2f} kWh")
    c3.metric("Net Units", f"{net_units:.2f} kWh")
    
    st.metric("Estimated Monthly Bill", f"₹ {est_bill:,.2f}")
    
    if not df.empty:
        st.bar_chart(df_grouped.set_index('Name')['Daily_kWh'])
    
    if st.button("Restart App 🔄"):
        st.session_state.appliance_list = []
        st.session_state.step = 1
        st.rerun()