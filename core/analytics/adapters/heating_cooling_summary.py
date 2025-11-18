import pandas as pd

class HeatingCoolingSummaryAdapter:
    """
    Adapter for heating and cooling summary analytics.
    """

    def compute(self, context: SimulationContext) -> dict:
        df_raw = context.df_raw
        dt_hours = context.dt_hours
        cfg = context.cfg
    
    # summ heating load
    E_heating_kWh = (df_raw.loc[:,'output_heating_power'] * dt_hours).sum() / 1e6 # in MWh
    # summ cooling load
    E_cooling_kWh = (df_raw.loc[:,'output_cooling_power'] * dt_hours).sum() / 1e6 # in MWh
    # max heating power
    max_heating_power = df_raw.loc[:,'output_heating_power'].max() / 1e3 # in kW
    # max cooling power
    max_cooling_power = df_raw.loc[:,'output_cooling_power'].max() / 1e3 # in kW
    
    return df_summary