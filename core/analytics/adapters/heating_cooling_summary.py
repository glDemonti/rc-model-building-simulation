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
            "datetime"
        }

    def compute(self, context: SimulationContext) -> dict:
        df_raw = context.df_raw
        dt_hours = context.dt_hours
        cfg = context.cfg
    
        # summ heating load
        E_heating_kWh = (df_raw.loc[:,'output_heating_power'] * dt_hours).sum() / 1e3 # in kWh
        # summ cooling load
        E_cooling_kWh = (df_raw.loc[:,'output_cooling_power'] * dt_hours).sum() / 1e3 # in kWh
        # max heating power
        max_heating_power = df_raw.loc[:,'output_heating_power'].max() / 1e3 # in kW
        # max cooling power
        max_cooling_power = df_raw.loc[:,'output_cooling_power'].max() / 1e3 # in kW
        # specific heating load

        
        return df_summary