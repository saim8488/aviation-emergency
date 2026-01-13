import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pak-Aviation Emergency Advisor", page_icon="✈️", layout="wide")

# --- SECRETS & API SETUP ---
# On Streamlit Cloud, add your key to 'Secrets' with the name: GEMINI_KEY
try:
    API_KEY = st.secrets["GEMINI_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception:
    st.error("API Key not found. Please set 'GEMINI_KEY' in Streamlit Secrets.")
    st.stop()

# --- DATA: PAKISTAN AVIATION CONTEXT ---
# Standard routes and major airports in Pakistan
AIRPORTS_DB = {
    "Karachi (OPKC)": {"runway": "3400m", "fuel": "Jet A-1", "emergency_services": "CAT 9"},
    "Lahore (OPLA)": {"runway": "3300m", "fuel": "Jet A-1", "emergency_services": "CAT 9"},
    "Islamabad (OPIS)": {"runway": "3600m", "fuel": "Jet A-1", "emergency_services": "CAT 9"},
    "Quetta (OPQT)": {"runway": "3600m", "fuel": "Jet A-1", "emergency_services": "High Altitude"},
    "Peshawar (OPPS)": {"runway": "2700m", "fuel": "Jet A-1", "emergency_services": "CAT 8"},
    "Multan (OPMT)": {"runway": "3200m", "fuel": "Jet A-1", "emergency_services": "CAT 8"},
}

# Sample historical data for Gemini to learn from
HISTORICAL_DATA = [
    {"date": "2020-05-22", "city": "Karachi", "incident": "PIA 8303 Engine Failure / Gear Issue"},
    {"date": "2010-07-28", "city": "Islamabad", "incident": "Airblue 202 CFIT due to Weather/Pilot Error"},
    {"date": "2012-04-20", "city": "Islamabad", "incident": "Bhoja Air 213 Windshear on Approach"}
]

# --- UI LAYOUT ---
st.title("🇵🇰 Pakistan Aviation Emergency Decision Support")
st.markdown("---")

# Sidebar for Input
with st.sidebar:
    st.header("Emergency Details")
    emergency_type = st.selectbox("Type of Emergency", ["Engine Failure", "Fire/Smoke", "Fuel Leakage", "Medical Emergency", "Hydraulic Failure"])
    location = st.selectbox("Current Nearest Major City", list(AIRPORTS_DB.keys()))
    altitude = st.number_input("Current Altitude (ft)", value=30000, step=1000)
    weather = st.text_input("Current Weather Conditions", "Clear")
    
    generate_btn = st.button("GET VIABLE OPTIONS", type="primary")

# Main Display
if generate_btn:
    with st.spinner("Analyzing data and calculating options..."):
        # Construct the context for Gemini
        historical_context = "\n".join([f"- {d['incident']} at {d['city']}" for d in HISTORICAL_DATA])
        airport_info = AIRPORTS_DB[location]
        
        prompt = f"""
        ACT AS: A Senior Flight Safety Officer for Pakistan Civil Aviation.
        EMERGENCY: {emergency_type} near {location}.
        AIRCRAFT STATUS: Altitude {altitude}ft, Weather: {weather}.
        NEAREST AIRPORT SPECS: {airport_info}.
        HISTORICAL INCIDENTS IN PK: {historical_context}.
        
        TASK: Provide exactly TWO viable options for the pilot. 
        Each option must include:
        1. Action Name (e.g., Immediate Diversion to [Airport])
        2. Reasoning (Why this is safer based on specs or history)
        3. Risks (What to watch out for)
        
        Format as clear, professional bullet points. Use technical aviation terminology.
        """
        
        try:
            response = model.generate_content(prompt)
            
            st.subheader("⚠️ Critical Advisory")
            st.info(f"Analysis complete for {emergency_type} near {location}")
            
            # Show Options in two columns
            col1, col2 = st.columns(2)
            options = response.text.split("Option 2:") # Crude split for layout
            
            with col1:
                st.markdown("### Option 1")
                st.markdown(options[0].replace("Option 1:", ""))
                
            if len(options) > 1:
                with col2:
                    st.markdown("### Option 2")
                    st.markdown(options[1])
            else:
                st.write(response.text) # Fallback if split fails

        except Exception as e:
            st.error(f"Error communicating with AI: {e}")

# Footer
st.markdown("---")
st.caption("Disclaimer: This is a decision support tool for educational purposes only. Always follow official PCAA and Airline SOPs.")