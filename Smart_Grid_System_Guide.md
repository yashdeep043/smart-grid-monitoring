# ⚡ Complete Beginner's Guide: ESP32 Smart Grid Monitoring & Fault Analysis System

Welcome! This document provides an **end-to-end tutorial and textbook guide** for your Smart Grid System. It is written specifically for students, researchers, and engineers taking their first steps into Smart Grids, Power Engineering, IoT, and AI.

---

## 1. Executive Summary & System Architecture

A **Smart Grid** is a modernized electrical grid that uses digital communication, sensors, computer simulation, and artificial intelligence to monitor and control the flow of electricity in real time.

### 📐 End-to-End System Block Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           1. HARDWARE LAYER                               │
│  ESP32 Microcontroller + PZEM-004T AC Voltage & Current Transducers       │
│  (Or Python ESP32 Telemetry Simulator: esp32_simulator.py)               │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼ (WiFi / MQTT / JSON Payloads)
┌───────────────────────────────────────────────────────────────────────────┐
│                         2. INGESTION & BROKER LAYER                       │
│  Public MQTT Broker (broker.hivemq.com:1883)                              │
│  Topic: esp32/smartgrid/telemetry                                         │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          3. PYTHON BACKEND ENGINE                         │
│                                                                           │
│   ├── database.py       ──► SQLite Time-Series Database (smart_grid.db)   │
│   ├── grid_simulation.py──► Pandapower AC Newton-Raphson Power Flow Solver│
│   ├── fault_analysis.py ──► OpenDSS Short-Circuit & Voltage Sag Engine    │
│   └── ai_analytics.py   ──► Scikit-learn (IsolationForest & RandomForest) │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      4. FRONTEND DASHBOARD LAYER                          │
│  Streamlit Web Control Panel (app.py)                                     │
│  Real-Time Waveforms, Grid Voltage Maps, Fault Simulator, AI Alerts       │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Deep-Dive

### 📡 Component A: Hardware & Telemetry Layer (`esp32_firmware.ino` & `esp32_simulator.py`)

#### What is an ESP32?
The **ESP32** is a low-cost, dual-core Wi-Fi & Bluetooth microcontroller. In smart grids, ESP32 nodes are installed at distribution substations and transformer poles to read grid parameters every few seconds.

#### Sensor Transducers (PZEM-004T)
The **PZEM-004T** is an AC power sensor module equipped with a Current Transformer (CT) clamp. It measures:
1. **Voltage ($V$)**: AC RMS Voltage (Nominal 230V).
2. **Current ($I$)**: AC RMS Current in Amperes ($A$).
3. **Active Power ($P$)**: Real power consumed ($kW$).
4. **Frequency ($f$)**: Grid frequency ($50 \text{ Hz}$ or $60 \text{ Hz}$).
5. **Power Factor ($PF$)**: Ratio of real power to apparent power ($\cos\phi$).

#### JSON Payload Structure over MQTT
Data is published over the MQTT protocol inside JSON strings formatted as follows:
```json
{
  "timestamp": "2026-07-24 18:35:41",
  "node_id": "ESP32_FEEDER_A",
  "voltage_a": 231.09,
  "voltage_b": 230.15,
  "voltage_c": 229.80,
  "current_a": 13.95,
  "current_b": 14.10,
  "current_c": 13.85,
  "active_power": 9.13,
  "reactive_power": 2.10,
  "power_factor": 0.95,
  "frequency": 50.0,
  "status": "NORMAL"
}
```

---

### 💾 Component B: Database Layer (`database.py`)

#### Why SQLite?
Smart grid telemetry generates continuous time-series data. We use **SQLite** (`smart_grid.db`), a light, serverless SQL database engine.

#### Database Tables Schema
1. `telemetry`: Stores live sensor readings every 3 seconds.
2. `fault_events`: Stores historical short-circuit fault simulations.
3. `anomalies`: Stores AI-flagged voltage sags, current surges, and equipment anomalies.

---

### 🌐 Component C: Pandapower Grid Power Flow Solver (`grid_simulation.py`)

#### What is Pandapower?
**Pandapower** is an open-source BSD-licensed Python library developed by the University of Kassel and Fraunhofer IEE for power system modeling and AC power flow calculation.

#### How AC Power Flow Works (Newton-Raphson Method)
Electricity obeys **Kirchhoff’s Current Law** and **Ohm’s Law** in complex AC phasor form ($\bar{S} = \bar{V} \cdot \bar{I}^*$). Pandapower solves non-linear AC equations:

$$P_i = \sum_{j=1}^{N} |V_i||V_j|(G_{ij}\cos\theta_{ij} + B_{ij}\sin\theta_{ij})$$

$$Q_i = \sum_{j=1}^{N} |V_i||V_j|(G_{ij}\sin\theta_{ij} - B_{ij}\cos\theta_{ij})$$

#### Key Metrics Evaluated:
1. **Bus Voltage Profile (p.u.)**: Per-unit voltage ($V_{pu} = V_{actual} / V_{base}$). Normal range is $0.95 \le V_{pu} \le 1.05$.
2. **Line Loading Percentage (%)**: $I_{line} / I_{max\_rated} \times 100\%$. If loading exceeds $90\%$, an overload warning is triggered.
3. **Active Line Losses ($kW$)**: Power lost as heat in feeder lines ($I^2 R$).

---

### 💥 Component D: OpenDSS Short-Circuit & Fault Analyzer (`fault_analysis.py`)

#### What is OpenDSS?
**OpenDSS** (Open Distribution System Simulator) is EPRI’s electric power distribution system simulator.

#### Types of Electrical Faults Simulated:
1. **3-Phase Symmetrical Fault (3PH)**: All three phase conductors touch each other. Extreme short-circuit current ($I_f \approx 2.5 - 5.0 \text{ kA}$).
2. **Single Line-to-Ground Fault (SLG)**: One phase conductor falls to the earth (70% of real-world grid faults).
3. **Line-to-Line Fault (LL)**: Two phase conductors collide due to storm winds or physical breakdown.

#### Overcurrent Relay Trip Time Calculation (IEC Curves)
Relays disconnect circuit breakers when fault current spikes. Trip time ($t$) follows the **IEC Extremely Inverse Characteristic**:

$$t = \frac{80}{\left(\frac{I_{fault}}{I_{pickup}}\right)^2 - 1} \text{ (seconds)}$$

---

### 🤖 Component E: Artificial Intelligence & Machine Learning (`ai_analytics.py`)

#### 1. Anomaly Detection (`IsolationForest`)
- **Algorithm**: `IsolationForest` from Scikit-Learn.
- **How it Works**: It builds random decision trees to isolate datapoints. Outliers (like a sudden voltage sag to 175V or a current surge to 47A) require very few splits to isolate, earning a high negative anomaly score.

#### 2. 24-Hour Load Forecasting (`RandomForestRegressor`)
- **Algorithm**: `RandomForestRegressor`.
- **How it Works**: Uses historical hour-of-day ($0-23$) and day-of-week ($0-6$) patterns to predict upcoming grid power demand ($kW$) for the next 24 hours with a $90\%$ upper/lower confidence band.

---

### 🎨 Component F: Streamlit Web Dashboard (`app.py`)

#### What is Streamlit?
**Streamlit** is a Python framework that converts Python code into interactive web applications.

#### Dashboard Features & Tabs:
- ⚡ **Real-Time Telemetry**: Gauges, 3-phase R-Y-B line charts, live stream table.
- 🌐 **Pandapower Power Flow**: Interactive load scaling slider ($0.5x - 2.5x$) & Solar PV slider ($0 - 3 \text{ MW}$).
- 💥 **OpenDSS Fault Analysis**: Interactive fault location selector & voltage collapse graph.
- 🤖 **AI Anomaly & Load Forecast**: Live anomaly alert table and 24h prediction plot.
- ⚙️ **Settings**: Database reset & system architecture overview.

---

## 3. Step-by-Step Code Summary

| File Name | Primary Language | Purpose | Key Libraries Used |
| :--- | :--- | :--- | :--- |
| [`requirements.txt`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/requirements.txt) | Text | Lists Python package dependencies | `streamlit`, `pandapower`, `scikit-learn`, `plotly` |
| [`database.py`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/database.py) | Python | SQLite DB manager & historical seeder | `sqlite3`, `pandas`, `numpy` |
| [`grid_simulation.py`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/grid_simulation.py) | Python | AC Newton-Raphson power flow solver | `pandapower`, `pandas` |
| [`fault_analysis.py`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/fault_analysis.py) | Python | Short-circuit fault current & voltage sag engine | `numpy`, `pandas` |
| [`ai_analytics.py`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/ai_analytics.py) | Python | ML IsolationForest & RandomForest forecaster | `scikit-learn`, `numpy` |
| [`esp32_simulator.py`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/esp32_simulator.py) | Python | 3-Phase telemetry producer & MQTT client | `paho-mqtt`, `json` |
| [`esp32_firmware.ino`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/esp32_firmware/esp32_firmware.ino) | C++ (Arduino) | ESP32 hardware firmware for real PZEM-004T sensors | `WiFi.h`, `PubSubClient.h`, `ArduinoJson.h` |
| [`app.py`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/app.py) | Python | Streamlit multi-tab web application | `streamlit`, `plotly`, `pandas` |
| [`run_system.py`](file:///C:/Users/yashd/.gemini/antigravity/scratch/smart_grid_monitoring/run_system.py) | Python | One-click master launcher script | `subprocess`, `threading` |

---

## 4. How to Execute the Project

Open PowerShell inside your project folder:

```powershell
cd C:\Users\yashd\.gemini\antigravity\scratch\smart_grid_monitoring
python run_system.py
```
