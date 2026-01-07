import pandas as pd
import numpy as np

from core.analytics.adapters.base import BaseAdapter

class MeasurementsSummaryAdapter(BaseAdapter):
    """
    Adapter for computing statistics from measurement data.
    Returns data in standardized summary format (project_id, column_name, metric, value, unit).
    Compatible with AnalyticsService.compute_measurements() method.
    """
    def __init__(self):
        super().__init__(name="MeasurementsSummary", kind="measurements")
        self.required_raw_columns = set()  # flexible, depends on input data

    def compute(self, df: pd.DataFrame, project_id: str = None, time_column: str = None, date_range: tuple = None) -> dict:
        """
        Compute statistics for numeric columns in measurement data.
        
        Args:
            df (pd.DataFrame): Measurement data
            project_id (str): Project identifier for summary table
            time_column (str): Name of the time column (usually first column)
            date_range (tuple): Optional (start_date, end_date) for filtering
        
        Returns:
            dict: {"summary": DataFrame with standardized format}
        """
        if df is None or df.empty:
            return {"summary": pd.DataFrame()}
        
        # Identify time column if not provided
        if time_column is None:
            time_column = df.columns[0]
        
        # Parse times
        times = pd.to_datetime(df[time_column], errors="coerce")
        
        # Apply optional date range filter
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
        
        # Get numeric columns (exclude time column)
        numeric_cols = filtered.select_dtypes(include=["number"]).columns.tolist()
        
        rows = []
        for col in numeric_cols:
            series = filtered[col]
            if series.empty or series.count() == 0:
                continue
            
            idx_min = series.idxmin()
            idx_max = series.idxmax()
            min_ts = filtered_times.get(idx_min, pd.NaT)
            max_ts = filtered_times.get(idx_max, pd.NaT)
            
            # Return in standardized format like simulation adapters
            rows.extend([
                {"project_id": project_id, "column_name": col, "metric": "count", "value": int(series.count()), "unit": "-"},
                {"project_id": project_id, "column_name": col, "metric": "mean", "value": float(series.mean()), "unit": "-"},
                {"project_id": project_id, "column_name": col, "metric": "std", "value": float(series.std()), "unit": "-"},
                {"project_id": project_id, "column_name": col, "metric": "min", "value": float(series.min()), "unit": "-"},
                {"project_id": project_id, "column_name": col, "metric": "min_timestamp", "value": str(min_ts), "unit": "datetime"},
                {"project_id": project_id, "column_name": col, "metric": "max", "value": float(series.max()), "unit": "-"},
                {"project_id": project_id, "column_name": col, "metric": "max_timestamp", "value": str(max_ts), "unit": "datetime"},
            ])
        
        if not rows:
            return {"summary": pd.DataFrame()}
        
        summary_df = pd.DataFrame(rows)
        return {"summary": summary_df}
