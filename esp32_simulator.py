import time
import json
import random
import math
from datetime import datetime
import database as db
from ai_analytics import SmartGridAI

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

MQTT_BROKER = "broker.hivemq.com" # Free public MQTT broker for instant testing
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/smartgrid/telemetry"

def generate_sensor_data(node_id="ESP32_SUBSTATION_01"):
    now = datetime.now()
    hour = now.hour
    
    # Load shape: peak during 12:00 - 20:00
    load_factor = 0.7 + 0.3 * math.sin(math.pi * (hour - 6) / 12) if 6 <= hour <= 22 else 0.45
    
    v_nominal = 230.0
    v_a = v_nominal * (1.0 + random.uniform(-0.02, 0.02))
    v_b = v_nominal * (1.0 + random.uniform(-0.02, 0.02))
    v_c = v_nominal * (1.0 + random.uniform(-0.02, 0.02))
    
    base_curr = 20.0 * load_factor
    i_a = base_curr * (1.0 + random.uniform(-0.04, 0.04))
    i_b = base_curr * (1.0 + random.uniform(-0.04, 0.04))
    i_c = base_curr * (1.0 + random.uniform(-0.04, 0.04))
    
    pf = round(random.uniform(0.91, 0.98), 2)
    
    # Inject synthetic fault/sag on 5% probability for live demo excitement
    status = "NORMAL"
    if random.random() < 0.05:
        v_a *= 0.78
        status = "VOLTAGE_SAG"
    elif random.random() < 0.02:
        i_a *= 3.5
        status = "OVERCURRENT_SPIKE"

    p_kw = round((v_a * i_a + v_b * i_b + v_c * i_c) * pf / 1000.0, 2)
    q_kvar = round(p_kw * math.tan(math.acos(pf)), 2)
    freq = round(50.0 + random.uniform(-0.08, 0.08), 2)
    
    payload = {
        "timestamp": now.strftime('%Y-%m-%d %H:%M:%S'),
        "node_id": node_id,
        "voltage_a": round(v_a, 2),
        "voltage_b": round(v_b, 2),
        "voltage_c": round(v_c, 2),
        "current_a": round(i_a, 2),
        "current_b": round(i_b, 2),
        "current_c": round(i_c, 2),
        "active_power": p_kw,
        "reactive_power": q_kvar,
        "power_factor": pf,
        "frequency": freq,
        "status": status
    }
    return payload

def run_simulator(interval_sec=5, max_loops=None):
    print(f"Starting ESP32 Sensor Simulator... (Publishing every {interval_sec}s)")
    db.init_db()
    ai = SmartGridAI()
    
    client = None
    if MQTT_AVAILABLE:
        try:
            if hasattr(mqtt, "CallbackAPIVersion"):
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "ESP32_Grid_Simulator")
            else:
                client = mqtt.Client("ESP32_Grid_Simulator")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            client.loop_start()
            print(f"Connected to MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            print(f"MQTT Broker Connection Note: {e} (Continuing with direct SQLite database logging)")
            client = None

    nodes = ["ESP32_SUBSTATION_01", "ESP32_FEEDER_A", "ESP32_FEEDER_B"]
    loop_count = 0
    
    try:
        while True:
            for node in nodes:
                packet = generate_sensor_data(node)
                
                # Check for AI Anomaly
                is_anom, score, desc = ai.predict_anomaly(packet)
                if is_anom:
                    db.log_anomaly(node, packet['voltage_a'], packet['current_a'], score, desc)
                    packet['status'] = 'ANOMALY_DETECTED'
                    
                # Save to database
                db.log_telemetry(packet)
                
                # Publish over MQTT if connected
                if client:
                    client.publish(MQTT_TOPIC, json.dumps(packet))
                    
                print(f"[{packet['timestamp']}] {node} | V_A: {packet['voltage_a']}V | I_A: {packet['current_a']}A | P: {packet['active_power']}kW | {packet['status']}")
                
            loop_count += 1
            if max_loops and loop_count >= max_loops:
                break
            time.sleep(interval_sec)
            
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()

if __name__ == "__main__":
    run_simulator(interval_sec=1)
