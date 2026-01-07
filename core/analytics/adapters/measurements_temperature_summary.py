import pandas as pd
import re

from core.analytics.adapters.base import BaseAdapter

class MeasurementsTemperatureSummaryAdapter(BaseAdapter):
    """
    Adapter for computing temperature statistics from measurement data.
    Mirrors the TemperatureSummaryAdapter for simulations.
    
    Column structure by position (names don't matter):
    - Col 0: datetime (Zeitstempel)
    - Col 1: Aussentemperatur (used here)
    - Col 2: Raumtemperatur (used here)
    - Col 3: Heizleistung
    - Col 4: Kühlleistung
    """
    def __init__(self, overheating_threshold: float = 26.0):
        super().__init__(name="MeasurementsTemperatureSummary", kind="measurements")
        self.overheating_threshold = overheating_threshold
        self.required_raw_columns = set()

    def compute(self, df: pd.DataFrame, project_id: str = None, time_column: str = None, date_range: tuple = None) -> dict:
        """
        Compute temperature statistics for measurement data.
        Uses column positions instead of names.
        
        Returns metrics like: mean, min, max, overheating_hours
        """
        if df is None or df.empty:
            return {"summary": pd.DataFrame()}
        
        if time_column is None:
            time_column = df.columns[0]
        
        times = pd.to_datetime(df[time_column], errors="coerce")
        
        # Apply date range filter
        mask = times.notna()
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            if start_date:
                mask &= times >= pd.to_datetime(start_date)
            if end_date:
                mask &= times <= pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(milliseconds=1)
        
        filtered = df.loc[mask].copy()
        filtered_times = times.loc[mask]
        
        if filtered.empty:
            return {"summary": pd.DataFrame()}
        
        # Use fixed column positions:
        # Col 1: Aussentemperatur, Col 2: Raumtemperatur
        temp_positions = [1, 2]
        temp_names = ["Aussentemperatur", "Raumtemperatur"]
        
        rows = []
        dt_hours = 1.0  # Assuming 1-hour timestep
        
        for pos, name in zip(temp_positions, temp_names):
            if pos >= len(df.columns):
                continue
            
            col = df.columns[pos]
            # Convert to numeric, coercing errors
            series = pd.to_numeric(filtered[col], errors="coerce")
            
            if series.empty or series.count() == 0:
                continue
            
            idx_min = series.idxmin()
            idx_max = series.idxmax()
            
            try:
                min_ts = filtered_times.loc[idx_min] if pd.notna(idx_min) else pd.NaT
            except:
                min_ts = pd.NaT
            
            try:
                max_ts = filtered_times.loc[idx_max] if pd.notna(idx_max) else pd.NaT
            except:
                max_ts = pd.NaT
            
            # Compute overheating hours
            overheating_hours = (series > self.overheating_threshold).sum() * dt_hours
            
            rows.extend([
                {"project_id": project_id, "column_name": name, "metric": "mean", "value": float(series.mean()), "unit": "°C"},
                {"project_id": project_id, "column_name": name, "metric": "min", "value": float(series.min()), "unit": "°C"},
                {"project_id": project_id, "column_name": name, "metric": "min_timestamp", "value": str(min_ts), "unit": "datetime"},
                {"project_id": project_id, "column_name": name, "metric": "max", "value": float(series.max()), "unit": "°C"},
                {"project_id": project_id, "column_name": name, "metric": "max_timestamp", "value": str(max_ts), "unit": "datetime"},
                {"project_id": project_id, "column_name": name, "metric": "overheating_hours", "value": float(overheating_hours), "unit": "h"},
            ])
        
        if not rows:
            return {"summary": pd.DataFrame()}
        
        summary_df = pd.DataFrame(rows)
        return {"summary": summary_df}
