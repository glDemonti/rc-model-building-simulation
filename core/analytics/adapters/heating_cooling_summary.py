import pandas as pd

from core.analytics.context import SimulationContext
from core.analytics.adapters.base import BaseAdapter

class HeatingCoolingSummaryAdapter(BaseAdapter):
    """
    Adapter for heating and cooling summary analytics.
    """
    def __init__(self):
        super().__init__(name="heating_cooling_summary", kind="summary")

        self.required_raw_columns = {
            "output_heating_power",
            "output_cooling_power",
            "datetime",
        }

    def compute(self, context: SimulationContext) -> dict:
        df_raw = context.df_raw
        dt_hours = context.dt_hours
        cfg = context.cfg
        project_id = context.project_id
        variant_id = context.variant_id
    
        # summ heating load
        E_heating_kWh = (df_raw.loc[:,'output_heating_power'] * dt_hours).sum() / 1e3 # in kWh
        # summ cooling load
        E_cooling_kWh = (df_raw.loc[:,'output_cooling_power'] * dt_hours).sum() / 1e3 # in kWh
        # max heating power
        max_heating_power = df_raw.loc[:,'output_heating_power'].max() / 1e3 # in kW
        # max cooling power
        max_cooling_power = df_raw.loc[:,'output_cooling_power'].max() / 1e3 # in kW
        # anual costs (heating + cooling)
        anual_heating_cost = E_heating_kWh * cfg['economic_parameters']['heating_price']['value']    # in CHF
        anual_cooling_cost = E_cooling_kWh * cfg['economic_parameters']['cooling_price']['value']    # in CHF

        df_summary = pd.DataFrame([
            {"project_id": project_id, "variant_id": variant_id, "end_use": "heating", "metric": "energy_year", "value": E_heating_kWh, "unit": "kWh"},
            {"project_id": project_id, "variant_id": variant_id, "end_use": "cooling", "metric": "energy_year", "value": E_cooling_kWh, "unit": "kWh"},
            {"project_id": project_id, "variant_id": variant_id, "end_use": "heating", "metrics":"power_max", "value": max_heating_power, "unit": "kW"}

        ])

        return {"summary": df_summary}