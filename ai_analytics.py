import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from datetime import datetime, timedelta

class SmartGridAI:
    def __init__(self):
        self.anomaly_model = IsolationForest(contamination=0.05, random_state=42)
        self.forecaster = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_anomaly_fitted = False
        self.is_forecaster_fitted = False

    def train_anomaly_detector(self, df_telemetry):
        """Train IsolationForest model on historical voltage/current readings."""
        if len(df_telemetry) < 20:
            return False
            
        features = df_telemetry[['voltage_a', 'voltage_b', 'voltage_c', 'current_a', 'current_b', 'current_c', 'power_factor']].dropna()
        if len(features) >= 20:
            self.anomaly_model.fit(features)
            self.is_anomaly_fitted = True
            return True
        return False

    def predict_anomaly(self, packet):
        """
        Evaluate single incoming ESP32 packet for anomalies.
        Returns: is_anomaly (bool), anomaly_score (float), description (str)
        """
        v_a = packet.get('voltage_a', 230.0)
        v_b = packet.get('voltage_b', 230.0)
        v_c = packet.get('voltage_c', 230.0)
        i_a = packet.get('current_a', 10.0)
        i_b = packet.get('current_b', 10.0)
        i_c = packet.get('current_c', 10.0)
        pf  = packet.get('power_factor', 0.95)
        
        # Rule-based quick checks
        if v_a < 180 or v_b < 180 or v_c < 180:
            return True, -0.85, "CRITICAL: Severe Voltage Sag Detected (<180V)"
        if i_a > 100 or i_b > 100 or i_c > 100:
            return True, -0.90, "CRITICAL: Overcurrent / Short Circuit Surge"
        if pf < 0.75:
            return True, -0.65, "WARNING: Low Power Factor (<0.75) Reactive Power Loss"
            
        if self.is_anomaly_fitted:
            features = np.array([[v_a, v_b, v_c, i_a, i_b, i_c, pf]])
            pred = self.anomaly_model.predict(features)[0] # -1 for anomaly, 1 for normal
            score = float(self.anomaly_model.score_samples(features)[0])
            if pred == -1:
                return True, round(score, 3), "ML Anomaly: Statistical Outlier Pattern"
                
        return False, 0.1, "NORMAL"

    def train_load_forecaster(self, df_telemetry):
        """Train RandomForest load forecasting model using historical hourly data."""
        if len(df_telemetry) < 30:
            return False
            
        df = df_telemetry.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['dayofweek'] = df['timestamp'].dt.dayofweek
        
        features = df[['hour', 'dayofweek']]
        target = df['active_power']
        
        self.forecaster.fit(features, target)
        self.is_forecaster_fitted = True
        return True

    def forecast_next_24h(self, df_telemetry=None):
        """Generate 24-hour ahead grid active power demand forecast (kW)."""
        now = datetime.now()
        future_hours = [(now + timedelta(hours=h)) for h in range(1, 25)]
        
        hours = [t.hour for t in future_hours]
        days = [t.weekday() for t in future_hours]
        
        if self.is_forecaster_fitted:
            X_future = pd.DataFrame({'hour': hours, 'dayofweek': days})
            predictions = self.forecaster.predict(X_future)
        else:
            # Baseline mathematical profile if ML not trained yet
            predictions = [
                35.0 + 20.0 * np.sin(np.pi * (h - 6) / 12) + np.random.normal(0, 2) if 6 <= h <= 22 else 20.0
                for h in hours
            ]
            
        forecast_df = pd.DataFrame({
            'Time': [t.strftime('%H:00') for t in future_hours],
            'Hour': hours,
            'Forecasted Load (kW)': np.round(predictions, 2),
            'Lower Confidence (kW)': np.round(np.array(predictions) * 0.9, 2),
            'Upper Confidence (kW)': np.round(np.array(predictions) * 1.1, 2)
        })
        
        return forecast_df

if __name__ == "__main__":
    ai = SmartGridAI()
    sample_packet = {'voltage_a': 165.0, 'voltage_b': 230.0, 'voltage_c': 230.0, 'current_a': 15.0, 'current_b': 10.0, 'current_c': 10.0, 'power_factor': 0.92}
    is_anom, score, desc = ai.predict_anomaly(sample_packet)
    print(f"Anomaly Check: {is_anom} | Score: {score} | Description: {desc}")
    print(ai.forecast_next_24h().head())
