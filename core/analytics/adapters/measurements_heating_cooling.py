import pandas as pd

from core.analytics.adapters.base import BaseAdapter

class MeasurementsHeatingCoolingAdapter(BaseAdapter):
    """
    Adapter for computing heating/cooling statistics from measurement data.
    Mirrors the HeatingCoolingSummaryAdapter for simulations.
    
    Column structure by position (names don't matter):
    - Col 0: datetime (Zeitstempel)
    - Col 1: Aussentemperatur
    - Col 2: Raumtemperatur
    - Col 3: Heizleistung (used here)
    - Col 4: Kühlleistung (used here)
    """
    def __init__(self, ebf_area: float = None):
        super().__init__(name="MeasurementsHeatingCooling", kind="measurements")
        self.ebf_area = ebf_area  # Building energy reference area (m²)
        self.required_raw_columns = set()

    def _is_power_column(self, col_name: str) -> bool:
        """Check if column contains power data."""
        return "power" in col_name.lower() or "leistung" in col_name.lower()

    def _is_energy_column(self, col_name: str) -> bool:
        """Check if column contains energy data."""
        return "energy" in col_name.lower() or "energie" in col_name.lower() or "kwh" in col_name.lower()

    def compute(self, df: pd.DataFrame, project_id: str = None, time_column: str = None, date_range: tuple = None, costs_config: dict = None) -> dict:
        """
        Compute heating/cooling statistics for measurement data.
        Uses column positions instead of names.
        
        Args:
            df: Measurement data
            project_id: Project identifier
            time_column: Name of time column
            date_range: Optional (start_date, end_date) filter
            costs_config: Dict with 'heating_price' and 'cooling_price' in CHF/kWh
        
        Returns:
            dict: {"summary": DataFrame with metrics}
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
        # Col 3: Heizleistung, Col 4: Kühlleistung
        power_positions = [3, 4]
        power_names = ["Heizleistung", "Kühlleistung"]
        power_types = ["heating", "cooling"]
        
        rows = []
        dt_hours = 1.0  # Assuming 1-hour timestep
        
        for pos, name, end_use in zip(power_positions, power_names, power_types):
            if pos >= len(df.columns):
                continue
            
            col = df.columns[pos]
            # Convert to numeric, coercing errors
            series = pd.to_numeric(filtered[col], errors="coerce").abs()  # Ensure positive values
            
            if series.empty or series.count() == 0:
                continue
            
            try:
                idx_max = series.idxmax()
                max_ts = filtered_times.loc[idx_max] if pd.notna(idx_max) else pd.NaT
            except Exception:
                max_ts = pd.NaT
            
            # Power metrics
            max_power_kW = float(series.max()) / 1000 if series.max() > 100 else float(series.max())
            mean_power_kW = float(series.mean()) / 1000 if series.mean() > 100 else float(series.mean())
            
            rows.extend([
                {"project_id": project_id, "column_name": name, "metric": "power_mean", "value": mean_power_kW, "unit": "kW"},
                {"project_id": project_id, "column_name": name, "metric": "power_max", "value": max_power_kW, "unit": "kW"},
                {"project_id": project_id, "column_name": name, "metric": "power_max_timestamp", "value": str(max_ts), "unit": "datetime"},
            ])
            
            # Specific load if ebf_area available
            if self.ebf_area:
                spec_load = (max_power_kW * 1000) / self.ebf_area  # W/m²
                rows.append(
                    {"project_id": project_id, "column_name": name, "metric": "load_specific", "value": spec_load, "unit": "W/m²"}
                )
            
            # Energy metrics (assuming power in W)
            energy_kWh = (series * dt_hours).sum() / 1000 if series.max() > 100 else (series * dt_hours).sum()
            
            rows.extend([
                {"project_id": project_id, "column_name": name, "metric": "energy_year", "value": energy_kWh, "unit": "kWh"},
            ])
            
            # Specific energy if ebf_area available
            if self.ebf_area:
                energy_specific = energy_kWh / self.ebf_area
                rows.append(
                    {"project_id": project_id, "column_name": name, "metric": "energy_specific", "value": energy_specific, "unit": "kWh/m²"}
                )
            
            # Costs if pricing available
            if costs_config:
                price_key = f"{end_use}_price"
                if price_key in costs_config:
                    cost = energy_kWh * costs_config[price_key]
                    rows.append(
                        {"project_id": project_id, "column_name": name, "metric": "costs_year", "value": cost, "unit": "CHF"}
                    )
        
        if not rows:
            return {"summary": pd.DataFrame()}
        
        summary_df = pd.DataFrame(rows)
        return {"summary": summary_df}
