import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smart_grid.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Initialize database tables and seed baseline data if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Telemetry Table (ESP32 Sensor readings)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            node_id TEXT NOT NULL,
            voltage_a REAL,
            voltage_b REAL,
            voltage_c REAL,
            current_a REAL,
            current_b REAL,
            current_c REAL,
            active_power REAL,
            reactive_power REAL,
            power_factor REAL,
            frequency REAL,
            status TEXT
        )
    ''')
    
    # Fault Events Table (OpenDSS / Short Circuit results)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fault_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            fault_type TEXT,
            location_node TEXT,
            fault_current_ka REAL,
            voltage_dip_pct REAL,
            clearing_time_ms REAL,
            severity TEXT
        )
    ''')
    
    # AI Anomalies Table (Scikit-learn IsolationForest outputs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            node_id TEXT,
            voltage_v REAL,
            current_a REAL,
            anomaly_score REAL,
            description TEXT
        )
    ''')
    
    # Power Flow History Table (Time-series Pandapower runs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS powerflow_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            mode TEXT,
            total_load_mw REAL,
            solar_gen_mw REAL,
            total_loss_kw REAL,
            min_voltage_pu REAL,
            max_line_loading_pct REAL,
            status TEXT,
            violations TEXT
        )
    ''')
    
    conn.commit()
    
    # Check if empty; if so, seed historical demo data for dashboard immediate readiness
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_historical_data(conn)
        
    conn.close()

def seed_historical_data(conn):
    """Seed 24 hours of realistic 3-phase grid telemetry data."""
    now = datetime.now()
    records = []
    nodes = ["ESP32_SUBSTATION_01", "ESP32_FEEDER_A", "ESP32_FEEDER_B"]
    
    for i in range(240): # 24 hours, 6 min intervals
        ts = (now - timedelta(minutes=(240 - i)*6)).strftime('%Y-%m-%d %H:%M:%S')
        # Hourly load shape (peak at hour 14-20)
        hour = (now - timedelta(minutes=(240 - i)*6)).hour
        load_factor = 0.6 + 0.35 * np.sin(np.pi * (hour - 6) / 12) if 6 <= hour <= 22 else 0.4
        
        for node in nodes:
            v_nominal = 230.0 if "FEEDER" in node else 11000.0 # Low vs Medium voltage
            v_a = v_nominal * (1.0 + np.random.normal(0, 0.015))
            v_b = v_nominal * (1.0 + np.random.normal(0, 0.015))
            v_c = v_nominal * (1.0 + np.random.normal(0, 0.015))
            
            base_curr = 25.0 * load_factor if "FEEDER" in node else 150.0 * load_factor
            i_a = base_curr * (1.0 + np.random.normal(0, 0.03))
            i_b = base_curr * (1.0 + np.random.normal(0, 0.03))
            i_c = base_curr * (1.0 + np.random.normal(0, 0.03))
            
            pf = 0.92 + np.random.normal(0, 0.02)
            pf = min(max(pf, 0.80), 0.99)
            
            p_kw = (v_a * i_a + v_b * i_b + v_c * i_c) * pf / 1000.0
            q_kvar = p_kw * np.tan(np.arccos(pf))
            freq = 50.0 + np.random.normal(0, 0.05)
            
            status = "NORMAL"
            if np.random.rand() < 0.03: # occasional sag or spike
                v_a *= 0.85
                status = "VOLTAGE_SAG"
                
            records.append((ts, node, v_a, v_b, v_c, i_a, i_b, i_c, p_kw, q_kvar, pf, freq, status))
            
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO telemetry 
        (timestamp, node_id, voltage_a, voltage_b, voltage_c, current_a, current_b, current_c, active_power, reactive_power, power_factor, frequency, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)
    conn.commit()

def log_telemetry(data):
    """Insert single telemetry packet from MQTT or Simulator."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO telemetry 
        (timestamp, node_id, voltage_a, voltage_b, voltage_c, current_a, current_b, current_c, active_power, reactive_power, power_factor, frequency, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("timestamp", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        data.get("node_id", "ESP32_NODE_01"),
        data.get("voltage_a", 230.0),
        data.get("voltage_b", 230.0),
        data.get("voltage_c", 230.0),
        data.get("current_a", 10.0),
        data.get("current_b", 10.0),
        data.get("current_c", 10.0),
        data.get("active_power", 6.5),
        data.get("reactive_power", 1.2),
        data.get("power_factor", 0.95),
        data.get("frequency", 50.0),
        data.get("status", "NORMAL")
    ))
    conn.commit()
    conn.close()

def log_fault_event(fault_type, location, fault_ka, voltage_dip, clearing_ms, severity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fault_events (timestamp, fault_type, location_node, fault_current_ka, voltage_dip_pct, clearing_time_ms, severity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), fault_type, location, fault_ka, voltage_dip, clearing_ms, severity))
    conn.commit()
    conn.close()

def log_anomaly(node_id, v, i, score, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO anomalies (timestamp, node_id, voltage_v, current_a, anomaly_score, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), node_id, v, i, score, description))
    conn.commit()
    conn.close()

def get_recent_telemetry(limit=100, node_id=None):
    conn = get_connection()
    query = "SELECT * FROM telemetry"
    params = []
    if node_id:
        query += " WHERE node_id = ?"
        params.append(node_id)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def get_all_faults():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM fault_events ORDER BY id DESC", conn)
    conn.close()
    return df

def get_all_anomalies():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM anomalies ORDER BY id DESC", conn)
    conn.close()
    return df

def log_powerflow_result(mode, total_load_mw, solar_gen_mw, total_loss_kw, min_voltage_pu, max_line_loading_pct, status, violations):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO powerflow_history 
        (timestamp, mode, total_load_mw, solar_gen_mw, total_loss_kw, min_voltage_pu, max_line_loading_pct, status, violations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), mode, total_load_mw, solar_gen_mw, total_loss_kw, min_voltage_pu, max_line_loading_pct, status, violations))
    conn.commit()
    conn.close()

def get_powerflow_history(limit=60):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM powerflow_history ORDER BY id DESC LIMIT ?", conn, params=[limit])
    conn.close()
    return df

def get_telemetry_baseline_load(limit=10):
    """
    Query recent active power readings from telemetry table.
    Returns:
        dict containing average active_power (kW), nominal baseline MW (for Pandapower),
        and ratio relative to nominal base grid load (5.45 MW).
    """
    conn = get_connection()
    df = pd.read_sql_query("SELECT active_power FROM telemetry ORDER BY id DESC LIMIT ?", conn, params=[limit])
    conn.close()
    
    if df.empty or 'active_power' not in df.columns:
        return {'avg_power_kw': 25.0, 'live_load_mw': 5.45, 'baseline_scaling': 1.0}
        
    avg_power_kw = float(df['active_power'].mean())
    # Baseline grid nominal load is 5.45 MW.
    # Telemetry active_power represents localized feeder sample (around 20-35 kW nominal).
    # Baseline scaling ratio = avg_power_kw / 25.0 (25 kW standard baseline).
    baseline_scaling = round(avg_power_kw / 25.0, 2)
    baseline_scaling = max(min(baseline_scaling, 3.0), 0.3)
    live_load_mw = round(5.45 * baseline_scaling, 2)
    
    return {
        'avg_power_kw': round(avg_power_kw, 2),
        'live_load_mw': live_load_mw,
        'baseline_scaling': baseline_scaling
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized and seeded successfully.")
    print("Baseline:", get_telemetry_baseline_load())

