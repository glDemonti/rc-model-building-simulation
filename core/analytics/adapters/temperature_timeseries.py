import pandas as pd

from core.analytics.context import SimulationContext
from core.analytics.adapters.base import BaseAdapter

class TemperatureTimeseriesAdapter(BaseAdapter):
    """
    Adapter for temperature timeseries.
    """
    def __init__(self):
        super().__init__(name="temperature_timeseries", kind="timeseries")

        self.required_raw_columns = {
            # "datetime",
            "temperature_air_room",
            "temperature_outdoor_air",
        }

    def compute(self, context:SimulationContext) -> dict:
        df_raw = context.df_raw

        df_ts_temp = pd.DataFrame({
            "datetime": df_raw.index,
            "project_id": context.project_id,
            "variant_id": context.variant_id,
            "temp_air_room": df_raw["temperature_air_room"],        # room air temperature [°C]
            "temp_outdoor_air": df_raw["temperature_outdoor_air"]   # outdoor air temperature [°C]
        })

        return {"timeseries": df_ts_temp}