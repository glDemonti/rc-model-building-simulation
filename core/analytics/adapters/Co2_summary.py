import pandas as pd

from core.analytics.context import SimulationContext
from core.analytics.adapters.base import BaseAdapter

class Co2SummaryAdapter(BaseAdapter):
    """
    Adapter for CO2 summary analytics.
    """
    def __init__(self):
        super().__init__(name="co2_summary", kind="summary")

        self.required_raw_columns = {
            "output_heating_power",
            "output_cooling_power",
            # "datetime",
        }

    def compute(self, context: SimulationContext) -> dict:
        df_raw = context.df_raw.copy()
        dt_hours = context.dt_hours
        cfg = context.cfg
        project_id = context.project_id
        variant_id = context.variant_id

        # sum CO2 emissions
        CO2_total_cooling = (df_raw.loc[:,'output_cooling_power'].abs() * dt_hours).sum() / 1e3 * cfg["Co2_emission_factors"]["cooling"]["value"] # in kg
        CO2_total_heating = (df_raw.loc[:,'output_heating_power'] * dt_hours).sum() / 1e3 * cfg["Co2_emission_factors"]["heating"]["value"] # in kg
        CO2_total_kg = CO2_total_cooling + CO2_total_heating    # in kg

        # specific CO2 emissions
        CO2_spec_kg_per_m2 = CO2_total_kg / cfg['building_geometry']['enclosure']['ebf_area']['value'] # in kg/m²

        df_summary = pd.DataFrame([
            {"project_id": project_id, "variant_id": variant_id, "end_use": "heating", "metric": "co2_year", "value": CO2_total_heating, "unit": "kg"},
            {"project_id": project_id, "variant_id": variant_id, "end_use": "cooling", "metric": "co2_year", "value": CO2_total_cooling, "unit": "kg"},
            {"project_id": project_id, "variant_id": variant_id, "end_use": "total", "metric": "co2_total_year", "value": CO2_total_kg, "unit": "kg"},
        ])

        return {"summary": df_summary}