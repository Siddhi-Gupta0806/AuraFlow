import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime
import json
import random
import os
from google import genai
from google.genai import types

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & THEME STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AuraFlow - Real-Time Decision Intelligence Platform",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Fidelity CSS for Dark Command Center Aesthetics
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Share+Tech+Mono&display=swap');
    
    /* Main body background & typography */
    .stApp {
        background-color: #0d0e15;
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Headers styling */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Custom Title Area */
    .title-container {
        padding: 1.5rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
    }
    
    .title-main {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding-bottom: 0.2rem;
        font-family: 'Outfit', sans-serif;
    }
    
    .title-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin: 0;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Premium Metric Card Container */
    .kpi-container {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        flex: 1;
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: left;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
    }
    
    .kpi-card.red::before { background: #ef4444; }
    .kpi-card.orange::before { background: #f97316; }
    .kpi-card.green::before { background: #10b981; }
    .kpi-card.blue::before { background: #3b82f6; }
    
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 0.4rem;
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    
    .kpi-status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        vertical-align: middle;
    }
    
    .pulse {
        animation: pulse-animation 2s infinite;
    }
    
    @keyframes pulse-animation {
        0% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.1); opacity: 1; box-shadow: 0 0 8px rgba(239, 68, 68, 0.8); }
        100% { transform: scale(0.9); opacity: 0.8; }
    }
    
    /* Styled Alerts and status badges */
    .status-badge {
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge.high { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    .status-badge.medium { background-color: rgba(249, 115, 22, 0.15); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.3); }
    .status-badge.low { background-color: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }
    
    .status-badge.active { background-color: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    .status-badge.resolving { background-color: rgba(249, 115, 22, 0.15); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.3); }
    .status-badge.resolved { background-color: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
    
    /* Custom Intervention Plan Visual Styling */
    .plan-box {
        background: linear-gradient(135deg, rgba(20, 26, 45, 0.8) 0%, rgba(10, 12, 22, 0.9) 100%);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 8px 32px rgba(168, 85, 247, 0.15);
    }
    
    .plan-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #a855f7;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .plan-section {
        margin-bottom: 1rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .plan-section-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #38bdf8;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .plan-section-text {
        font-size: 0.9rem;
        color: #cbd5e1;
        line-height: 1.4;
    }
    
    /* Citizen feedback cards */
    .feedback-card {
        background: rgba(30, 41, 59, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.8rem;
    }
    .feedback-meta {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.4rem;
    }
    
    /* Chat window custom CSS wrapper */
    .chat-container {
        height: 380px;
        overflow-y: auto;
        padding-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MOCK DATA ENGINE
# -----------------------------------------------------------------------------
def initialize_mock_data(force=False):
    if "data_initialized" not in st.session_state or force:
        # Define New York Coordinates center (Times Square / Midtown area)
        center_lat, center_lon = 40.7589, -73.9851
        
        # 1. Weather Data Setup
        st.session_state.weather = {
            "condition": "Heavy Rain & Winds",
            "temp": "68°F",
            "humidity": "92%",
            "alert_level": "Orange Warning",
            "impacted_zones": "Zone 2 (Midtown), Zone 4 (FDR Drive & East Side)"
        }
        
        # 2. Traffic Incidents Dataset
        incidents_data = [
            {
                "incident_id": "INC-1001",
                "zone": "Zone 2 (Midtown)",
                "location": "Broadway & W 42nd St",
                "latitude": 40.7580,
                "longitude": -73.9855,
                "type": "Accident (2-Vehicle Collision)",
                "severity": "High",
                "status": "Active",
                "avg_delay": 45,
                "lines_affected": "Bus 104, Bus 42",
                "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=22)).strftime("%H:%M:%S")
            },
            {
                "incident_id": "INC-1002",
                "zone": "Zone 4 (East Side)",
                "location": "FDR Drive Southbound near E 34th St",
                "latitude": 40.7420,
                "longitude": -73.9710,
                "type": "Severe Flash Flooding",
                "severity": "High",
                "status": "Active",
                "avg_delay": 60,
                "lines_affected": "Route M15, Route M34",
                "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=35)).strftime("%H:%M:%S")
            },
            {
                "incident_id": "INC-1003",
                "zone": "Zone 2 (Midtown)",
                "location": "8th Ave & W 34th St",
                "latitude": 40.7525,
                "longitude": -73.9935,
                "type": "Severe Gridlock (Intersection blocked)",
                "severity": "Medium",
                "status": "Active",
                "avg_delay": 25,
                "lines_affected": "Route M20, Route M34-SBS",
                "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime("%H:%M:%S")
            },
            {
                "incident_id": "INC-1004",
                "zone": "Zone 3 (Upper East)",
                "location": "5th Ave & E 57th St",
                "latitude": 40.7625,
                "longitude": -73.9735,
                "type": "Smart Signal Controller Offline",
                "severity": "Medium",
                "status": "Active",
                "avg_delay": 18,
                "lines_affected": "Route M1, Route M2, Route M4",
                "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=8)).strftime("%H:%M:%S")
            },
            {
                "incident_id": "INC-1005",
                "zone": "Zone 1 (Downtown)",
                "location": "Lexington Ave & E 42nd St",
                "latitude": 40.7510,
                "longitude": -73.9750,
                "type": "Construction Lane Blockage",
                "severity": "Low",
                "status": "Active",
                "avg_delay": 12,
                "lines_affected": "Route M101, Route M102",
                "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=45)).strftime("%H:%M:%S")
            }
        ]
        st.session_state.incidents = pd.DataFrame(incidents_data)
        
        # 3. GTFS Transit Delays Dataset (Simulated Bus fleet status)
        bus_data = [
            {"route_id": "M15-SBS", "vehicle_id": "V-5510", "zone": "Zone 4 (East Side)", "delay_mins": 38, "passenger_load": 88, "latitude": 40.7435, "longitude": -73.9720, "status": "Delayed"},
            {"route_id": "M34-SBS", "vehicle_id": "V-2201", "zone": "Zone 2 (Midtown)", "delay_mins": 25, "passenger_load": 92, "latitude": 40.7515, "longitude": -73.9910, "status": "Delayed"},
            {"route_id": "M104", "vehicle_id": "V-1204", "zone": "Zone 2 (Midtown)", "delay_mins": 42, "passenger_load": 75, "latitude": 40.7590, "longitude": -73.9860, "status": "Delayed"},
            {"route_id": "M42", "vehicle_id": "V-8809", "zone": "Zone 2 (Midtown)", "delay_mins": 45, "passenger_load": 95, "latitude": 40.7570, "longitude": -73.9835, "status": "Delayed"},
            {"route_id": "M2", "vehicle_id": "V-3011", "zone": "Zone 3 (Upper East)", "delay_mins": 15, "passenger_load": 64, "latitude": 40.7640, "longitude": -73.9715, "status": "Delayed"},
            {"route_id": "M102", "vehicle_id": "V-4015", "zone": "Zone 1 (Downtown)", "delay_mins": 8, "passenger_load": 40, "latitude": 40.7495, "longitude": -73.9775, "status": "On Schedule"},
            {"route_id": "M15-SBS", "vehicle_id": "V-5522", "zone": "Zone 4 (East Side)", "delay_mins": 55, "passenger_load": 82, "latitude": 40.7395, "longitude": -73.9740, "status": "Delayed"},
            {"route_id": "M1", "vehicle_id": "V-3304", "zone": "Zone 3 (Upper East)", "delay_mins": 5, "passenger_load": 30, "latitude": 40.7610, "longitude": -73.9755, "status": "On Schedule"},
            {"route_id": "M55", "vehicle_id": "V-6602", "zone": "Zone 1 (Downtown)", "delay_mins": 2, "passenger_load": 22, "latitude": 40.7120, "longitude": -74.0080, "status": "On Schedule"}
        ]
        st.session_state.bus_delays = pd.DataFrame(bus_data)
        
        # 4. Citizen Feedback & Incident Logs (AlloyDB Semantic mock representation)
        feedback_data = [
            {
                "log_id": "LOG-3091",
                "text": "FDR southbound is completely flooded under the bridge! Water is rising rapidly, cars are screeching to stop.",
                "zone": "Zone 4 (East Side)",
                "sentiment": "Negative",
                "timestamp": "00:15:30"
            },
            {
                "log_id": "LOG-3092",
                "text": "Bus M15 is super delayed. Trapped near 34th St for 25 mins without moving an inch. Tell driver to reroute please!",
                "zone": "Zone 4 (East Side)",
                "sentiment": "Negative",
                "timestamp": "00:20:12"
            },
            {
                "log_id": "LOG-3093",
                "text": "The traffic signals at 5th Ave and 57th St are completely dark. Drivers are gridlocking each other. Total mess.",
                "zone": "Zone 3 (Upper East)",
                "sentiment": "Negative",
                "timestamp": "00:22:45"
            },
            {
                "log_id": "LOG-3094",
                "text": "Fender bender at Times Square intersection (Broadway/42). Blocking two lanes, police haven't arrived yet.",
                "zone": "Zone 2 (Midtown)",
                "sentiment": "Negative",
                "timestamp": "00:24:10"
            },
            {
                "log_id": "LOG-3095",
                "text": "Bus 42 is full capacity, had to wait for the next one in heavy rain. Need extra bus dispatches on 42nd St corridor.",
                "zone": "Zone 2 (Midtown)",
                "sentiment": "Negative",
                "timestamp": "00:26:05"
            },
            {
                "log_id": "LOG-3096",
                "text": "Nice run down Broadway below 30th St, clean flow and no major rain issues.",
                "zone": "Zone 1 (Downtown)",
                "sentiment": "Positive",
                "timestamp": "00:27:18"
            }
        ]
        st.session_state.citizen_feedback = pd.DataFrame(feedback_data)
        
        # 5. Global Logs & History
        st.session_state.action_plans = []
        st.session_state.chat_history = []
        st.session_state.active_intervention_plan = None
        st.session_state.data_initialized = True

initialize_mock_data()

# -----------------------------------------------------------------------------
# SIDEBAR CONFIGURATION (Filters & API Keys)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 Platform Configuration")
    
    # Live Gemini API Key Input Setup
    user_gemini_key = st.text_input(
        "Enter Gemini API Key (Optional)",
        type="password",
        help="If not provided, the dashboard operates using an offline local simulated AI fallback engine.",
        value=os.environ.get("GEMINI_API_KEY", "")
    )
    if user_gemini_key:
        st.session_state.user_gemini_key = user_gemini_key
    
    st.markdown("---")
    st.markdown("### 📊 Operational Filters")
    
    # Zone selector
    zones_list = ["All Zones"] + list(st.session_state.incidents["zone"].unique())
    selected_zone = st.selectbox("Select Mobility Zone", zones_list)
    
    # Severity selector
    severity_list = ["All Levels", "High", "Medium", "Low"]
    selected_severity = st.selectbox("Incident Severity Level", severity_list)
    
    # Status selector
    status_list = ["All Statuses", "Active", "Resolving", "Resolved"]
    selected_status = st.selectbox("Incident Action Status", status_list)
    
    st.markdown("---")
    # Simulation trigger button
    if st.button("🔄 Force Simulator Grid Refresh"):
        # Shift coords slightly & increase random delays to simulate real-time updates
        inc_df = st.session_state.incidents.copy()
        inc_df["avg_delay"] = inc_df["avg_delay"].apply(lambda x: max(5, x + random.randint(-5, 8)))
        
        bus_df = st.session_state.bus_delays.copy()
        bus_df["delay_mins"] = bus_df["delay_mins"].apply(lambda x: max(0, x + random.randint(-4, 6)))
        bus_df["latitude"] = bus_df["latitude"] + np.random.normal(0, 0.0005, len(bus_df))
        bus_df["longitude"] = bus_df["longitude"] + np.random.normal(0, 0.0005, len(bus_df))
        
        st.session_state.incidents = inc_df
        st.session_state.bus_delays = bus_df
        
        # Log to chat
        st.session_state.chat_history.append({
            "role": "system",
            "content": f"🔄 Simulator Grid Refresh triggered at {datetime.datetime.now().strftime('%H:%M:%S')}. Coordinate offsets updated, transit metrics recalculated."
        })
        st.rerun()

    st.markdown("<div style='font-size: 0.8rem; color: #64748b; text-align: center; margin-top: 2rem;'>APAAC Cohort 2 Hackathon Project<br>Powered by Vertex AI & Gemini</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FILTER LOGIC
# -----------------------------------------------------------------------------
filtered_incidents = st.session_state.incidents.copy()
filtered_buses = st.session_state.bus_delays.copy()
filtered_feedback = st.session_state.citizen_feedback.copy()

if selected_zone != "All Zones":
    filtered_incidents = filtered_incidents[filtered_incidents["zone"] == selected_zone]
    filtered_buses = filtered_buses[filtered_buses["zone"] == selected_zone]
    filtered_feedback = filtered_feedback[filtered_feedback["zone"] == selected_zone]

if selected_severity != "All Levels":
    filtered_incidents = filtered_incidents[filtered_incidents["severity"] == selected_severity]

if selected_status != "All Statuses":
    filtered_incidents = filtered_incidents[filtered_incidents["status"] == selected_status]

# -----------------------------------------------------------------------------
# UI TOP TITLE BANNER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="title-container">
    <div class="title-main">AuraFlow Platform</div>
    <div class="title-subtitle">Real-Time Decision Intelligence & Predictive Orchestration for Urban Mobility</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# KPI METRICS ROW (Premium styling)
# -----------------------------------------------------------------------------
active_incident_count = len(st.session_state.incidents[st.session_state.incidents["status"] == "Active"])
resolving_incident_count = len(st.session_state.incidents[st.session_state.incidents["status"] == "Resolving"])
avg_bus_delay = int(st.session_state.bus_delays["delay_mins"].mean())
avg_occupancy = int(st.session_state.bus_delays["passenger_load"].mean())

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card red">
        <div class="kpi-label">Active Jams & Incidents</div>
        <div class="kpi-value">
            <span class="kpi-status-dot pulse" style="background-color: #ef4444;"></span>{active_incident_count}
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8;">High Severity: {len(st.session_state.incidents[(st.session_state.incidents["severity"] == "High") & (st.session_state.incidents["status"] == "Active")])}</div>
    </div>
    <div class="kpi-card orange">
        <div class="kpi-label">Average Transit Delay</div>
        <div class="kpi-value">{avg_bus_delay}m</div>
        <div style="font-size: 0.8rem; color: #94a3b8;">Peak delay: {st.session_state.bus_delays['delay_mins'].max()}m ({st.session_state.bus_delays.loc[st.session_state.bus_delays['delay_mins'].idxmax(), 'route_id']})</div>
    </div>
    <div class="kpi-card green">
        <div class="kpi-label">Resolving Plans</div>
        <div class="kpi-value">
            <span class="kpi-status-dot" style="background-color: #10b981;"></span>{resolving_incident_count}
        </div>
        <div style="font-size: 0.8rem; color: #94a3b8;">Deployments actively running</div>
    </div>
    <div class="kpi-card blue">
        <div class="kpi-label">Weather Risk Assessment</div>
        <div class="kpi-value">{st.session_state.weather['alert_level']}</div>
        <div style="font-size: 0.8rem; color: #94a3b8;">Condition: {st.session_state.weather['condition']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN SPLIT GRID LAYOUT
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([1.1, 0.9])

# -----------------------------------------------------------------------------
# LEFT COLUMN: GIS MAP & DATA TABLES
# -----------------------------------------------------------------------------
with col_left:
    st.markdown("### 🗺️ Real-Time Spatial Traffic Overlay")
    
    # Create pydeck layers
    # Incidents Layer (Red points for high severity, orange for medium, yellow for low)
    incidents_map_df = filtered_incidents.copy()
    if not incidents_map_df.empty:
        # Assign color mapping
        def assign_color(row):
            if row["severity"] == "High":
                return [239, 68, 68, 200]  # Red
            elif row["severity"] == "Medium":
                return [249, 115, 22, 200]  # Orange
            else:
                return [59, 130, 246, 200]  # Blue
        incidents_map_df["color"] = incidents_map_df.apply(assign_color, axis=1)
        incidents_map_df["radius"] = incidents_map_df["avg_delay"] * 3
    else:
        # fallback dummy empty rows
        incidents_map_df = pd.DataFrame(columns=["latitude", "longitude", "color", "radius", "location", "type", "severity"])

    # Bus locations layer (Green/yellow circles depending on delays)
    buses_map_df = filtered_buses.copy()
    if not buses_map_df.empty:
        def assign_bus_color(row):
            if row["delay_mins"] > 30:
                return [234, 179, 8, 180]  # Yellow/warning
            else:
                return [16, 185, 129, 180]  # Green
        buses_map_df["color"] = buses_map_df.apply(assign_bus_color, axis=1)
        buses_map_df["radius"] = 40  # Constant radius
    else:
        buses_map_df = pd.DataFrame(columns=["latitude", "longitude", "color", "radius", "route_id", "delay_mins"])

    # Setup Pydeck Map
    view_state = pdk.ViewState(
        latitude=40.7525,
        longitude=-73.9835,
        zoom=12.8,
        pitch=45
    )
    
    layers = []
    
    # Add active buses layer
    if not buses_map_df.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=buses_map_df,
                get_position="[longitude, latitude]",
                get_color="color",
                get_radius="radius",
                pickable=True,
                id="buses-layer"
            )
        )
        
    # Add incident points layer
    if not incidents_map_df.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=incidents_map_df,
                get_position="[longitude, latitude]",
                get_color="color",
                get_radius="radius",
                pickable=True,
                id="incidents-layer"
            )
        )
        
    r_map = pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v9",
        initial_view_state=view_state,
        layers=layers,
        tooltip={
            "html": "<b>Location:</b> {location}{route_id}<br/>"
                    "<b>Type/Info:</b> {type}{status}<br/>"
                    "<b>Delay:</b> {avg_delay}{delay_mins} mins",
            "style": {"backgroundColor": "#1e293b", "color": "white", "fontSize": "12px", "zIndex": 1000}
        }
    )
    st.pydeck_chart(r_map, use_container_width=True)
    
    # Structured Data Tables Tabbed layout
    tab_incidents, tab_buses, tab_feedback = st.tabs([
        "⚠️ Active Incidents Grid", 
        "🚌 GTFS Bus Telemetry", 
        "💬 Citizen Feedback Feed"
    ])
    
    with tab_incidents:
        if filtered_incidents.empty:
            st.info("No active incidents matching current filters.")
        else:
            # Custom styled dataframe for display
            styled_inc = filtered_incidents[["incident_id", "location", "type", "severity", "status", "avg_delay", "lines_affected"]].copy()
            st.dataframe(
                styled_inc.style.map(
                    lambda v: "color: #ef4444; font-weight: bold;" if v == "High" else 
                              ("color: #f97316;" if v == "Medium" else ("color: #3b82f6;" if v == "Low" else "")),
                    subset=["severity"]
                ).map(
                    lambda v: "color: #ef4444; background-color: rgba(239, 68, 68, 0.1);" if v == "Active" else
                              ("color: #f97316; background-color: rgba(249, 115, 22, 0.1);" if v == "Resolving" else
                               "color: #10b981; background-color: rgba(16, 185, 129, 0.1);"),
                    subset=["status"]
                ),
                use_container_width=True,
                hide_index=True
            )
            
    with tab_buses:
        if filtered_buses.empty:
            st.info("No bus routes found matching current filters.")
        else:
            styled_buses = filtered_buses[["route_id", "vehicle_id", "zone", "delay_mins", "passenger_load", "status"]].copy()
            st.dataframe(
                styled_buses.style.bar(
                    subset=["passenger_load"], 
                    color="rgba(168, 85, 247, 0.35)", 
                    vmin=0, 
                    vmax=100
                ).map(
                    lambda v: "color: #ef4444; font-weight: bold;" if v > 30 else "color: #10b981;",
                    subset=["delay_mins"]
                ),
                use_container_width=True,
                hide_index=True
            )
            
    with tab_feedback:
        if filtered_feedback.empty:
            st.info("No citizen feedback logged for this zone.")
        else:
            for _, row in filtered_feedback.iterrows():
                sentiment_color = "#ef4444" if row["sentiment"] == "Negative" else "#10b981"
                st.markdown(f"""
                <div class="feedback-card">
                    <div style="font-size: 0.9rem; color: #f1f5f9; font-weight: 500;">{row['text']}</div>
                    <div class="feedback-meta">
                        <span>📍 {row['zone']}</span>
                        <span style="color: {sentiment_color}; font-weight: 600;">Sentiment: {row['sentiment']}</span>
                        <span>⏰ {row['timestamp']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# RIGHT COLUMN: GEMINI CO-PILOT CHAT & AUTONOMOUS DECISION ENGINE
# -----------------------------------------------------------------------------
with col_right:
    # Check if a valid API key is available
    gemini_key = st.session_state.get("user_gemini_key", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    is_live_ai = len(gemini_key) > 5
    
    # ------------------
    # Section A: AI Co-Pilot Chat Box
    # ------------------
    st.markdown("### 💬 AuraFlow Decision Co-Pilot")
    
    # Mode indicator banner
    if is_live_ai:
        st.markdown("<div style='background-color: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 6px; padding: 0.5rem 1rem; font-size: 0.85rem; margin-bottom: 1rem;'>🟢 <b>Live Gemini Mode Active</b>. Connected to Gemini 2.5 on Vertex AI.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color: rgba(249, 115, 22, 0.1); color: #f97316; border: 1px solid rgba(249, 115, 22, 0.3); border-radius: 6px; padding: 0.5rem 1rem; font-size: 0.85rem; margin-bottom: 1rem;'>⚠️ <b>Simulated AI Fallback Mode</b>. Enter a Gemini API Key in the sidebar to activate real-time AI.</div>", unsafe_allow_html=True)
    
    # Setup chat display container
    chat_container = st.container(height=260)
    with chat_container:
        # Display greeting if history is empty
        if not st.session_state.chat_history:
            st.markdown("""
            <div style='color: #94a3b8; font-size: 0.9rem;'>
                <b>System Initialized.</b> Hello Mobility Controller. Ask me questions like:
                <ul>
                    <li><i>"Which intersections need emergency routing right now?"</i></li>
                    <li><i>"Is the heavy rain alert affecting Route M15?"</i></li>
                    <li><i>"Provide a summary of Zone 4 incidents."</i></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(msg["content"])
            elif msg["role"] == "assistant":
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])
            elif msg["role"] == "system":
                st.markdown(f"<div style='font-size: 0.75rem; color: #64748b; font-style: italic; border-left: 2px solid #64748b; padding-left: 8px; margin: 4px 0;'>{msg['content']}</div>", unsafe_allow_html=True)

    # Chat query handler function
    def run_ai_query(user_query):
        # Format the system status as text context to feed to AI
        current_incidents_text = st.session_state.incidents.to_markdown(index=False)
        current_buses_text = st.session_state.bus_delays.to_markdown(index=False)
        weather_text = json.dumps(st.session_state.weather, indent=2)
        citizen_feedback_text = st.session_state.citizen_feedback.to_markdown(index=False)
        
        system_instruction = f"""You are the AuraFlow AI Urban Mobility Co-Pilot, an elite Google Cloud Decision Intelligence Assistant.
Analyze the following active city transit datasets to answer the controller's query.
Be direct, metrics-driven, and highly practical.

CURRENT ACCIDENT & CONGESTION INCIDENTS:
{current_incidents_text}

GTFS TRANSIT DELAYS TELEMETRY:
{current_buses_text}

WEATHER ADVISORY:
{weather_text}

CITIZEN LOGS FEED (AlloyDB Vector Data):
{citizen_feedback_text}
"""
        
        if is_live_ai:
            try:
                # Initialize Google GenAI client
                client = genai.Client(api_key=gemini_key)
                
                # Request response from gemini-2.5-flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_query,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )
                )
                return response.text
            except Exception as e:
                # Fallback to local matching in case of API failure
                st.session_state.chat_history.append({
                    "role": "system",
                    "content": f"⚠️ Gemini API Request failed. Activating local inference engine fallback. Error: {str(e)}"
                })
        
        # ------------------
        # OFFLINE SIMULATED AI RULE-BASED MATCHING ENGINE
        # ------------------
        query_lower = user_query.lower()
        
        if "emergency" in query_lower or "routing" in query_lower or "accident" in query_lower or "intersection" in query_lower:
            high_sev = st.session_state.incidents[st.session_state.incidents["severity"] == "High"]
            if not high_sev.empty:
                response_text = "### 🚨 Active High-Severity Routing Anomalies:\n\n"
                for _, row in high_sev.iterrows():
                    response_text += f"- **{row['location']}** ({row['zone']}): `{row['type']}`. Currently delaying traffic by **{row['avg_delay']} minutes**. Affects routes: **{row['lines_affected']}**.\n"
                response_text += "\n**Recommendation:** Trigger an autonomous routing plan immediately to detour buses M15, M34, and M104 around W 42nd St and FDR Drive."
            else:
                response_text = "All major accidents and high-severity gridlocks are currently resolved or marked as resolving."
                
        elif "rain" in query_lower or "weather" in query_lower or "flood" in query_lower or "m15" in query_lower:
            m15_delays = st.session_state.bus_delays[st.session_state.bus_delays["route_id"] == "M15-SBS"]
            avg_m15_delay = int(m15_delays["delay_mins"].mean()) if not m15_delays.empty else 0
            response_text = f"### 🌧️ Weather Advisory & Transit Impact:\n\n" \
                            f"- **Advisory:** {st.session_state.weather['alert_level']} for `{st.session_state.weather['condition']}`.\n" \
                            f"- **Impact Zone:** {st.session_state.weather['impacted_zones']}.\n" \
                            f"- **Route M15-SBS Impact:** Currently experiencing severe delays averaging **{avg_m15_delay} minutes** due to flash flooding on FDR Drive near E 34th St.\n\n" \
                            f"**Operational Advice:** Advise dispatch to reroute M15-SBS away from FDR Drive onto 2nd Avenue."
                            
        elif "zone" in query_lower:
            matched_zone = None
            for i in range(1, 6):
                if f"zone {i}" in query_lower:
                    matched_zone = f"Zone {i}"
                    break
            
            if matched_zone:
                zone_incidents = st.session_state.incidents[st.session_state.incidents["zone"].str.contains(matched_zone)]
                zone_buses = st.session_state.bus_delays[st.session_state.bus_delays["zone"].str.contains(matched_zone)]
                
                response_text = f"### 📊 Mobility Summary for {matched_zone}:\n\n"
                if not zone_incidents.empty:
                    response_text += "**Active Incidents:**\n"
                    for _, row in zone_incidents.iterrows():
                        response_text += f"- `{row['incident_id']}`: {row['type']} at {row['location']} ({row['status']}) - Delay: {row['avg_delay']}m\n"
                else:
                    response_text += "- No active incidents reported in this zone.\n"
                    
                if not zone_buses.empty:
                    response_text += "\n**Bus Statuses:**\n"
                    for _, row in zone_buses.iterrows():
                        response_text += f"- Route {row['route_id']} (Bus {row['vehicle_id']}): Delay: {row['delay_mins']}m, Occupancy: {row['passenger_load']}%\n"
            else:
                response_text = "Please specify which zone (e.g., 'Zone 2' or 'Zone 4') you'd like a summary for."
                
        else:
            response_text = "### 🧠 AuraFlow AI Core Analysis:\n\n" \
                            f"- **System Status:** Currently tracking **{active_incident_count} active congestion incidents** across 5 zones.\n" \
                            f"- **Transit Delay:** Average delays are at **{avg_bus_delay} minutes**, primarily driven by weather conditions ({st.session_state.weather['condition']}).\n" \
                            f"- **Suggested Action:** Generate an autonomous Intervention Plan using the controller panel below to resolve active Broadway & FDR Drive incidents."
                            
        return response_text

    # Read chat input
    user_query = st.chat_input("Enter mobility query...")
    if user_query:
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # Get AI response
        ai_response = run_ai_query(user_query)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        st.rerun()

    st.markdown("---")
    
    # ------------------
    # Section B: Autonomous Intervention Center
    # ------------------
    st.markdown("### ⚡ Predictive Orchestration & Intervention Center")
    
    # Trigger button to analyze active anomalies and draft a plan
    if st.button("🧠 Generate Autonomous Intervention Plan", type="primary", use_container_width=True):
        # We target high-severity active incidents
        target_incidents = st.session_state.incidents[
            (st.session_state.incidents["status"] == "Active") & 
            (st.session_state.incidents["severity"] == "High")
        ]
        
        if target_incidents.empty:
            # Fall back to medium severity if no high severity incidents are active
            target_incidents = st.session_state.incidents[
                (st.session_state.incidents["status"] == "Active") & 
                (st.session_state.incidents["severity"] == "Medium")
            ]
            
        if target_incidents.empty:
            st.session_state.active_intervention_plan = {
                "title": "AuraFlow Dispatch Advisory",
                "incidents": [],
                "body": "### ✅ Platform Status Normal\nNo critical high or medium severity incidents requiring active intervention at this time."
            }
        else:
            incident_ids = ", ".join(target_incidents["incident_id"].tolist())
            
            if is_live_ai:
                try:
                    client = genai.Client(api_key=gemini_key)
                    prompt = f"""Analyze the active mobility incidents ({incident_ids}) and output a highly detailed, actionable Intervention Plan.
Format it using clean, executive-level markdown with these sections:
1. **⚠️ CRITICAL ANOMALIES IDENTIFIED**: Summary of the issues.
2. **🚓 EMERGENCY DISPATCH & ROUTING**: Specify precise coordinate directions.
3. **🚦 SMART TRAFFIC SIGNAL CONTROLS**: Propose signal timing adjustments in seconds.
4. **🚌 TRANSIT REROUTING SCHEMES**: Detailed detour route plans for impacted lines.
5. **📢 PUBLIC SAFETY BROADCAST**: Write a SMS/Alert push notification message.

ACTIVE DATA:
{target_incidents.to_json(orient='records')}
"""
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.3
                        )
                    )
                    
                    st.session_state.active_intervention_plan = {
                        "title": f"Autonomous Mobility Intervention Plan: {incident_ids}",
                        "incidents": target_incidents["incident_id"].tolist(),
                        "body": response.text
                    }
                except Exception as e:
                    is_live_ai = False  # Trigger fallback due to failure
                    
            if not is_live_ai:
                # Generate a premium structured offline plan
                plan_md = f"""### ⚠️ CRITICAL ANOMALIES IDENTIFIED ({incident_ids})
- **Broadway & W 42nd St (INC-1001)**: High-severity 2-vehicle crash gridlocking Zone 2.
- **FDR Drive Southbound near E 34th St (INC-1002)**: High-severity flooding due to storm drain backup.

### 🚓 EMERGENCY DISPATCH & ROUTING
- **INC-1001**: Dispatch Traffic unit T-14 and Tow Truck Unit to coordinates `(40.7580, -73.9855)`.
- **INC-1002**: Dispatch Municipal Flooding Response Crew to pump out pooling water at coordinate `(40.7420, -73.9710)`.

### 🚦 SMART TRAFFIC SIGNAL CONTROLS
- **Zone 2 Corridor**: Extend green light phase on **7th Ave and W 42nd St** by **45 seconds** to clear vehicle backlog.
- **East Side Corridor**: Increase green-light timing on **2nd Avenue** by **30 seconds** to absorb FDR detoured volume.

### 🚌 TRANSIT REROUTING SCHEMES
- **Bus M104 / M42**: Detour W 42nd St lines via W 44th St to avoid the Broadway accident intersection.
- **Bus M15-SBS**: Reroute Southbound M15 service off FDR Drive at E 42nd St; run southbound via 2nd Avenue.

### 📢 PUBLIC SAFETY BROADCAST
- **Cell-Broadcast SMS**: *"AuraFlow Warning: High delays in Midtown due to accident on Broadway & W 42nd St, and severe flooding on FDR Drive Southbound at E 34th St. Alternate routes advised."*
"""
                st.session_state.active_intervention_plan = {
                    "title": f"Autonomous Mobility Intervention Plan: {incident_ids}",
                    "incidents": target_incidents["incident_id"].tolist(),
                    "body": plan_md
                }
        st.rerun()

    # Display drafted intervention plan with Approve & Reject buttons
    if st.session_state.active_intervention_plan:
        plan = st.session_state.active_intervention_plan
        
        st.markdown(f"""
        <div class="plan-box">
            <div class="plan-title">🧠 {plan['title']}</div>
            <div style="font-size: 0.9rem; color: #cbd5e1; line-height: 1.5;">
                {plan['body']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if plan.get("incidents"):
            # Provide Human-In-The-Loop Approval Action Items
            col_approve, col_reject = st.columns(2)
            
            with col_approve:
                if st.button("✅ Approve & Deploy Plan", type="primary", use_container_width=True):
                    # Update status of target incidents to "Resolving"
                    inc_ids = plan["incidents"]
                    inc_df = st.session_state.incidents.copy()
                    inc_df.loc[inc_df["incident_id"].isin(inc_ids), "status"] = "Resolving"
                    inc_df.loc[inc_df["incident_id"].isin(inc_ids), "avg_delay"] = inc_df.loc[inc_df["incident_id"].isin(inc_ids), "avg_delay"] // 2
                    st.session_state.incidents = inc_df
                    
                    # Update affected buses delay reduction
                    bus_df = st.session_state.bus_delays.copy()
                    for inc_id in inc_ids:
                        affected_lines = st.session_state.incidents.loc[st.session_state.incidents["incident_id"] == inc_id, "lines_affected"].values[0]
                        lines_list = [line.strip() for line in affected_lines.split(",")]
                        for line in lines_list:
                            # Search for matches in route_id
                            bus_df.loc[bus_df["route_id"].str.contains(line.replace("Bus ", "").replace("Route ", "")), "delay_mins"] = \
                                bus_df.loc[bus_df["route_id"].str.contains(line.replace("Bus ", "").replace("Route ", "")), "delay_mins"] // 2
                    st.session_state.bus_delays = bus_df
                    
                    # Log event to chat history
                    st.session_state.chat_history.append({
                        "role": "system",
                        "content": f"🚨 Intervention Approved: Command dispatched signal adjustments & detours for {', '.join(inc_ids)}. Traffic signal changes propagated. Delays reducing."
                    })
                    
                    st.session_state.active_intervention_plan = None
                    st.toast("🚀 Action Plan Deployed! Coordinates dispatched to field crews.", icon="✅")
                    st.rerun()
                    
            with col_reject:
                if st.button("❌ Dismiss Plan", use_container_width=True):
                    st.session_state.active_intervention_plan = None
                    st.toast("Plan dismissed by controller.", icon="ℹ️")
                    st.rerun()
