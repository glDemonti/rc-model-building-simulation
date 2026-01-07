import pandas as pd
import re

from core.analytics.adapters.base import BaseAdapter

class MeasurementsTemperatureSummaryAdapter(BaseAdapter):
    """
    Adapter for computing temperature statistics from measurement data.
    Mirrors the TemperatureSummaryAdapter for simulations.
    Detects temperature columns by name pattern (contains "temp").
    """
    def __init__(self, overheating_threshold: float = 26.0):
        super().__init__(name="MeasurementsTemperatureSummary", kind="measurements")
        self.overheating_threshold = overheating_threshold
        self.required_raw_columns = set()

    def _is_temperature_column(self, col_name: str) -> bool:
        """Check if column name suggests it's a temperature measurement."""
        return "temp" in col_name.lower()

    def compute(self, df: pd.DataFrame, project_id: str = None, time_column: str = None, date_range: tuple = None) -> dict:
        """
        Compute temperature statistics for measurement data.
        
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
        
        # Find temperature columns
        temp_cols = [col for col in filtered.select_dtypes(include=["number"]).columns 
                     if self._is_temperature_column(col)]
        
        if not temp_cols:
            return {"summary": pd.DataFrame()}
        
        rows = []
        dt_hours = 1.0  # Assuming 1-hour timestep
        
        for col in temp_cols:
            series = filtered[col]
            if series.empty or series.count() == 0:
                continue
            
            idx_min = series.idxmin()
            idx_max = series.idxmax()
            min_ts = filtered_times.get(idx_min, pd.NaT)
            max_ts = filtered_times.get(idx_max, pd.NaT)
            
            # Compute overheating hours
            overheating_hours = (series > self.overheating_threshold).sum() * dt_hours
            
            rows.extend([
                {"project_id": project_id, "column_name": col, "metric": "mean", "value": float(series.mean()), "unit": "°C"},
                {"project_id": project_id, "column_name": col, "metric": "min", "value": float(series.min()), "unit": "°C"},
                {"project_id": project_id, "column_name": col, "metric": "min_timestamp", "value": str(min_ts), "unit": "datetime"},
                {"project_id": project_id, "column_name": col, "metric": "max", "value": float(series.max()), "unit": "°C"},
                {"project_id": project_id, "column_name": col, "metric": "max_timestamp", "value": str(max_ts), "unit": "datetime"},
                {"project_id": project_id, "column_name": col, "metric": "overheating_hours", "value": float(overheating_hours), "unit": "h"},
            ])
        
        if not rows:
            return {"summary": pd.DataFrame()}
        
        summary_df = pd.DataFrame(rows)
        return {"summary": summary_df}
