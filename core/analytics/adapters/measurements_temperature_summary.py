import pandas as pd

from core.analytics.adapters.base import BaseAdapter

class MeasurementsTemperatureSummaryAdapter(BaseAdapter):
    """
    Adapter for computing temperature statistics from measurement data.
    Mirrors the TemperatureSummaryAdapter for simulations.
    
    Expected input format:
    - Temperatures in °C
    
    Column structure by position (names don't matter):
    - Col 0: datetime (Zeitstempel)
    - Col 1: Aussentemperatur [°C]
    - Col 2: Raumtemperatur [°C]
    
    KPIs calculated (used in UI):
    - min: Minimum outdoor temperature [°C]
    - max: Maximum outdoor temperature [°C]
    - min_timestamp: Timestamp of minimum temperature
    - max_timestamp: Timestamp of maximum temperature
    """
    def __init__(self, overheating_threshold: float = 26.0):
        super().__init__(name="MeasurementsTemperatureSummary", kind="measurements")
        self.overheating_threshold = overheating_threshold
        self.required_raw_columns = set()

    def compute(self, df: pd.DataFrame, project_id: str = None, time_column: str = None, date_range: tuple = None) -> dict:
        """
        Compute temperature KPIs for measurement data.
        
        Args:
            df: Measurement data
            project_id: Project identifier
            time_column: Name of time column
            date_range: Optional (start_date, end_date) filter
        
        Returns:
            dict: {"summary": DataFrame with KPIs}
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
        
        # Fixed positions: Col 1 = Outdoor temp (only KPI used in UI)
        if len(df.columns) <= 1:
            return {"summary": pd.DataFrame()}
        
        outdoor_col = df.columns[1]
        outdoor_series = pd.to_numeric(filtered[outdoor_col], errors="coerce")
        
        if outdoor_series.empty or outdoor_series.count() == 0:
            return {"summary": pd.DataFrame()}
        
        try:
            idx_min = outdoor_series.idxmin()
            idx_max = outdoor_series.idxmax()
            min_ts = filtered_times.loc[idx_min] if pd.notna(idx_min) else pd.NaT
            max_ts = filtered_times.loc[idx_max] if pd.notna(idx_max) else pd.NaT
        except Exception:
            min_ts = pd.NaT
            max_ts = pd.NaT
        
        rows = [
            {"project_id": project_id, "column_name": "Aussentemperatur", "metric": "min", "value": float(outdoor_series.min()), "unit": "°C"},
            {"project_id": project_id, "column_name": "Aussentemperatur", "metric": "max", "value": float(outdoor_series.max()), "unit": "°C"},
            {"project_id": project_id, "column_name": "Aussentemperatur", "metric": "min_timestamp", "value": str(min_ts), "unit": "datetime"},
            {"project_id": project_id, "column_name": "Aussentemperatur", "metric": "max_timestamp", "value": str(max_ts), "unit": "datetime"},
        ]
        
        summary_df = pd.DataFrame(rows)
        return {"summary": summary_df}
