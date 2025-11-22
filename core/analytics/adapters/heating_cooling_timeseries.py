import pandas as pd

from core.analytics.context import SimulationContext
from core.analytics.adapters.base import BaseAdapter

class HeatingCoolingTimeseriesAdapter(BaseAdapter):
    """
    Adapter for heating and cooling timeseries.
    """

    def __init__(self):
        super().__init__(name="heating_cooling_timeseries", kind="timeseries")

        self.required_raw_columns = {
            "output_heating_power",
            "output_cooling_power",
            #"datetime",
        }

    def compute(self, context: SimulationContext) -> dict:
        df_raw = context.df_raw

        df_ts_power = pd.DataFrame({
            # "datetime": df_raw["datetime"],
            "project_id": context.project_id,
            "variant_id": context.variant_id,
            "heating_power": df_raw["output_heating_power"],
            "cooling_power": df_raw["output_cooling_power"]
        })

        return {"timeseries": df_ts_power}