import pandas as pd

from core.analytics.context import SimulationContext
from core.analytics.adapters.base import BaseAdapter

class HeatingCoolingMonthTimeseriesAdapter(BaseAdapter):
    """
    Adapter for heating and cooling month timeseries analytics.
    """
    def __init__(self):
        super().__init__(name="heating_cooling_month_timeseries", kind="timeseries")

        self.required_raw_columns = {
            "output_heating_power",
            "output_cooling_power",
            # "datetime",
        }

    def compute(self, context: SimulationContext) -> dict:
        df_raw = context.df_raw.copy()
        monthly_heat = df_raw['output_heating_power'].resample('M').sum() * context.dt_hours / 1e3  # kWh
        monthly_cool = df_raw['output_cooling_power'].abs().resample('M').sum() * context.dt_hours / 1e3  # kWh

        df_ts_pow_monthly = pd.DataFrame({
            "datetime": monthly_heat.index,
            "project_id": context.project_id,
            "variant_id": context.variant_id,
            "heating_energy_kWh": monthly_heat.values,
            "cooling_energy_kWh": monthly_cool.values
        })

        return {"month_timeseries": df_ts_pow_monthly}