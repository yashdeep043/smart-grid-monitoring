import os
import sys
import subprocess
import time
import threading

def install_dependencies():
    print("Checking Python requirements...")
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_path], check=True)
        print("Dependencies verified!")
    except Exception as e:
        print(f"Note on dependencies: {e}")

def run_simulator_background():
    print("Starting background ESP32 Simulator process...")
    sim_script = os.path.join(os.path.dirname(__file__), "esp32_simulator.py")
    subprocess.run([sys.executable, sim_script])

def run_continuous_powerflow_background():
    print("Starting background Continuous Power Flow solver thread...")
    import database as db
    from grid_simulation import GridSimulator
    
    grid_sim = GridSimulator()
    while True:
        try:
            res = grid_sim.run_power_flow(
                load_scaling=1.0, 
                solar_generation_mw=0.8, 
                use_telemetry_baseline=True, 
                auto_log_anomalies=True
            )
            if res.get('success'):
                status_str = "VIOLATION" if len(res['violations']) > 0 else "NORMAL"
                viol_str = "; ".join(res['violations']) if len(res['violations']) > 0 else "None"
                db.log_powerflow_result(
                    mode="LIVE_AUTO",
                    total_load_mw=res['total_load_mw'],
                    solar_gen_mw=res['solar_gen_mw'],
                    total_loss_kw=res['total_loss_kw'],
                    min_voltage_pu=res['min_voltage_pu'],
                    max_line_loading_pct=res['max_line_loading_pct'],
                    status=status_str,
                    violations=viol_str
                )
        except Exception as e:
            print(f"Error in continuous powerflow thread: {e}")
        time.sleep(4)

def main():
    print("==========================================================")
    print("⚡ ESP32 SMART GRID MONITORING & FAULT ANALYSIS SYSTEM ⚡")
    print("==========================================================")
    
    # 1. Initialize Database
    import database as db
    db.init_db()
    print("✓ SQLite Database Initialized & Seeded")
    
    # 2. Launch Background Simulator in separate thread
    sim_thread = threading.Thread(target=run_simulator_background, daemon=True)
    sim_thread.start()
    print("✓ ESP32 Sensor Simulator Active")
    
    # 3. Launch Continuous Power Flow Thread
    pf_thread = threading.Thread(target=run_continuous_powerflow_background, daemon=True)
    pf_thread.start()
    print("✓ Continuous Pandapower Power Flow Thread Active")
    
    time.sleep(2)
    
    # 4. Launch Streamlit App
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    print(f"✓ Launching Streamlit Dashboard on app.py...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()

