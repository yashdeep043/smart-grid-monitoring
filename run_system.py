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
    
    time.sleep(2)
    
    # 3. Launch Streamlit App
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    print(f"✓ Launching Streamlit Dashboard on app.py...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()
