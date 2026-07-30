import pandas as pd
import numpy as np
import database as db

try:
    import pandapower as pp
    import pandapower.networks as pn
    PANDAPOWER_AVAILABLE = True
except ImportError:
    PANDAPOWER_AVAILABLE = False

class GridSimulator:
    def __init__(self):
        self.net = None
        self.setup_network()
        
    def setup_network(self):
        """Construct a 7-Bus Radial Electrical Distribution Grid Network."""
        if not PANDAPOWER_AVAILABLE:
            return
            
        net = pp.create_empty_network(name="Smart_Grid_Distribution_Feeder")
        
        # Buses
        b0 = pp.create_bus(net, vn_kv=110.0, name="Grid Substation High Voltage", geodata=(0, 0))
        b1 = pp.create_bus(net, vn_kv=11.0, name="Substation Bus 11kV", geodata=(1, 0))
        b2 = pp.create_bus(net, vn_kv=11.0, name="Feeder Node A (Industrial)", geodata=(2, 1))
        b3 = pp.create_bus(net, vn_kv=11.0, name="Feeder Node B (Commercial)", geodata=(3, 1))
        b4 = pp.create_bus(net, vn_kv=11.0, name="Feeder Node C (Residential)", geodata=(4, 0))
        b5 = pp.create_bus(net, vn_kv=0.4, name="Local Transformer LV Node 1", geodata=(4, -1))
        b6 = pp.create_bus(net, vn_kv=0.4, name="Local Transformer LV Node 2", geodata=(3, -1))
        
        # Grid External Connection
        pp.create_ext_grid(net, bus=b0, vm_pu=1.0, name="HV Grid Grid Connection")
        
        # Transformer (Custom 110/11 kV and 10/0.4 kV Transformers)
        pp.create_transformer_from_parameters(
            net, hv_bus=b0, lv_bus=b1, sn_mva=25.0, vn_hv_kv=110.0, vn_lv_kv=11.0,
            vkr_percent=0.4, vk_percent=12.0, pfe_kw=15.0, i0_percent=0.06, name="Main Substation Trafo"
        )
        pp.create_transformer_from_parameters(
            net, hv_bus=b4, lv_bus=b5, sn_mva=0.4, vn_hv_kv=11.0, vn_lv_kv=0.4,
            vkr_percent=1.2, vk_percent=4.0, pfe_kw=0.8, i0_percent=0.25, name="Residential Trafo"
        )
        pp.create_transformer_from_parameters(
            net, hv_bus=b3, lv_bus=b6, sn_mva=0.63, vn_hv_kv=11.0, vn_lv_kv=0.4,
            vkr_percent=1.1, vk_percent=4.0, pfe_kw=1.1, i0_percent=0.22, name="Commercial Trafo"
        )
        
        # Lines (11kV Distribution Lines)
        pp.create_line_from_parameters(
            net, from_bus=b1, to_bus=b2, length_km=2.5, r_ohm_per_km=0.12, x_ohm_per_km=0.35,
            c_nf_per_km=210.0, max_i_ka=0.4, name="Line 1-2"
        )
        pp.create_line_from_parameters(
            net, from_bus=b2, to_bus=b3, length_km=1.8, r_ohm_per_km=0.12, x_ohm_per_km=0.35,
            c_nf_per_km=210.0, max_i_ka=0.4, name="Line 2-3"
        )
        pp.create_line_from_parameters(
            net, from_bus=b3, to_bus=b4, length_km=3.0, r_ohm_per_km=0.12, x_ohm_per_km=0.35,
            c_nf_per_km=210.0, max_i_ka=0.4, name="Line 3-4"
        )
        
        # Loads
        pp.create_load(net, bus=b2, p_mw=2.2, q_mvar=0.8, name="Industrial Load")
        pp.create_load(net, bus=b3, p_mw=1.5, q_mvar=0.5, name="Commercial Load")
        pp.create_load(net, bus=b4, p_mw=1.1, q_mvar=0.3, name="Residential Load HV")
        pp.create_load(net, bus=b5, p_mw=0.25, q_mvar=0.08, name="Residential Low Voltage")
        pp.create_load(net, bus=b6, p_mw=0.45, q_mvar=0.15, name="Commercial Low Voltage")
        
        # Solar PV Generator (Distributed Energy Resource)
        pp.create_sgen(net, bus=b4, p_mw=0.8, q_mvar=0.0, name="Rooftop Solar PV Park")
        
        self.net = net

    def run_power_flow(self, load_scaling=1.0, solar_generation_mw=0.8, use_telemetry_baseline=True, auto_log_anomalies=True):
        """Execute AC Power Flow simulation with live baseline telemetry scaling and auto-alerting."""
        # Query SQLite live baseline
        baseline = db.get_telemetry_baseline_load() if use_telemetry_baseline else {'avg_power_kw': 25.0, 'live_load_mw': 5.45, 'baseline_scaling': 1.0}
        
        # Effective scaling = user multiplier * live telemetry baseline ratio
        effective_scaling = load_scaling * baseline['baseline_scaling'] if use_telemetry_baseline else load_scaling
        
        if not PANDAPOWER_AVAILABLE or self.net is None:
            return self._fallback_simulation(effective_scaling, solar_generation_mw, baseline, auto_log_anomalies)
            
        # Update dynamic parameters
        self.net.load['scaling'] = effective_scaling
        if len(self.net.sgen) > 0:
            self.net.sgen.loc[0, 'p_mw'] = solar_generation_mw
            
        try:
            pp.runpp(self.net, algorithm="nr", max_iteration=20)
            
            # Format Bus Voltage Profile DataFrame
            buses_df = pd.DataFrame({
                'Bus ID': self.net.bus.index,
                'Bus Name': self.net.bus['name'],
                'Voltage (kV)': (self.net.res_bus['vm_pu'] * self.net.bus['vn_kv']).round(3),
                'Voltage (p.u.)': self.net.res_bus['vm_pu'].round(4),
                'Angle (deg)': self.net.res_bus['va_degree'].round(2),
                'Status': np.where(
                    (self.net.res_bus['vm_pu'] < 0.95) | (self.net.res_bus['vm_pu'] > 1.05), 
                    'VIOLATION', 'NORMAL'
                )
            })
            
            # Format Line Loading DataFrame
            lines_df = pd.DataFrame({
                'Line Name': self.net.line['name'],
                'From Bus': self.net.line['from_bus'],
                'To Bus': self.net.line['to_bus'],
                'Loading (%)': self.net.res_line['loading_percent'].round(2),
                'Losses (kW)': (self.net.res_line['pl_mw'] * 1000).round(2),
                'Current (kA)': self.net.res_line['i_ka'].round(4),
                'Overloaded': self.net.res_line['loading_percent'] > 90.0
            })
            
            total_loss_kw = float((self.net.res_line['pl_mw'].sum() + self.net.res_trafo['pl_mw'].sum()) * 1000)
            min_voltage_pu = float(self.net.res_bus['vm_pu'].min())
            max_line_loading_pct = float(self.net.res_line['loading_percent'].max())
            
            most_stressed_line_idx = self.net.res_line['loading_percent'].idxmax()
            most_stressed_line = str(self.net.line.loc[most_stressed_line_idx, 'name'])
            
            min_v_idx = self.net.res_bus['vm_pu'].idxmin()
            most_stressed_node = str(self.net.bus.loc[min_v_idx, 'name'])
            
            violations = []
            if min_voltage_pu < 0.95:
                violations.append(f"Voltage Undervoltage ({min_voltage_pu:.3f} p.u. at {most_stressed_node})")
            elif min_voltage_pu > 1.05:
                violations.append(f"Voltage Overvoltage ({min_voltage_pu:.3f} p.u.)")
                
            if max_line_loading_pct > 90.0:
                violations.append(f"Line Thermal Overload ({max_line_loading_pct:.1f}% on {most_stressed_line})")
                
            # Log anomalies automatically into SQLite anomalies table
            if auto_log_anomalies and len(violations) > 0:
                for v_msg in violations:
                    db.log_anomaly(
                        node_id=most_stressed_node,
                        v=round(min_voltage_pu * 230.0, 1),
                        i=round(max_line_loading_pct * 0.5, 1),
                        score=-0.88,
                        description=f"POWER FLOW ALERTS: {v_msg}"
                    )
            
            return {
                'success': True,
                'buses': buses_df,
                'lines': lines_df,
                'total_loss_kw': round(total_loss_kw, 2),
                'total_load_mw': round(float(self.net.res_load['p_mw'].sum()), 2),
                'solar_gen_mw': solar_generation_mw,
                'effective_scaling': round(effective_scaling, 2),
                'telemetry_baseline': baseline,
                'min_voltage_pu': round(min_voltage_pu, 4),
                'max_line_loading_pct': round(max_line_loading_pct, 2),
                'most_stressed_line': most_stressed_line,
                'most_stressed_node': most_stressed_node,
                'violations': violations
            }
            
        except Exception as e:
            print(f"Pandapower solver error: {e}")
            return self._fallback_simulation(effective_scaling, solar_generation_mw, baseline, auto_log_anomalies)

    def _fallback_simulation(self, load_scaling, solar_mw, baseline=None, auto_log_anomalies=True):
        """Analytical fallback if pandapower solver fails or is uninstalled."""
        if baseline is None:
            baseline = {'avg_power_kw': 25.0, 'live_load_mw': 5.45, 'baseline_scaling': 1.0}
            
        bus_names = [
            "Grid Substation 110kV", "Substation 11kV", "Feeder Node A (Industrial)",
            "Feeder Node B (Commercial)", "Feeder Node C (Residential)", 
            "LV Node 1 (0.4kV)", "LV Node 2 (0.4kV)"
        ]
        nominal_kv = [110.0, 11.0, 11.0, 11.0, 11.0, 0.4, 0.4]
        
        # Calculate voltage drop based on load scaling
        v_pu = [1.0, 1.0, 0.99 - 0.02 * load_scaling, 0.98 - 0.03 * load_scaling, 0.97 - 0.04 * load_scaling + 0.015 * solar_mw, 0.96 - 0.045 * load_scaling, 0.965 - 0.04 * load_scaling]
        v_kv = [nom * pu for nom, pu in zip(nominal_kv, v_pu)]
        
        buses_df = pd.DataFrame({
            'Bus ID': range(7),
            'Bus Name': bus_names,
            'Voltage (kV)': np.round(v_kv, 3),
            'Voltage (p.u.)': np.round(v_pu, 4),
            'Angle (deg)': [0.0, -1.2, -2.5, -3.8, -4.9, -5.2, -4.5],
            'Status': ['NORMAL' if 0.95 <= v <= 1.05 else 'VIOLATION' for v in v_pu]
        })
        
        lines_df = pd.DataFrame({
            'Line Name': ["Line 1-2 (Ind)", "Line 2-3 (Com)", "Line 3-4 (Res)"],
            'From Bus': [1, 2, 3],
            'To Bus': [2, 3, 4],
            'Loading (%)': [np.round(52.4 * load_scaling, 1), np.round(41.1 * load_scaling, 1), np.round(38.6 * load_scaling, 1)],
            'Losses (kW)': [np.round(18.5 * load_scaling**2, 1), np.round(12.2 * load_scaling**2, 1), np.round(14.1 * load_scaling**2, 1)],
            'Current (kA)': [0.24, 0.18, 0.15],
            'Overloaded': [52.4 * load_scaling > 90.0, 41.1 * load_scaling > 90.0, 38.6 * load_scaling > 90.0]
        })
        
        min_voltage_pu = float(min(v_pu))
        max_line_loading_pct = float(max(lines_df['Loading (%)']))
        most_stressed_line = lines_df.loc[lines_df['Loading (%)'].idxmax(), 'Line Name']
        most_stressed_node = buses_df.loc[buses_df['Voltage (p.u.)'].idxmin(), 'Bus Name']
        
        violations = []
        if min_voltage_pu < 0.95:
            violations.append(f"Voltage Undervoltage ({min_voltage_pu:.3f} p.u. at {most_stressed_node})")
        if max_line_loading_pct > 90.0:
            violations.append(f"Line Thermal Overload ({max_line_loading_pct:.1f}% on {most_stressed_line})")
            
        if auto_log_anomalies and len(violations) > 0:
            for v_msg in violations:
                db.log_anomaly(
                    node_id=most_stressed_node,
                    v=round(min_voltage_pu * 230.0, 1),
                    i=round(max_line_loading_pct * 0.5, 1),
                    score=-0.88,
                    description=f"POWER FLOW ALERTS: {v_msg}"
                )
        
        return {
            'success': True,
            'buses': buses_df,
            'lines': lines_df,
            'total_loss_kw': round(44.8 * (load_scaling**2), 2),
            'total_load_mw': round(5.45 * load_scaling, 2),
            'solar_gen_mw': solar_mw,
            'effective_scaling': round(load_scaling, 2),
            'telemetry_baseline': baseline,
            'min_voltage_pu': round(min_voltage_pu, 4),
            'max_line_loading_pct': round(max_line_loading_pct, 2),
            'most_stressed_line': most_stressed_line,
            'most_stressed_node': most_stressed_node,
            'violations': violations
        }

if __name__ == "__main__":
    sim = GridSimulator()
    res = sim.run_power_flow(load_scaling=1.2, solar_generation_mw=1.0)
    print("Power Flow Simulation Results:")
    print(res['buses'])
    print(res['lines'])
