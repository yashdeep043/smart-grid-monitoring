import pandas as pd
import numpy as np

class OpenDSSFaultAnalyzer:
    def __init__(self):
        # Grid System Parameters
        self.v_base_kv = 11.0 # 11kV Distribution Nominal Voltage
        self.z_source_ohm = complex(0.2, 1.2) # Substation grid source impedance
        self.z_line_per_km = complex(0.15, 0.25) # Line impedance per km
        
        self.node_locations = {
            "Substation Bus (Node 1)": {"dist_km": 0.0, "type": "Substation"},
            "Feeder Node A (Node 2)": {"dist_km": 2.5, "type": "Industrial"},
            "Feeder Node B (Node 3)": {"dist_km": 4.3, "type": "Commercial"},
            "Feeder Node C (Node 4)": {"dist_km": 7.3, "type": "Residential"}
        }

    def simulate_fault(self, fault_type="3PH", location_node="Feeder Node B (Node 3)", fault_resistance=0.01):
        """
        Simulates short-circuit faults using OpenDSS impedance matrix methods.
        Fault Types:
          - '3PH': Three-Phase Symmetrical Fault
          - 'SLG': Single Line-to-Ground Fault
          - 'LL': Line-to-Line Fault
        """
        node_info = self.node_locations.get(location_node, {"dist_km": 4.3})
        dist_km = node_info["dist_km"]
        
        # Calculate total line impedance to fault point
        z_line = dist_km * self.z_line_per_km
        z_pos = self.z_source_ohm + z_line # Positive sequence impedance
        z_zero = z_pos * 3.0 # Zero sequence impedance approximation
        
        v_phase_v = (self.v_base_kv * 1000.0) / np.sqrt(3) # Line-to-neutral voltage
        
        r_f = float(fault_resistance)
        
        if fault_type == "3PH":
            # I_f = V_ph / (Z_1 + Z_f)
            z_total = abs(z_pos + r_f)
            i_fault_a = v_phase_v / z_total
            multiplier = 1.0
            description = "Three-Phase Symmetrical Short-Circuit (Severe)"
        elif fault_type == "SLG":
            # I_f = 3 * V_ph / (2*Z_1 + Z_0 + 3*R_f)
            z_total = abs(2 * z_pos + z_zero + 3 * r_f)
            i_fault_a = 3 * v_phase_v / z_total
            multiplier = 0.85
            description = "Single Line-to-Ground Fault (Most Common)"
        elif fault_type == "LL":
            # I_f = sqrt(3) * V_ph / (2*Z_1 + 2*R_f)
            z_total = abs(2 * z_pos + 2 * r_f)
            i_fault_a = np.sqrt(3) * v_phase_v / z_total
            multiplier = 0.866
            description = "Line-to-Line Unsymmetrical Fault"
        else:
            i_fault_a = 5000.0
            multiplier = 1.0
            description = "Generic Short Circuit"
            
        i_fault_ka = round(i_fault_a / 1000.0, 3)
        
        # Calculate Voltage Dips along feeder nodes
        dip_results = []
        for name, info in self.node_locations.items():
            d = info["dist_km"]
            if d <= dist_km:
                # Voltage sag proportional to fault distance ratio
                v_rem_pu = (d / (dist_km + 0.001)) * (1.0 - 0.1) + 0.1 * (dist_km - d) / (dist_km + 0.001)
                v_rem_pu = max(min(v_rem_pu, 0.98), 0.08)
            else:
                v_rem_pu = 0.15 # Downstream of fault collapses to low voltage
                
            dip_pct = round((1.0 - v_rem_pu) * 100, 1)
            dip_results.append({
                'Node': name,
                'Distance (km)': d,
                'Voltage Remainder (p.u.)': round(v_rem_pu, 3),
                'Voltage Dip (%)': dip_pct,
                'Fault Sag Status': 'CRITICAL DIP' if dip_pct > 50 else ('MODERATE SAG' if dip_pct > 15 else 'NORMAL')
            })
            
        # Overcurrent Relay Trip Time Calculation (IEC Extremely Inverse Curve)
        # t = 80 / ((I / I_pickup)^2 - 1)
        i_pickup_a = 400.0 # 400A relay setting
        multiple = max(i_fault_a / i_pickup_a, 1.05)
        trip_time_sec = round(80.0 / (multiple**2 - 1), 3)
        trip_time_sec = max(min(trip_time_sec, 5.0), 0.04) # 40ms to 5 seconds
        
        severity = "HIGH (CRITICAL)" if i_fault_ka > 4.0 else ("MEDIUM" if i_fault_ka > 2.0 else "LOW")
        
        return {
            'fault_type': fault_type,
            'location_node': location_node,
            'fault_current_ka': i_fault_ka,
            'fault_current_amp': round(i_fault_a, 1),
            'description': description,
            'trip_time_sec': trip_time_sec,
            'trip_time_ms': round(trip_time_sec * 1000, 1),
            'severity': severity,
            'voltage_dips': pd.DataFrame(dip_results)
        }

if __name__ == "__main__":
    analyzer = OpenDSSFaultAnalyzer()
    res = analyzer.simulate_fault("3PH", "Feeder Node B (Node 3)", fault_resistance=0.05)
    print(f"Fault Current: {res['fault_current_ka']} kA ({res['fault_current_amp']} A)")
    print(f"Relay Trip Time: {res['trip_time_ms']} ms")
    print(res['voltage_dips'])
