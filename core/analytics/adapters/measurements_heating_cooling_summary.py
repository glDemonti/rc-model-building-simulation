import pandas as pd

from core.analytics.adapters.base import BaseAdapter


class MeasurementsHeatingCoolingSummaryAdapter(BaseAdapter):
    """
    Adapter for computing heating/cooling KPI summary from measurement data.
    Mirrors the HeatingCoolingSummaryAdapter structure for simulations.
    
    Expected input format:
    - Temperatures in °C
    - Power values in W (Watt)
    - Cooling can be positive or negative (absolute value is used)
    
    Column structure by position (names don't matter):
    - Col 0: datetime (Zeitstempel)
    - Col 1: Aussentemperatur [°C]
    - Col 2: Raumtemperatur [°C]
    - Col 3: Heizleistung [W]
    - Col 4: Kühlleistung [W] (can be positive or negative)
    
    KPIs calculated (used in UI):
    - energy_year: Annual energy consumption [kWh]
    - power_max: Maximum power [kW]
    - power_max_timestamp: Timestamp of maximum power
    - load_specific: Specific load [W/m²]
    - energy_specific: Specific energy [kWh/m²]
    - costs_year: Annual costs [CHF]
    """

    def __init__(self, ebf_area: float = None):
        super().__init__(
            name="MeasurementsHeatingCoolingSummary", kind="measurements"
        )
        self.ebf_area = ebf_area  # Building energy reference area (m²)
        self.required_raw_columns = set()

    def compute(
        self,
        df: pd.DataFrame,
        project_id: str = None,
        time_column: str = None,
        date_range: tuple = None,
        costs_config: dict = None,
    ) -> dict:
        """
        Compute heating/cooling KPIs for measurement data.
        Uses column positions instead of names.
        
        Args:
            df: Measurement data
            project_id: Project identifier
            time_column: Name of time column
            date_range: Optional (start_date, end_date) filter
            costs_config: Dict with 'heating_price' and 'cooling_price'
        
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
                mask &= (
                    times
                    <= pd.to_datetime(end_date)
                    + pd.Timedelta(days=1)
                    - pd.Timedelta(milliseconds=1)
                )

        filtered = df.loc[mask].copy()
        filtered_times = times.loc[mask]

        # Ensure chronological order for robust delta computation
        try:
            order = filtered_times.sort_values().index
            filtered = filtered.loc[order]
            filtered_times = filtered_times.loc[order]
        except Exception:
            pass

        if filtered.empty:
            return {"summary": pd.DataFrame()}

        # Use fixed column positions:
        # Col 3: Heizleistung, Col 4: Kühlleistung
        power_positions = [3, 4]
        power_names = ["Heizleistung", "Kühlleistung"]
        power_types = ["heating", "cooling"]

        rows = []
        # Compute per-step duration to next timestamp in hours
        dt_to_next_h = (
            filtered_times.shift(-1) - filtered_times
        ).dt.total_seconds() / 3600.0
        if dt_to_next_h.notna().any():
            median_dt = (
                float(dt_to_next_h.dropna().median())
                if dt_to_next_h.dropna().size
                else 1.0
            )
            dt_to_next_h = dt_to_next_h.fillna(median_dt).clip(lower=0)
        else:
            # If we cannot compute deltas, fallback to 1h
            dt_to_next_h = pd.Series(1.0, index=filtered.index)

        for pos, name, end_use in zip(
            power_positions, power_names, power_types
        ):
            if pos >= len(df.columns):
                continue

            col = df.columns[pos]
            # Convert to numeric and take absolute value (cooling can be + or -)
            # REQUIRED: Input must be in W (Watt) - no unit detection
            series = pd.to_numeric(filtered[col], errors="coerce").abs()

            if series.empty or series.count() == 0:
                continue

            try:
                idx_max = series.idxmax()
                max_ts = (
                    filtered_times.loc[idx_max]
                    if pd.notna(idx_max)
                    else pd.NaT
                )
            except Exception:
                max_ts = pd.NaT

            # Power metrics: input in W, output in kW
            max_power_kW = float(series.max()) / 1000.0

            rows.extend(
                [
                    {
                        "project_id": project_id,
                        "column_name": name,
                        "metric": "power_max",
                        "value": max_power_kW,
                        "unit": "kW",
                    },
                    {
                        "project_id": project_id,
                        "column_name": name,
                        "metric": "power_max_timestamp",
                        "value": str(max_ts),
                        "unit": "datetime",
                    },
                ]
            )

            # Specific load if ebf_area available
            if self.ebf_area:
                spec_load = (max_power_kW * 1000.0) / self.ebf_area  # W/m²
                rows.append(
                    {
                        "project_id": project_id,
                        "column_name": name,
                        "metric": "load_specific",
                        "value": spec_load,
                        "unit": "W/m²",
                    }
                )

            # Energy metrics: integrate power[W] over time[h] -> Wh, /1000 -> kWh
            energy_kWh = float((series * dt_to_next_h).sum() / 1000.0)

            rows.extend(
                [
                    {
                        "project_id": project_id,
                        "column_name": name,
                        "metric": "energy_year",
                        "value": energy_kWh,
                        "unit": "kWh",
                    },
                ]
            )

            # Specific energy if ebf_area available
            if self.ebf_area:
                energy_specific = energy_kWh / self.ebf_area
                rows.append(
                    {
                        "project_id": project_id,
                        "column_name": name,
                        "metric": "energy_specific",
                        "value": energy_specific,
                        "unit": "kWh/m²",
                    }
                )

            # Costs if pricing available and > 0
            if costs_config:
                price_key = f"{end_use}_price"
                if price_key in costs_config and costs_config[price_key] > 0:
                    cost = energy_kWh * costs_config[price_key]
                    rows.append(
                        {
                            "project_id": project_id,
                            "column_name": name,
                            "metric": "costs_year",
                            "value": cost,
                            "unit": "CHF",
                        }
                    )

        if not rows:
            return {"summary": pd.DataFrame()}

        summary_df = pd.DataFrame(rows)
        return {"summary": summary_df}
