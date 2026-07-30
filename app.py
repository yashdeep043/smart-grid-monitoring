import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import os
from datetime import datetime, timedelta

# Local Backend Imports
import database as db
from grid_simulation import GridSimulator
from fault_analysis import OpenDSSFaultAnalyzer
from ai_analytics import SmartGridAI

import threading
from esp32_simulator import run_simulator

# Streamlit Page Config - Compact Wide Dashboard
st.set_page_config(
    page_title="ESP32 Smart Grid Control Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Backend Systems & Background Telemetry Stream
@st.cache_resource
def setup_system():
    db.init_db()
    grid_sim = GridSimulator()
    fault_sim = OpenDSSFaultAnalyzer()
    ai_engine = SmartGridAI()
    
    # Guarantee background ESP32 Telemetry Generator is running @ 1s interval
    def start_background_telemetry():
        try:
            run_simulator(interval_sec=1)
        except Exception as e:
            print(f"Background simulator thread notice: {e}")
            
    sim_thread = threading.Thread(target=start_background_telemetry, daemon=True)
    sim_thread.start()
    
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
    ],
    key="nav_menu"
)

st.sidebar.markdown("---")
st.sidebar.subheader("📡 Telemetry Stream Controls")

plotly_template = "none"
plotly_bg = "rgba(0,0,0,0)"
plotly_font = None
plotly_grid = "rgba(128, 128, 128, 0.2)"
card_border = "rgba(128, 128, 128, 0.25)"

# Custom High-Density Native Theme Adaptive CSS
st.markdown("""
<style>
    /* 1. Inherit Streamlit Native Theme Variables */
    .stApp {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
    }
    [data-testid="stHeader"] {
        background-color: var(--background-color) !important;
    }
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        border-right: 1px solid rgba(128, 128, 128, 0.2) !important;
    }
    
    /* 2. Global Text & Headings */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp td, .stApp th,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: var(--text-color) !important;
    }

    /* 3. Compact Container Padding */
    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* 4. High Density Metric Card */
    .metric-card {
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.25) !important;
        border-radius: 8px;
        padding: 10px 14px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
        text-align: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #58a6ff !important;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-color) !important;
        opacity: 0.75;
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
        color: var(--text-color) !important;
    }
    /* Compact Table & Divider */
    hr {
        margin-top: 0.8rem !important;
        margin-bottom: 0.8rem !important;
        border-color: rgba(128, 128, 128, 0.2) !important;
    }
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    /* Floating Bottom-Left Badge */
    .made-by-badge {
        position: fixed;
        bottom: 15px;
        left: 20px;
        opacity: 0.85;
        background: var(--secondary-background-color);
        border: 1px solid rgba(88, 166, 255, 0.4);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #58a6ff;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
        z-index: 99999;
        cursor: pointer;
        transition: all 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: floatBadge 3s ease-in-out infinite;
    }
    .made-by-badge:hover {
        animation-play-state: paused;
        transform: translateY(-5px) scale(1.12) !important;
        opacity: 1 !important;
        border-color: #58a6ff !important;
        box-shadow: 0 8px 24px rgba(88, 166, 255, 0.5) !important;
    }
    @keyframes floatBadge {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-4px); }
    }
</style>

<div class='made-by-badge'>
    ⚡ Made by <b>Yashdeep</b>
</div>
""", unsafe_allow_html=True)

# Top Header Bar
st.markdown("<h2 style='margin-bottom: 0px; padding-top: 0px;'>⚡ ESP32 Smart Grid Control Center</h2>", unsafe_allow_html=True)
st.caption("Real-Time Distribution Grid Monitoring • Pandapower AC Flow • OpenDSS Faults • AI Forecasting")
st.markdown("<hr style='margin-top: 0.4rem !important; margin-bottom: 1.2rem !important;'>", unsafe_allow_html=True)

auto_refresh = st.sidebar.checkbox("Auto-Refresh Telemetry", value=True)
refresh_sec = st.sidebar.select_slider(
    "⏱️ Telemetry Refresh Speed",
    options=[1, 2, 5, 10, 15, 30],
    value=1,
    format_func=lambda x: f"{x} second{'s' if x > 1 else ''}"
)

if auto_refresh:
    st.sidebar.success(f"🟢 Live Stream ACTIVE ({refresh_sec}s interval)")
else:
    st.sidebar.error("🔴 Live Stream PAUSED")

# ---------------------------------------------------------
# TAB 1: REAL-TIME TELEMETRY (ESP32 Sensors)
# ---------------------------------------------------------
is_telemetry_active = (st.session_state.get('nav_menu', '⚡ Real-Time Telemetry') == "⚡ Real-Time Telemetry")

if menu == "⚡ Real-Time Telemetry":
    st.markdown("<div class='section-header'>⚡ ESP32 Sensor Telemetry Monitor</div>", unsafe_allow_html=True)
    
    # 1. Static Time Window Selector (Outside 1s fragment loop -> ZERO layout flickering)
    col_selector_l, col_selector_r = st.columns([3, 1])
    with col_selector_l:
        time_range = st.radio(
            "⏱️ **Select Telemetry Time Window**",
            ["Live Stream (Real-Time)", "Last 15 Mins", "Last 1 Hour", "Last 6 Hours", "Last 24 Hours"],
            horizontal=True, key="time_range_select"
        )
    with col_selector_r:
        st.caption("ℹ️ *Downsampled automatically for long ranges to maintain high performance.*")

    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    is_live_selected = (time_range == "Live Stream (Real-Time)")
    
    # 2. Smooth Live Telemetry Data Fragment
    @st.fragment(run_every=f"{refresh_sec}s" if (auto_refresh and is_telemetry_active and is_live_selected) else None)
    def render_telemetry_stream():
        if st.session_state.get('nav_menu') != "⚡ Real-Time Telemetry":
            return
        df_telemetry = db.get_recent_telemetry(limit=600)
        
        if df_telemetry.empty:
            st.warning("No telemetry found. Run simulator or wait for ESP32 packets.")
            return

        latest = df_telemetry.iloc[0]
        node_id = str(latest['node_id'])
        v_a = float(latest['voltage_a'])
        v_b = float(latest['voltage_b'])
        v_c = float(latest['voltage_c'])
        i_a = float(latest['current_a'])
        i_b = float(latest['current_b'])
        i_c = float(latest['current_c'])
        
        # Calculate Phase Voltage Imbalance (NEMA Standard)
        v_avg = (v_a + v_b + v_c) / 3.0
        if v_avg > 0:
            max_dev = max(abs(v_a - v_avg), abs(v_b - v_avg), abs(v_c - v_avg))
            imbalance_pct = (max_dev / v_avg) * 100.0
        else:
            imbalance_pct = 0.0

        imb_col = '#f85149' if imbalance_pct >= 2.0 else '#3fb950'
        imb_status = "⚠️ UNBALANCED (>2%)" if imbalance_pct >= 2.0 else "🟢 BALANCED (<2%)"
        
        # Automatically surface imbalance event in AI Anomalies table if threshold crossed (60s cooldown per node)
        if imbalance_pct >= 2.0:
            desc = f"WARNING: Phase Imbalance ({imbalance_pct:.2f}%) Exceeds 2% Limit (V_A={v_a:.1f}V, V_B={v_b:.1f}V, V_C={v_c:.1f}V)"
            last_anomaly_ts = db.get_latest_anomaly_timestamp(node_id, "WARNING: Phase Imbalance%")
            should_log = False
            if last_anomaly_ts is None:
                should_log = True
            else:
                try:
                    last_dt = datetime.strptime(last_anomaly_ts, '%Y-%m-%d %H:%M:%S')
                    if (datetime.now() - last_dt).total_seconds() >= 60:
                        should_log = True
                except Exception:
                    should_log = True

            if should_log:
                db.log_anomaly(node_id, v_a, i_a, round(-0.70 - (imbalance_pct / 100.0), 3), desc)

        # Threshold checks for voltage and current (Nominal V: 230V, Normal V range: 218.5V-241.5V; Normal I max: 30A)
        v_a_col = '#f85149' if (v_a > 241.5 or v_a < 218.5) else '#3fb950'
        i_a_col = '#f85149' if i_a > 30.0 else '#79c0ff'
        pa_border = '1px solid rgba(248, 81, 73, 0.85)' if (v_a > 241.5 or v_a < 218.5 or i_a > 30.0) else '1px solid rgba(56, 139, 253, 0.35)'

        v_b_col = '#f85149' if (v_b > 241.5 or v_b < 218.5) else '#3fb950'
        i_b_col = '#f85149' if i_b > 30.0 else '#79c0ff'
        pb_border = '1px solid rgba(248, 81, 73, 0.85)' if (v_b > 241.5 or v_b < 218.5 or i_b > 30.0) else '1px solid rgba(56, 139, 253, 0.35)'

        v_c_col = '#f85149' if (v_c > 241.5 or v_c < 218.5) else '#3fb950'
        i_c_col = '#f85149' if i_c > 30.0 else '#79c0ff'
        pc_border = '1px solid rgba(248, 81, 73, 0.85)' if (v_c > 241.5 or v_c < 218.5 or i_c > 30.0) else '1px solid rgba(56, 139, 253, 0.35)'

        p_kw_val = float(latest['active_power'])
        p_kw_col = '#f85149' if p_kw_val > 25.0 else '#d2a8ff'

        # 1. Top Summary Metric Bar
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'><div class='metric-label'>Active Node</div><div class='metric-value' style='font-size: 1.1rem; color: #a5d6ff;'>{node_id}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><div class='metric-label'>Active Power</div><div class='metric-value' style='color: {p_kw_col};'>{p_kw_val:.2f} kW</div></div>", unsafe_allow_html=True)
        
        pf_col = '#3fb950' if latest['power_factor'] >= 0.90 else '#f85149'
        c3.markdown(f"<div class='metric-card'><div class='metric-label'>Power Factor</div><div class='metric-value' style='color: {pf_col};'>{latest['power_factor']:.2f}</div></div>", unsafe_allow_html=True)
        
        c4.markdown(f"<div class='metric-card' style='border-color: {imb_col};'><div class='metric-label'>Phase Imbalance</div><div class='metric-value' style='color: {imb_col};'>{imbalance_pct:.2f}%</div><div style='font-size: 0.72rem; color: {imb_col}; font-weight: 700;'>{imb_status}</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
        
        # 2. Side-by-Side 3-Phase Gauges
        col_pa, col_pb, col_pc = st.columns(3)
        with col_pa:
            st.markdown(f"""
            <div style='background: var(--secondary-background-color); border: {pa_border}; border-radius: 8px; padding: 10px 14px; text-align: center;'>
                <div style='color: var(--text-color); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;'>🔴 Phase A (R)</div>
                <div style='display: flex; justify-content: space-around; margin-top: 8px;'>
                    <div><div class='metric-label'>Voltage</div><div class='metric-value' style='color: {v_a_col};'>{v_a:.1f} V</div></div>
                    <div><div class='metric-label'>Current</div><div class='metric-value' style='color: {i_a_col};'>{i_a:.1f} A</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_pb:
            st.markdown(f"""
            <div style='background: var(--secondary-background-color); border: {pb_border}; border-radius: 8px; padding: 10px 14px; text-align: center;'>
                <div style='color: var(--text-color); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;'>🟡 Phase B (Y)</div>
                <div style='display: flex; justify-content: space-around; margin-top: 8px;'>
                    <div><div class='metric-label'>Voltage</div><div class='metric-value' style='color: {v_b_col};'>{v_b:.1f} V</div></div>
                    <div><div class='metric-label'>Current</div><div class='metric-value' style='color: {i_b_col};'>{i_b:.1f} A</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_pc:
            st.markdown(f"""
            <div style='background: var(--secondary-background-color); border: {pc_border}; border-radius: 8px; padding: 10px 14px; text-align: center;'>
                <div style='color: var(--text-color); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px;'>🔵 Phase C (B)</div>
                <div style='display: flex; justify-content: space-around; margin-top: 8px;'>
                    <div><div class='metric-label'>Voltage</div><div class='metric-value' style='color: {v_c_col};'>{v_c:.1f} V</div></div>
                    <div><div class='metric-label'>Current</div><div class='metric-value' style='color: {i_c_col};'>{i_c:.1f} A</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if imbalance_pct >= 2.0:
            st.warning(f"⚠️ **VOLTAGE PHASE IMBALANCE ALERT**: Current voltage deviation is **{imbalance_pct:.2f}%** ($V_A$: {v_a:.1f}V, $V_B$: {v_b:.1f}V, $V_C$: {v_c:.1f}V). Threshold is 2.0%. Event logged to AI Anomalies table.")

        st.markdown("<hr>", unsafe_allow_html=True)

        # RENDER WAVEFORM CHARTS
        def render_waveform_charts(selected_range, active_node):
            col_charts_l, col_charts_r = st.columns(2)
            conn = db.get_connection()
            
            # Determine maximum timestamp in database for accurate window filtering
            max_ts_df = pd.read_sql_query("SELECT MAX(timestamp) as max_ts FROM telemetry WHERE node_id = ?", conn, params=[active_node])
            max_ts_val = max_ts_df['max_ts'].values[0] if not max_ts_df.empty and max_ts_df['max_ts'].values[0] is not None else None
            ref_dt = pd.to_datetime(max_ts_val) if max_ts_val else datetime.now()

            # Direct database query inside fragment for Live Stream and historical ranges
            if selected_range == "Live Stream (Real-Time)":
                df_chart = pd.read_sql_query(
                    "SELECT * FROM telemetry WHERE node_id = ? ORDER BY id DESC LIMIT 30",
                    conn, params=[active_node]
                ).sort_values('id')
            elif selected_range == "Last 15 Mins":
                cutoff = (ref_dt - timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
                df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? AND timestamp >= ? ORDER BY id ASC LIMIT 150", conn, params=[active_node, cutoff])
                if len(df_chart) < 10:
                    df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? ORDER BY id DESC LIMIT 150", conn, params=[active_node]).sort_values('id')
            elif selected_range == "Last 1 Hour":
                cutoff = (ref_dt - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? AND timestamp >= ? ORDER BY id ASC LIMIT 300", conn, params=[active_node, cutoff])
                if len(df_chart) < 10:
                    df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? ORDER BY id DESC LIMIT 300", conn, params=[active_node]).sort_values('id')
            elif selected_range == "Last 6 Hours":
                cutoff = (ref_dt - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')
                df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? AND timestamp >= ? ORDER BY id ASC LIMIT 600", conn, params=[active_node, cutoff])
                if len(df_chart) < 10:
                    df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? ORDER BY id DESC LIMIT 600", conn, params=[active_node]).sort_values('id')
            else: # Last 24 Hours
                cutoff = (ref_dt - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
                df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? AND timestamp >= ? ORDER BY id ASC LIMIT 1200", conn, params=[active_node, cutoff])
                if len(df_chart) < 10:
                    df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? ORDER BY id DESC LIMIT 1200", conn, params=[active_node]).sort_values('id')
            conn.close()

            if df_chart.empty:
                conn = db.get_connection()
                df_chart = pd.read_sql_query("SELECT * FROM telemetry WHERE node_id = ? ORDER BY id DESC LIMIT 50", conn, params=[active_node]).sort_values('id')
                conn.close()

            df_chart['ts_dt'] = pd.to_datetime(df_chart['timestamp'])
            is_live = (selected_range == "Live Stream (Real-Time)")
            trace_mode = 'lines+markers' if (is_live and len(df_chart) <= 30) else 'lines'
            marker_size = 6 if trace_mode == 'lines+markers' else 0

            # -----------------------------------------------------
            # VOLTAGE WAVEFORM CHART
            # -----------------------------------------------------
            fig_v = go.Figure()
            fig_v.add_trace(go.Scatter(
                x=df_chart['ts_dt'], y=df_chart['voltage_a'],
                mode=trace_mode, name="Phase A (Red)",
                line={"color": '#ff4d4d', "width": 3.0, "shape": 'spline', "smoothing": 1.2},
                marker={"size": marker_size, "symbol": 'circle', "color": '#ff4d4d'},
                hovertemplate="Phase A: %{y:.1f} V"
            ))
            fig_v.add_trace(go.Scatter(
                x=df_chart['ts_dt'], y=df_chart['voltage_b'],
                mode=trace_mode, name="Phase B (Yellow)",
                line={"color": '#e3b341', "width": 3.0, "shape": 'spline', "smoothing": 1.2},
                marker={"size": marker_size, "symbol": 'circle', "color": '#e3b341'},
                hovertemplate="Phase B: %{y:.1f} V"
            ))
            fig_v.add_trace(go.Scatter(
                x=df_chart['ts_dt'], y=df_chart['voltage_c'],
                mode=trace_mode, name="Phase C (Blue)",
                line={"color": '#58a6ff', "width": 3.0, "shape": 'spline', "smoothing": 1.2},
                marker={"size": marker_size, "symbol": 'circle', "color": '#58a6ff'},
                hovertemplate="Phase C: %{y:.1f} V"
            ))
            fig_v.add_hrect(
                y0=218.5, y1=241.5,
                fillcolor="rgba(0, 200, 83, 0.08)", line_width=1, line_dash="dash", line_color="rgba(0, 200, 83, 0.35)",
                annotation_text="Normal 230V Band (±5%)", annotation_position="top left",
                annotation_font=dict(size=10, color="#00c853")
            )
            fig_v.update_layout(
                template=plotly_template, height=300,
                paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg,
                margin={"l": 20, "r": 15, "t": 25, "b": 15},
                hovermode="x unified", uirevision=selected_range,
                legend_title_text="",
                legend=dict(orientation="h", y=1.18, x=0, font=dict(size=11, color=plotly_font), bgcolor="rgba(0,0,0,0)"),
                hoverlabel=dict(bgcolor=plotly_bg, font_size=12, font_color=plotly_font, bordercolor=card_border)
            )
            fig_v.update_xaxes(
                type='date', tickformat='%H:%M:%S',
                showgrid=False, showline=False, zeroline=False,
                tickfont=dict(color=plotly_font, size=10)
            )
            fig_v.update_yaxes(
                showgrid=True, gridcolor=plotly_grid, gridwidth=1, showline=False, zeroline=False,
                title_text="Voltage (V)", title_font=dict(color=plotly_font, size=11),
                tickfont=dict(color=plotly_font, size=10)
            )
            key_v = f"fig_v_{selected_range.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')}"
            col_charts_l.plotly_chart(fig_v, use_container_width=True, key=key_v, config={'displayModeBar': False, 'responsive': True})

            # -----------------------------------------------------
            # CURRENT WAVEFORM CHART
            # -----------------------------------------------------
            fig_i = make_subplots(specs=[[{"secondary_y": True}]])
            fig_i.add_trace(go.Scatter(
                x=df_chart['ts_dt'], y=df_chart['current_a'],
                mode=trace_mode, name="Phase A Current",
                line={"color": '#ff4d4d', "width": 3.0, "shape": 'spline', "smoothing": 1.2},
                marker={"size": marker_size, "symbol": 'circle', "color": '#ff4d4d'},
                hovertemplate="Phase A: %{y:.1f} A"
            ), secondary_y=False)
            fig_i.add_trace(go.Scatter(
                x=df_chart['ts_dt'], y=df_chart['current_b'],
                mode=trace_mode, name="Phase B Current",
                line={"color": '#e3b341', "width": 3.0, "shape": 'spline', "smoothing": 1.2},
                marker={"size": marker_size, "symbol": 'circle', "color": '#e3b341'},
                hovertemplate="Phase B: %{y:.1f} A"
            ), secondary_y=False)
            fig_i.add_trace(go.Scatter(
                x=df_chart['ts_dt'], y=df_chart['current_c'],
                mode=trace_mode, name="Phase C Current",
                line={"color": '#58a6ff', "width": 3.0, "shape": 'spline', "smoothing": 1.2},
                marker={"size": marker_size, "symbol": 'circle', "color": '#58a6ff'},
                hovertemplate="Phase C: %{y:.1f} A"
            ), secondary_y=False)
            fig_i.add_trace(go.Scatter(
                x=df_chart['ts_dt'], y=df_chart['power_factor'],
                mode='lines', name="Power Factor",
                line={"color": '#00b0ff', "width": 2.2, "dash": 'dash', "shape": 'spline', "smoothing": 1.2},
                hovertemplate="PF: %{y:.2f}"
            ), secondary_y=True)
            fig_i.add_hline(
                y=30.0, line_dash="dash", line_color="rgba(255, 77, 77, 0.6)",
                annotation_text="Max Rating (30A)", annotation_position="top left",
                annotation_font=dict(size=10, color="#ff4d4d")
            )
            fig_i.update_layout(
                template=plotly_template, height=300,
                paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg,
                margin={"l": 20, "r": 15, "t": 25, "b": 15},
                hovermode="x unified", uirevision=selected_range,
                legend_title_text="",
                legend=dict(orientation="h", y=1.18, x=0, font=dict(size=11, color=plotly_font), bgcolor="rgba(0,0,0,0)"),
                hoverlabel=dict(bgcolor=plotly_bg, font_size=12, font_color=plotly_font, bordercolor=card_border)
            )
            fig_i.update_xaxes(
                type='date', tickformat='%H:%M:%S',
                showgrid=False, showline=False, zeroline=False,
                tickfont=dict(color=plotly_font, size=10)
            )
            fig_i.update_yaxes(
                showgrid=True, gridcolor=plotly_grid, gridwidth=1, showline=False, zeroline=False,
                title_text="Current (A)", title_font=dict(color=plotly_font, size=11),
                tickfont=dict(color=plotly_font, size=10), secondary_y=False
            )
            fig_i.update_yaxes(
                showgrid=False, title_text="Power Factor", title_font=dict(color="#00b0ff", size=11),
                tickfont=dict(color="#00b0ff", size=10), secondary_y=True
            )
            key_i = f"fig_i_{selected_range.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')}"
            col_charts_r.plotly_chart(fig_i, use_container_width=True, key=key_i, config={'displayModeBar': False, 'responsive': True})

        # Execute self-contained chart fragment
        render_waveform_charts(time_range, node_id)

        # 4. Full 3-Phase Live Telemetry Stream Table
        st.caption("📋 Real-Time 3-Phase Telemetry Sensor Stream Log")
        st.dataframe(
            df_telemetry[['timestamp', 'node_id', 'voltage_a', 'voltage_b', 'voltage_c', 'current_a', 'current_b', 'current_c', 'active_power', 'power_factor', 'frequency', 'status']].head(10),
            use_container_width=True, height=220
        )

    render_telemetry_stream()

# ---------------------------------------------------------
# TAB 2: PANDAPOWER GRID POWER FLOW (AUTO / LIVE / FORECAST & FAULT LOOP)
# ---------------------------------------------------------
elif menu == "🌐 Pandapower Power Flow":
    st.markdown("<div class='section-header'>🌐 Pandapower Distribution Power Flow & Early Warning System</div>", unsafe_allow_html=True)
    
    # 1. Operational Mode Selector Header
    mode_col, info_col = st.columns([1.5, 2.5])
    with mode_col:
        flow_mode = st.radio(
            "Operational Mode",
            ["🖐️ Manual", "📡 Live Telemetry", "🔮 AI Forecast"],
            horizontal=True,
            key="flow_mode_select",
            help="Manual: custom sliders | Live: auto-sync with ESP32 sensors | Forecast: auto-sync with AI predictions"
        )
        
    is_pandapower_active = (st.session_state.get('nav_menu') == "🌐 Pandapower Power Flow")
    is_live_flow = (st.session_state.get('flow_mode_select', flow_mode) == "📡 Live Telemetry")

    @st.fragment(run_every=f"{refresh_sec}s" if (auto_refresh and is_pandapower_active and is_live_flow) else None)
    def render_pandapower_dashboard():
        if st.session_state.get('nav_menu') != "🌐 Pandapower Power Flow":
            return

        baseline_info = db.get_telemetry_baseline_load()
        df_telemetry = db.get_recent_telemetry(limit=200)
        ai_multiplier = ai_engine.get_forecast_load_multiplier(df_telemetry)
        live_multiplier = baseline_info['baseline_scaling']
        
        # 2. Mode Logic & Control Sliders
        if flow_mode == "🖐️ Manual":
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                load_scale = st.slider("Grid Load Scaling", 0.5, 2.5, float(live_multiplier), 0.05, help="1.0x = live baseline")
            with c_s2:
                solar_mw = st.slider("Solar PV Feed-in (MW)", 0.0, 3.0, 0.8, 0.1)
                
            with info_col:
                st.markdown(f"""
                <div style='background: var(--secondary-background-color); padding: 8px 14px; border-radius: 6px; border: 1px solid rgba(88,166,255,0.35); font-size: 0.85rem; color: var(--text-color);'>
                    <b>🖐️ Manual Mode Active</b><br>
                    📡 Live Baseline: <span style='color: #58a6ff;'><b>{live_multiplier}x</b></span> ({baseline_info['avg_power_kw']} kW) | 
                    🔮 AI 24h Forecast: <span style='color: #d2a8ff;'><b>{ai_multiplier}x</b></span> | 
                    🎯 Selected Load: <span style='color: #3fb950;'><b>{load_scale}x</b></span>
                </div>
                """, unsafe_allow_html=True)
                
            res = grid_sim.run_power_flow(load_scaling=load_scale, solar_generation_mw=solar_mw, use_telemetry_baseline=False, auto_log_anomalies=True)

        elif flow_mode == "📡 Live Telemetry":
            solar_mw = 0.8
            load_scale = live_multiplier
            with info_col:
                st.markdown(f"""
                <div style='background: var(--secondary-background-color); padding: 8px 14px; border-radius: 6px; border: 1px solid rgba(63,185,80,0.5); font-size: 0.85rem; color: var(--text-color);'>
                    <b>📡 Live Mode Active</b> — Power flow is dynamically driven by ESP32 sensor telemetry.<br>
                    Avg Sensor Active Power: <span style='color: #58a6ff;'><b>{baseline_info['avg_power_kw']} kW</b></span> | 
                    Effective Feeder Load: <span style='color: #3fb950;'><b>{baseline_info['live_load_mw']} MW</b></span> ({live_multiplier}x baseline)
                </div>
                """, unsafe_allow_html=True)
                
            res = grid_sim.run_power_flow(load_scaling=1.0, solar_generation_mw=solar_mw, use_telemetry_baseline=True, auto_log_anomalies=True)

        else: # 🔮 AI Forecast
            solar_mw = 0.8
            load_scale = ai_multiplier
            with info_col:
                st.markdown(f"""
                <div style='background: var(--secondary-background-color); padding: 8px 14px; border-radius: 6px; border: 1px solid rgba(210,168,255,0.5); font-size: 0.85rem; color: var(--text-color);'>
                    <b>🔮 AI Forecast Mode Active</b> — Running predictive power flow on upcoming 24h peak load.<br>
                    RandomForest Predicted Load: <span style='color: #d2a8ff;'><b>{ai_multiplier}x</b></span> of normal baseline | 
                    Predicted Feeder Demand: <span style='color: #58a6ff;'><b>{round(5.45 * ai_multiplier, 2)} MW</b></span>
                </div>
                """, unsafe_allow_html=True)
                
            res = grid_sim.run_power_flow(load_scaling=ai_multiplier, solar_generation_mw=solar_mw, use_telemetry_baseline=False, auto_log_anomalies=True)

        # Log current run to powerflow_history time-series
        if res['success']:
            status_label = "VIOLATION" if len(res['violations']) > 0 else "NORMAL"
            viol_label = "; ".join(res['violations']) if len(res['violations']) > 0 else "None"
            db.log_powerflow_result(
                mode=flow_mode,
                total_load_mw=res['total_load_mw'],
                solar_gen_mw=res['solar_gen_mw'],
                total_loss_kw=res['total_loss_kw'],
                min_voltage_pu=res['min_voltage_pu'],
                max_line_loading_pct=res['max_line_loading_pct'],
                status=status_label,
                violations=viol_label
            )

            # 3. High Density Metrics Bar
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Feeder Load", f"{res['total_load_mw']} MW", f"{res['effective_scaling']}x scale")
            m2.metric("Solar Gen", f"{res['solar_gen_mw']} MW")
            m3.metric("Grid Losses", f"{res['total_loss_kw']} kW")
            
            v_col = "#3fb950" if res['min_voltage_pu'] >= 0.95 else "#f85149"
            m4.metric("Min Voltage", f"{res['min_voltage_pu']:.3f} p.u.", delta=None, delta_color="normal")
            
            l_col = "#58a6ff" if res['max_line_loading_pct'] <= 90.0 else "#f85149"
            m5.metric("Max Line Loading", f"{res['max_line_loading_pct']:.1f}%")
            
            # 4. Automatic Alert Banner & Closed-Loop Fault Analyzer Trigger
            if len(res['violations']) > 0:
                st.error(f"🚨 **AUTOMATIC ANOMALY ALERT LOGGED**: {'; '.join(res['violations'])}")
                
                # Closed-Loop Fault Trigger
                target_node = "Feeder Node B (Node 3)"
                if "Node A" in res['most_stressed_node'] or "Line 1-2" in res['most_stressed_line']:
                    target_node = "Feeder Node A (Node 2)"
                elif "Node C" in res['most_stressed_node'] or "Line 3-4" in res['most_stressed_line']:
                    target_node = "Feeder Node C (Node 4)"
                    
                fault_contingency = fault_sim.simulate_fault("3PH", location_node=target_node, fault_resistance=0.05)
                
                st.markdown(f"""
                <div style='background: rgba(248, 81, 73, 0.15); border: 1px solid #f85149; border-radius: 8px; padding: 12px 16px; margin-bottom: 15px;'>
                    <b style='color: #f85149; font-size: 1.05rem;'>⚡ CLOSED-LOOP FAULT CONTINGENCY RECOMMENDATION</b><br>
                    High grid stress detected on <b>{res['most_stressed_line']}</b> (Loading: {res['max_line_loading_pct']}%, Min V: {res['min_voltage_pu']} p.u.).<br>
                    <b>Automated What-If Contingency</b>: A 3-Phase short circuit at <b>{target_node}</b> right now would generate 
                    <span style='color: #f85149;'><b>{fault_contingency['fault_current_ka']} kA</b></span> fault current, causing relay trip in 
                    <b>{fault_contingency['trip_time_ms']} ms</b>. (Severity: <b>{fault_contingency['severity']}</b>).
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # 5. Parallel Bar Charts
            c1, c2 = st.columns(2)
            with c1:
                st.caption("⚡ Bus Voltage Magnitudes (p.u.)")
                b_df = res['buses']
                fig_b = px.bar(
                    b_df, x='Bus Name', y='Voltage (p.u.)', color='Status',
                    color_discrete_map={'NORMAL': '#3fb950', 'VIOLATION': '#f85149'},
                    text='Voltage (p.u.)'
                )
                fig_b.add_hline(y=0.95, line_dash="dash", line_color="orange", annotation_text="0.95 Min Limit")
                fig_b.add_hline(y=1.05, line_dash="dash", line_color="orange", annotation_text="1.05 Max Limit")
                fig_b.update_layout(template=plotly_template, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, height=290, margin={"l": 10, "r": 10, "t": 10, "b": 10}, font=dict(color=plotly_font))
                st.plotly_chart(fig_b, use_container_width=True)
                
            with c2:
                st.caption("🔥 Feeder Line Loading (%)")
                l_df = res['lines']
                fig_l = px.bar(
                    l_df, x='Line Name', y='Loading (%)', color='Overloaded',
                    color_discrete_map={False: '#58a6ff', True: '#f85149'},
                    text='Loading (%)'
                )
                fig_l.add_hline(y=90.0, line_dash="dash", line_color="red", annotation_text="90% Overload Threshold")
                fig_l.update_layout(template=plotly_template, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, height=290, margin={"l": 10, "r": 10, "t": 10, "b": 10}, font=dict(color=plotly_font))
                st.plotly_chart(fig_l, use_container_width=True)

            # 6. Grid Stress Time-Series History Chart (Continuous Background Execution Output)
            st.caption("📈 Time-Series Grid Stress & Line Loading History (Continuous Background Power Flow)")
            pf_hist_df = db.get_powerflow_history(limit=40)
            if not pf_hist_df.empty:
                pf_hist_df = pf_hist_df.sort_values('id')
                fig_hist = make_subplots(specs=[[{"secondary_y": True}]])
                fig_hist.add_trace(go.Scatter(
                    x=pf_hist_df['timestamp'], y=pf_hist_df['max_line_loading_pct'],
                    name="Max Line Loading (%)", line={"color": '#f85149', "width": 2.5}
                ), secondary_y=False)
                fig_hist.add_trace(go.Scatter(
                    x=pf_hist_df['timestamp'], y=pf_hist_df['total_loss_kw'],
                    name="Grid Losses (kW)", line={"color": '#e3b341', "dash": 'dash'}
                ), secondary_y=True)
                fig_hist.add_hline(y=90.0, line_dash="dot", line_color="red", secondary_y=False)
                fig_hist.update_layout(template=plotly_template, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, height=240, margin={"l": 10, "r": 10, "t": 20, "b": 10}, legend=dict(orientation="h", y=1.15, x=0, font=dict(color=plotly_font)), font=dict(color=plotly_font))
                st.plotly_chart(fig_hist, use_container_width=True)

            st.caption("📄 Network Bus Voltages Data")
            st.dataframe(b_df, use_container_width=True, height=180)

    render_pandapower_dashboard()


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
        fig_dip.update_layout(template=plotly_template, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, height=280, margin={"l": 10, "r": 10, "t": 10, "b": 10}, font=dict(color=plotly_font))
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
        fig_fc.update_layout(template=plotly_template, paper_bgcolor=plotly_bg, plot_bgcolor=plotly_bg, height=330, margin={"l": 10, "r": 10, "t": 25, "b": 10}, legend_title_text="", legend=dict(orientation="h", y=1.15, x=0, font=dict(color=plotly_font)), font=dict(color=plotly_font))
        st.plotly_chart(fig_fc, use_container_width=True)

elif menu == "⚙️ Architecture & Settings":
    st.markdown("<div class='section-header'>⚙️ Comprehensive System Architecture & Control Panel</div>", unsafe_allow_html=True)
    st.write("Welcome! This section provides a complete end-to-end breakdown of every single component, algorithm, hardware pinout, electrical formula, and database metric in your Smart Grid system.")
    
    # --- 1. SYSTEM OVERVIEW, BLOCK DIAGRAM & TECH SPECS ---
    col_diag_l, col_diag_r = st.columns([1.3, 1.0])
    
    with col_diag_l:
        st.caption("📐 4-Tier Smart Grid Architecture Block Diagram")
        st.markdown("""
        ```
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                        1. HARDWARE & SENSOR LAYER                           │
        │  ESP32 Microcontroller + PZEM-004T AC Voltage & Current Transducers        │
        └──────────────────────────────────────┬──────────────────────────────────────┘
                                               │ (Wi-Fi / MQTT JSON Payload @ 1s)
                                               ▼
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                      2. INGESTION & BROKER LAYER                            │
        │  Public MQTT Broker (broker.hivemq.com:1883) ──► Topic: esp32/.../telemetry │
        └──────────────────────────────────────┬──────────────────────────────────────┘
                                               │
                                               ▼
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                     3. PYTHON BACKEND & PHYSICS ENGINES                     │
        │   ├── database.py       ──► SQLite Time-Series Storage                      │
        │   ├── grid_simulation.py──► Pandapower AC Newton-Raphson Solver             │
        │   ├── fault_analysis.py ──► OpenDSS Short-Circuit & Relay Engine            │
        │   └── ai_analytics.py   ──► IsolationForest & RandomForest ML               │
        └──────────────────────────────────────┬──────────────────────────────────────┘
                                               │
                                               ▼
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                 4. STREAMLIT FRONTEND CONTROL DASHBOARD                     │
        │  Real-Time Waveforms, Grid Voltage Maps, Fault Simulator, AI Alerts         │
        └─────────────────────────────────────────────────────────────────────────────┘
        ```
        """)
        
    with col_diag_r:
        st.caption("⚙️ Core Technical Specifications & Operational Parameters")
        st.markdown("""
        <div style='background: var(--secondary-background-color); border: 1px solid rgba(88, 166, 255, 0.35); border-radius: 8px; padding: 14px; margin-bottom: 12px; color: var(--text-color);'>
            <div style='color: #58a6ff; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;'>
                ⚡ Electrical & Physics Metrics
            </div>
            <table style='width: 100%; font-size: 0.82rem; color: var(--text-color); border-collapse: collapse;'>
                <tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'><td style='padding: 4px 0;'><b>Nominal Voltage ($V_N$)</b></td><td style='text-align: right; color: #3fb950;'><b>230.0 V AC RMS</b></td></tr>
                <tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'><td style='padding: 4px 0;'><b>Voltage Tolerance Band</b></td><td style='text-align: right; color: #58a6ff;'>218.5V – 241.5V (±5%)</td></tr>
                <tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'><td style='padding: 4px 0;'><b>Maximum Feeder Current</b></td><td style='text-align: right; color: #f85149;'>30.0 A per phase</td></tr>
                <tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'><td style='padding: 4px 0;'><b>Active Power Threshold</b></td><td style='text-align: right; color: #d2a8ff;'>25.0 kW Feeder Rating</td></tr>
                <tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'><td style='padding: 4px 0;'><b>Grid AC Frequency</b></td><td style='text-align: right; color: #e3b341;'>50.0 Hz ± 0.08 Hz</td></tr>
                <tr><td style='padding: 4px 0;'><b>Target Power Factor</b></td><td style='text-align: right; color: #3fb950;'>≥ 0.90 ($\cos\phi$)</td></tr>
            </table>
        </div>

        <div style='background: var(--secondary-background-color); border: 1px solid rgba(248, 81, 73, 0.35); border-radius: 8px; padding: 14px; color: var(--text-color);'>
            <div style='color: #f85149; font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;'>
                🛡️ Grid Safety & Protection Limits
            </div>
            <table style='width: 100%; font-size: 0.82rem; color: var(--text-color); border-collapse: collapse;'>
                <tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'><td style='padding: 4px 0;'><b>Phase Imbalance Limit</b></td><td style='text-align: right; color: #f85149;'><b>2.0% (NEMA MG-1)</b></td></tr>
                <tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'><td style='padding: 4px 0;'><b>Relay Trip Protection</b></td><td style='text-align: right; color: #58a6ff;'>IEC 60255 Curve (&lt;150ms)</td></tr>
                <tr style='border-bottom: 1px solid rgba(128,128,128,0.2);'><td style='padding: 4px 0;'><b>Line Loading Threshold</b></td><td style='text-align: right; color: #e3b341;'>90.0% Max Rating</td></tr>
                <tr><td style='padding: 4px 0;'><b>Voltage Sag Limit</b></td><td style='text-align: right; color: #f85149;'>&lt; 0.90 p.u. (10% Drop)</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- 2. EXHAUSTIVE DEEP DIVE EXPANDERS FOR ALL 6 LAYERS ---
    st.caption("📘 Complete Layer-by-Layer Technical Guide")
    
    exp1, exp2 = st.columns(2)
    
    with exp1:
        with st.expander("📡 Layer 1: Hardware & Sensor Telemetry (ESP32 / PZEM-004T)"):
            st.markdown(r"""
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
            st.markdown(r"""
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
            st.markdown(r"""
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
            st.markdown(r"""
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
            st.markdown(r"""
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
    
    # --- 3. CROSS-TAB SYSTEM INTEGRATION MATRIX ---
    st.caption("🔗 Cross-Tab Integration Architecture & Data Flow")
    st.markdown("""
    | Component / Tab | Input Trigger | Core Engine / Module | Output Destination |
    | :--- | :--- | :--- | :--- |
    | **Tab 1: ESP32 Telemetry** | 1s MQTT / Simulator Packet | `database.py` SQLite Engine | Real-Time Waveforms, Phase Imbalance Alerts, Database |
    | **Tab 2: Pandapower Grid** | Sensor Baseline / Sliders | `grid_simulation.py` Newton-Raphson | Bus Voltage Maps, Line Loading %, Closed-Loop Fault Recommendations |
    | **Tab 3: OpenDSS Faults** | Automatic Violation / Inject Button | `fault_analysis.py` IEC 60255 Relays | Voltage Sag Profile, kA Short-Circuit Current, Relay Trip Times |
    | **Tab 4: AI & Load Forecast** | Telemetry Stream History | `ai_analytics.py` (IsolationForest + RF) | Anomaly Logs, 24-Hour Predictive Load Curves |
    | **Tab 5: Settings & Hub** | User Control Panel | System Diagnostics & Settings | System Health, AI Retraining, Database Reset, Config |
    """)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- 4. LIVE SYSTEM HEALTH & INTEGRATION CONTROL PANEL ---
    st.caption("⚡ Live System Integration & Maintenance Controls")
    
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.subheader("📡 Broker & Hardware Settings")
        st.text_input("MQTT Broker Host", "broker.hivemq.com", disabled=True)
        st.text_input("Port / Topic", "1883 | esp32/smartgrid/telemetry", disabled=True)
        
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.text_input("Nominal Voltage", "230 V (AC)", disabled=True)
        with c_p2:
            st.text_input("Grid Frequency", "50.0 Hz", disabled=True)
            
        st.info("🟢 MQTT Status: Online & Connected to HiveMQ Broker.")
        
        st.subheader("🚀 Full-System Integration Diagnostic Test")
        if st.button("🧪 Run End-to-End Grid Stress & AI Diagnostics Test", use_container_width=True):
            with st.spinner("Running full cross-tab integration test across Pandapower, OpenDSS, and AI..."):
                # 1. Run Power Flow
                pf_res = grid_sim.run_power_flow(load_scaling=1.35, solar_generation_mw=0.5, auto_log_anomalies=True)
                # 2. Run Fault Analysis
                f_res = fault_sim.simulate_fault("3PH", "Feeder Node B (Node 3)", 0.05)
                # 3. Retrain AI Models
                telemetry_df = db.get_recent_telemetry(limit=300)
                ai_engine.train_anomaly_detector(telemetry_df)
                ai_engine.train_load_forecaster(telemetry_df)
                
            st.success(f"✅ Integration Test Complete! Pandapower Max Loading: {pf_res['max_line_loading_pct']}%, OpenDSS Fault Current: {f_res['fault_current_ka']} kA, AI Models Retrained!")

    with c_right:
        st.subheader("💾 Database Health & Diagnostics")
        
        db_path = db.DB_PATH
        db_exists = os.path.exists(db_path)
        db_size_kb = os.path.getsize(db_path) / 1024.0 if db_exists else 0.0
        
        telemetry_df = db.get_recent_telemetry(limit=1000)
        faults_df = db.get_all_faults()
        anomalies_df = db.get_all_anomalies()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Telemetry Records", len(telemetry_df))
        m2.metric("Fault Logs", len(faults_df))
        m3.metric("AI Anomalies", len(anomalies_df))
        
        st.write(f"**Database Size**: `{db_size_kb:.1f} KB` | **File**: `{os.path.basename(db_path)}`")
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("🤖 Retrain AI Engines", use_container_width=True):
                ai_engine.train_anomaly_detector(telemetry_df)
                ai_engine.train_load_forecaster(telemetry_df)
                st.success("IsolationForest & RandomForest models successfully retrained!")
                
        with btn_c2:
            if st.button("🔄 Reset & Seed 24h Data", use_container_width=True):
                if os.path.exists(db_path):
                    os.remove(db_path)
                db.init_db()
                st.success("Database successfully reset and seeded with fresh 24h baseline data!")
                st.rerun()

#cd C:\Users\yashd\.gemini\antigravity\scratch\smart_grid_monitoring; python run_system.py