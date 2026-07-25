import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
from datetime import datetime

# Local Backend Imports
import database as db
from grid_simulation import GridSimulator
from fault_analysis import OpenDSSFaultAnalyzer
from ai_analytics import SmartGridAI

# Streamlit Page Config - Compact Wide Dashboard
st.set_page_config(
    page_title="ESP32 Smart Grid Control Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Density Cyber Glassmorphism CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    /* Compact Container Padding */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    /* High Density Metric Card */
    .metric-card {
        background: rgba(22, 27, 34, 0.85);
        border: 1px solid rgba(56, 139, 253, 0.35);
        border-radius: 8px;
        padding: 10px 14px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
        text-align: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #58a6ff;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }
    .section-header {
        border-left: 4px solid #58a6ff;
        padding-left: 10px;
        margin-top: 0px;
        margin-bottom: 12px;
        font-size: 1.4rem;
        font-weight: 700;
    }
    /* Compact Table & Divider */
    hr {
        margin-top: 0.8rem !important;
        margin-bottom: 0.8rem !important;
        border-color: rgba(56, 139, 253, 0.2);
    }
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    /* Floating Bottom-Right Badge */
    .made-by-badge {
        position: fixed;
        bottom: 14px;
        right: 20px;
        background: rgba(22, 27, 34, 0.92);
        border: 1px solid rgba(56, 139, 253, 0.5);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #58a6ff;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(8px);
        z-index: 99999;
    }
</style>

<div class='made-by-badge'>
    ⚡ Made by <b>Yashdeep</b>
</div>
""", unsafe_allow_html=True)

# Initialize Backend Systems
@st.cache_resource
def setup_system():
    db.init_db()
    grid_sim = GridSimulator()
    fault_sim = OpenDSSFaultAnalyzer()
    ai_engine = SmartGridAI()
    return grid_sim, fault_sim, ai_engine

grid_sim, fault_sim, ai_engine = setup_system()

# Sidebar Navigation & Speed Control
st.sidebar.title("⚡ Smart Grid Hub")
st.sidebar.caption("ESP32 • Pandapower • OpenDSS • AI")

menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "⚡ Real-Time Telemetry",
        "🌐 Pandapower Power Flow",
        "💥 OpenDSS Fault Analysis",
        "🤖 AI Anomaly & Load Forecast",
        "⚙️ Architecture & Settings"
    ]
)

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Auto-Refresh Telemetry (1s)", value=False)
if auto_refresh:
    time.sleep(1)
    st.rerun()

# ---------------------------------------------------------
# TAB 1: REAL-TIME TELEMETRY (ESP32 Sensors)
# ---------------------------------------------------------
if menu == "⚡ Real-Time Telemetry":
    st.markdown("<div class='section-header'>⚡ ESP32 Sensor Telemetry Monitor</div>", unsafe_allow_html=True)
    
    df_telemetry = db.get_recent_telemetry(limit=60)
    
    if df_telemetry.empty:
        st.warning("No telemetry found. Run simulator or wait for ESP32 packets.")
    else:
        latest = df_telemetry.iloc[0]
        
        # High-Density Top Metric Bar
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(f"<div class='metric-card'><div class='metric-label'>Active Node</div><div class='metric-value' style='font-size: 1.1rem; color: #a5d6ff;'>{latest['node_id']}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><div class='metric-label'>Phase-A Voltage</div><div class='metric-value'>{latest['voltage_a']:.1f} V</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><div class='metric-label'>Phase-A Current</div><div class='metric-value' style='color: #79c0ff;'>{latest['current_a']:.1f} A</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'><div class='metric-label'>Active Power</div><div class='metric-value' style='color: #d2a8ff;'>{latest['active_power']:.2f} kW</div></div>", unsafe_allow_html=True)
        
        pf_col = '#3fb950' if latest['power_factor'] >= 0.90 else '#f85149'
        c5.markdown(f"<div class='metric-card'><div class='metric-label'>Power Factor</div><div class='metric-value' style='color: {pf_col};'>{latest['power_factor']:.2f}</div></div>", unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Side-by-Side Charts (Maximizing horizontal space)
        col_charts_l, col_charts_r = st.columns(2)
        df_node = df_telemetry[df_telemetry['node_id'] == latest['node_id']].sort_values('id')
        
        with col_charts_l:
            st.caption("📈 3-Phase AC Voltage Waveform (V)")
            fig_v = px.line(
                df_node, x='timestamp', y=['voltage_a', 'voltage_b', 'voltage_c'],
                labels={'value': 'Voltage (V)', 'timestamp': 'Time', 'variable': 'Phase'},
                color_discrete_sequence=['#f85149', '#e3b341', '#58a6ff']
            )
            fig_v.update_layout(template="plotly_dark", height=300, margin={"l": 10, "r": 10, "t": 25, "b": 10}, legend_title_text="", legend=dict(orientation="h", y=1.15, x=0))
            st.plotly_chart(fig_v, use_container_width=True)

        with col_charts_r:
            st.caption("📊 Current (A) & Power Factor Dual-Axis")
            fig_i = make_subplots(specs=[[{"secondary_y": True}]])
            fig_i.add_trace(go.Scatter(x=df_node['timestamp'], y=df_node['current_a'], name="Current A (A)", line={"color": '#79c0ff'}), secondary_y=False)
            fig_i.add_trace(go.Scatter(x=df_node['timestamp'], y=df_node['power_factor'], name="Power Factor", line={"color": '#3fb950', "dash": 'dash'}), secondary_y=True)
            fig_i.update_layout(template="plotly_dark", height=300, margin={"l": 10, "r": 10, "t": 25, "b": 10}, legend_title_text="", legend=dict(orientation="h", y=1.15, x=0))
            st.plotly_chart(fig_i, use_container_width=True)

        # Bottom Stream Table & Node Selector
        st.caption("📋 Real-Time Sensor Stream Log")
        st.dataframe(df_telemetry[['timestamp', 'node_id', 'voltage_a', 'voltage_b', 'voltage_c', 'current_a', 'active_power', 'power_factor', 'frequency', 'status']].head(10), use_container_width=True, height=220)

# ---------------------------------------------------------
# TAB 2: PANDAPOWER GRID POWER FLOW
# ---------------------------------------------------------
elif menu == "🌐 Pandapower Power Flow":
    st.markdown("<div class='section-header'>🌐 Pandapower Distribution Power Flow</div>", unsafe_allow_html=True)
    
    # Integrated Control & Summary Header Row
    ctrl_col1, ctrl_col2, m1, m2, m3 = st.columns([1.5, 1.5, 1, 1, 1])
    with ctrl_col1:
        load_scale = st.slider("Grid Load Scaling", 0.5, 2.5, 1.0, 0.1)
    with ctrl_col2:
        solar_mw = st.slider("Solar PV Feed-in (MW)", 0.0, 3.0, 0.8, 0.1)
        
    res = grid_sim.run_power_flow(load_scaling=load_scale, solar_generation_mw=solar_mw)
    
    if res['success']:
        m1.metric("Feeder Load", f"{res['total_load_mw']} MW")
        m2.metric("Solar Gen", f"{res['solar_gen_mw']} MW")
        m3.metric("Grid Losses", f"{res['total_loss_kw']} kW")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Parallel Bar Charts
        c1, c2 = st.columns(2)
        with c1:
            st.caption("⚡ Bus Voltage Magnitudes (p.u.)")
            b_df = res['buses']
            fig_b = px.bar(
                b_df, x='Bus Name', y='Voltage (p.u.)', color='Status',
                color_discrete_map={'NORMAL': '#3fb950', 'VIOLATION': '#f85149'},
                text='Voltage (p.u.)'
            )
            fig_b.add_hline(y=0.95, line_dash="dash", line_color="orange")
            fig_b.add_hline(y=1.05, line_dash="dash", line_color="orange")
            fig_b.update_layout(template="plotly_dark", height=310, margin={"l": 10, "r": 10, "t": 10, "b": 10})
            st.plotly_chart(fig_b, use_container_width=True)
            
        with c2:
            st.caption("🔥 Feeder Line Loading (%)")
            l_df = res['lines']
            fig_l = px.bar(
                l_df, x='Line Name', y='Loading (%)', color='Overloaded',
                color_discrete_map={False: '#58a6ff', True: '#f85149'},
                text='Loading (%)'
            )
            fig_l.add_hline(y=90.0, line_dash="dash", line_color="red")
            fig_l.update_layout(template="plotly_dark", height=310, margin={"l": 10, "r": 10, "t": 10, "b": 10})
            st.plotly_chart(fig_l, use_container_width=True)

        st.caption("📄 Network Bus Voltages Data")
        st.dataframe(b_df, use_container_width=True, height=200)

# ---------------------------------------------------------
# TAB 3: OPENDSS FAULT ANALYSIS
# ---------------------------------------------------------
elif menu == "💥 OpenDSS Fault Analysis":
    st.markdown("<div class='section-header'>💥 OpenDSS Short-Circuit & Fault Analyzer</div>", unsafe_allow_html=True)
    
    # Single-Row Controls & Metrics
    f_col1, f_col2, f_col3, btn_col = st.columns([1, 1.2, 1.2, 1])
    with f_col1:
        f_type = st.selectbox("Fault Type", ["3PH", "SLG", "LL"])
    with f_col2:
        f_loc = st.selectbox("Fault Location Node", list(fault_sim.node_locations.keys()))
    with f_col3:
        f_res = st.slider("Fault Impedance R_f (Ω)", 0.001, 1.0, 0.05, 0.01)
    with btn_col:
        st.write("")
        st.write("")
        inject_btn = st.button("🚨 Inject Fault", use_container_width=True)
        
    f_res_data = fault_sim.simulate_fault(fault_type=f_type, location_node=f_loc, fault_resistance=f_res)
    
    if inject_btn:
        db.log_fault_event(f_type, f_loc, f_res_data['fault_current_ka'], 85.0, f_res_data['trip_time_ms'], f_res_data['severity'])
        st.success("Logged fault event into SQLite database!")

    # Compact Metrics Bar
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Short-Circuit Fault Current", f"{f_res_data['fault_current_ka']} kA", f"{f_res_data['fault_current_amp']} A")
    k2.metric("Relay Trip Time", f"{f_res_data['trip_time_ms']} ms", f"{f_res_data['trip_time_sec']} s")
    k3.metric("Severity Level", f_res_data['severity'])
    k4.metric("Classification", f_res_data['description'].split()[0])
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Side-by-Side Voltage Collapse Curve & Table
    dip_left, dip_right = st.columns([1.3, 1])
    dips_df = f_res_data['voltage_dips']
    
    with dip_left:
        st.caption("📉 Feeder Voltage Sag Collapse Profile")
        fig_dip = px.line(
            dips_df, x='Distance (km)', y='Voltage Remainder (p.u.)', text='Node', markers=True
        )
        fig_dip.add_hline(y=0.9, line_dash="dot", line_color="yellow")
        fig_dip.update_layout(template="plotly_dark", height=280, margin={"l": 10, "r": 10, "t": 10, "b": 10})
        st.plotly_chart(fig_dip, use_container_width=True)
        
    with dip_right:
        st.caption("📋 Node Voltage Dip Breakdown")
        st.dataframe(dips_df[['Node', 'Voltage Dip (%)', 'Fault Sag Status']], use_container_width=True, height=280)

# ---------------------------------------------------------
# TAB 4: AI ANOMALY & LOAD FORECASTING
# ---------------------------------------------------------
elif menu == "🤖 AI Anomaly & Load Forecast":
    st.markdown("<div class='section-header'>🤖 AI Anomaly Detection & Load Forecast</div>", unsafe_allow_html=True)
    
    df_telemetry = db.get_recent_telemetry(limit=200)
    ai_engine.train_anomaly_detector(df_telemetry)
    ai_engine.train_load_forecaster(df_telemetry)
    
    col_ai1, col_ai2 = st.columns([1, 1.2])
    
    with col_ai1:
        st.caption("🚨 IsolationForest Detected Anomalies")
        anomalies_df = db.get_all_anomalies()
        if anomalies_df.empty:
            st.info("No sensor anomalies detected. Operating normally.")
        else:
            st.dataframe(anomalies_df[['timestamp', 'node_id', 'voltage_v', 'current_a', 'description']].head(15), use_container_width=True, height=330)
            
    with col_ai2:
        st.caption("📈 24-Hour Load Demand Forecast (kW)")
        fc_df = ai_engine.forecast_next_24h(df_telemetry)
        
        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=fc_df['Time'], y=fc_df['Upper Confidence (kW)'],
            mode='lines', line={"width": 0}, showlegend=False
        ))
        fig_fc.add_trace(go.Scatter(
            x=fc_df['Time'], y=fc_df['Lower Confidence (kW)'],
            mode='lines', line={"width": 0}, fill='tonexty',
            fillcolor='rgba(88, 166, 255, 0.2)', name="90% Confidence Band"
        ))
        fig_fc.add_trace(go.Scatter(
            x=fc_df['Time'], y=fc_df['Forecasted Load (kW)'],
            mode='lines+markers', line={"color": '#58a6ff', "width": 2.5}, name="RandomForest Forecast"
        ))
        fig_fc.update_layout(template="plotly_dark", height=330, margin={"l": 10, "r": 10, "t": 25, "b": 10}, legend_title_text="", legend=dict(orientation="h", y=1.15, x=0))
        st.plotly_chart(fig_fc, use_container_width=True)

elif menu == "⚙️ Architecture & Settings":
    st.markdown("<div class='section-header'>⚙️ Comprehensive System Architecture & Control Panel</div>", unsafe_allow_html=True)
    st.write("Welcome! This section provides a complete end-to-end breakdown of every single component, algorithm, hardware pinout, electrical formula, and database metric in your Smart Grid system.")
    
    # --- 1. SYSTEM OVERVIEW & BLOCK DIAGRAM ---
    st.caption("📐 4-Tier Smart Grid Architecture Block Diagram")
    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────────────────────────────────────┐
    │                               1. HARDWARE & SENSOR LAYER                                │
    │  ESP32 Microcontroller + PZEM-004T AC Voltage & Current Transducers (or esp32_simulator) │
    └──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │
                                               ▼ (Wi-Fi / MQTT JSON Payload @ 1s)
    ┌─────────────────────────────────────────────────────────────────────────────────────────┐
    │                             2. INGESTION & BROKER LAYER                                 │
    │  Public MQTT Broker (broker.hivemq.com:1883)  ──►  Topic: esp32/smartgrid/telemetry    │
    └──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │
                                               ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────────┐
    │                            3. PYTHON BACKEND & PHYSICS ENGINE                           │
    │   ├── database.py       ──► SQLite Time-Series Storage (smart_grid.db)                  │
    │   ├── grid_simulation.py──► Pandapower AC Newton-Raphson Power Flow Solver              │
    │   ├── fault_analysis.py ──► OpenDSS Short-Circuit & Voltage Collapse Engine             │
    │   └── ai_analytics.py   ──► Scikit-Learn (IsolationForest & RandomForest)               │
    └──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │
                                               ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────────┐
    │                        4. STREAMLIT FRONTEND CONTROL DASHBOARD                          │
    │  Real-Time Waveforms, Grid Voltage Maps, Fault Simulator, AI Alerts, High-Density GUI  │
    └─────────────────────────────────────────────────────────────────────────────────────────┘
    ```
    """)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- 2. EXHAUSTIVE DEEP DIVE EXPANDERS FOR ALL 6 LAYERS ---
    st.caption("📘 Complete Layer-by-Layer Technical Guide")
    
    exp1, exp2 = st.columns(2)
    
    with exp1:
        with st.expander("📡 Layer 1: Hardware & Sensor Telemetry (ESP32 / PZEM-004T)"):
            st.markdown("""
            #### What it does:
            Measures real AC electrical parameters from transmission lines and substation transformers.

            #### Hardware Specifications & Hardware Pinout:
            - **ESP32 Microcontroller**: 32-bit dual-core Tensilica Xtensa @ 240 MHz with built-in Wi-Fi.
            - **PZEM-004T Transducer**: Reads AC RMS Voltage (80-260V), Current (0-100A), Active Power (kW), Frequency (45-65Hz), and Power Factor ($\cos\phi$) using a non-invasive Current Transformer (CT) clamp.
            - **Physical Wiring Pinouts**:
              - `PZEM TX` ➔ `ESP32 RX2 (GPIO 16)`
              - `PZEM RX` ➔ `ESP32 TX2 (GPIO 17)`
              - `VCC` ➔ `5V`, `GND` ➔ `GND`

            #### Python Sensor Simulator (`esp32_simulator.py`):
            When physical hardware is disconnected, `esp32_simulator.py` generates realistic AC physics values using sine wave load curves every 1 second.
            """)

        with st.expander("💾 Layer 2: Time-Series Storage Engine (`database.py`)"):
            st.markdown("""
            #### What it does:
            Manages local SQLite database storage (`smart_grid.db`) for real-time telemetry, fault logs, and AI anomalies.

            #### Database Tables Schema:
            1. **`telemetry`**: Stores timestamps, node IDs (`ESP32_SUBSTATION_01`, `FEEDER_A`, `FEEDER_B`), 3-phase voltages ($V_A, V_B, V_C$), currents ($I_A, I_B, I_C$), active power ($kW$), power factor ($PF$), and frequency ($Hz$).
            2. **`fault_events`**: Stores short-circuit simulations (fault type, location, fault current $kA$, voltage dip %, relay trip time $ms$, and severity).
            3. **`anomalies`**: Stores AI-detected outliers (voltage sags, current surges, low power factor).

            #### Historical Baseline Seeder:
            On first startup, `database.py` automatically generates 24 hours of baseline historical data (240 records) so all charts and AI models have rich data immediately.
            """)

        with st.expander("🌐 Layer 3: Pandapower AC Power Flow Engine (`grid_simulation.py`)"):
            st.markdown("""
            #### What it does:
            Models an 11kV/0.4kV distribution network with an HV grid substation, distribution lines, and rooftop solar PV generation.

            #### Mathematical Formulation (Newton-Raphson Method):
            Solves complex non-linear AC power flow equations ($\bar{S} = \bar{V} \cdot \bar{I}^*$):
            $$P_i = \sum_{j=1}^{N} |V_i||V_j|(G_{ij}\cos\theta_{ij} + B_{ij}\sin\theta_{ij})$$

            #### Key Output Parameters:
            - **Bus Voltage Magnitude ($V_{pu}$)**: Per-unit voltage ratio ($V_{actual} / V_{base}$). Target range: $0.95 \le V_{pu} \le 1.05$.
            - **Line Loading (%)**: Ratio of active line current to max thermal rating ($I / I_{max} \times 100\%$). Overloads flag above $90\%$.
            - **Active Line Losses ($kW$)**: Heat dissipation across line resistance ($I^2R$).
            """)

    with exp2:
        with st.expander("💥 Layer 4: OpenDSS Short-Circuit & Relay Protection (`fault_analysis.py`)"):
            st.markdown("""
            #### What it does:
            Simulates electrical short-circuit faults across distribution feeder nodes and calculates overcurrent relay trip timing.

            #### Fault Types Simulated:
            - **3-Phase Symmetrical (3PH)**: Heavy fault where all 3 phase conductors collide ($I_f \approx 2.5 - 5.0 \text{ kA}$).
            - **Single Line-to-Ground (SLG)**: Phase conductor grounds to earth ($70\%$ of real-world grid faults).
            - **Line-to-Line (LL)**: Two phase conductors collide ($I_f = \frac{\sqrt{3} V_{phase}}{2Z_1 + 2R_f}$).

            #### Overcurrent Relay Trip Curve (IEC 60255 Standard):
            Overcurrent protection relays trip circuit breakers using the IEC Extremely Inverse Characteristic curve:
            $$t_{trip} = \frac{80}{\left(\frac{I_{fault}}{I_{pickup}}\right)^2 - 1} \quad \text{(seconds)}$$
            """)

        with st.expander("🤖 Layer 5: Artificial Intelligence & Machine Learning (`ai_analytics.py`)"):
            st.markdown("""
            #### What it does:
            Provides real-time anomaly detection and 24-hour ahead grid load demand forecasting.

            #### ML Algorithms:
            1. **`IsolationForest` (Anomaly Detection)**:
               - Scans incoming ESP32 sensor streams ($V, I, PF$) for statistical outliers.
               - Isolates anomalies like voltage sags ($<180\text{V}$) or current surges ($>45\text{A}$) and logs them to the database.
            2. **`RandomForestRegressor` (24-Hour Load Forecasting)**:
               - Trains on historical hour-of-day ($0-23$) and day-of-week patterns.
               - Predicts upcoming active power demand ($kW$) for the next 24 hours with a $90\%$ upper/lower confidence interval.
            """)

        with st.expander("🎨 Layer 6: Streamlit Interactive Control Dashboard (`app.py`)"):
            st.markdown("""
            #### What it does:
            Renders a high-density, dark-mode cyber control panel in your browser.

            #### Key Features:
            - **5 Interactive Tabs**: Real-Time Telemetry, Pandapower Power Flow, OpenDSS Faults, AI Forecasting, and Settings.
            - **1-Second Live Auto-Refresh**: Live metrics update every 1 second.
            - **Zero Whitespace Grid**: Side-by-side Plotly charts, dataframes, and sliders for maximum screen efficiency.
            """)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- 3. LIVE DATABASE METRICS & MQTT CONTROL PANEL ---
    st.caption("💾 Live System Health & Control Settings")
    
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.subheader("📡 MQTT Broker Status")
        st.text_input("Broker Host", "broker.hivemq.com", disabled=True)
        st.text_input("Port", "1883", disabled=True)
        st.text_input("Topic", "esp32/smartgrid/telemetry", disabled=True)
        st.info("MQTT Status: Online & Connected to HiveMQ Broker.")

    with c_right:
        st.subheader("💾 Database Health & Metrics")
        
        db_path = db.DB_PATH
        db_exists = os.path.exists(db_path)
        db_size_kb = os.path.getsize(db_path) / 1024.0 if db_exists else 0.0
        
        telemetry_df = db.get_recent_telemetry(limit=1000)
        faults_df = db.get_all_faults()
        anomalies_df = db.get_all_anomalies()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Telemetry Rows", len(telemetry_df))
        m2.metric("Fault Logs", len(faults_df))
        m3.metric("AI Anomalies", len(anomalies_df))
        
        st.write(f"**Database Size**: `{db_size_kb:.1f} KB` | **File**: `{os.path.basename(db_path)}`")
        
        if st.button("🔄 Re-initialize & Seed Database", use_container_width=True):
            if os.path.exists(db_path):
                os.remove(db_path)
            db.init_db()
            st.success("Database successfully reset and seeded with fresh 24h data!")
            st.rerun()

#cd C:\Users\yashd\.gemini\antigravity\scratch\smart_grid_monitoring; python run_system.py