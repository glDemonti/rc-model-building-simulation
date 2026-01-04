import pandas as pd

from core.analytics.context import SimulationContext
from core.analytics.adapters.base import BaseAdapter

class TemperatureSummaryAdapter(BaseAdapter):
    """
    Adapter for temperature summary analytics.
    """
    def __init__(self):
        super().__init__(name="TemperatureSummary", kind="summary")

        self.required_raw_columns = {
            "temperature_air_room",
            #"datetime",
        }

    def compute(self, context: SimulationContext) -> dict:
        df_raw = context.df_raw
        dt_hours = context.dt_hours
        cfg = context.cfg
        project_id = context.project_id
        variant_id = context.variant_id

        # overheating hours roomtemperature
        temperature_air_room = df_raw.loc[:,'temperature_air_room']
        temperatur_setpoint_cooling = cfg['simulation_parameters']['cooling_setpoint']['value']
        overheating_hours = (temperature_air_room > temperatur_setpoint_cooling).sum()*dt_hours # [h]

        # max outdoor temperature
        temp_outdoor_max = df_raw.loc[:,'temperature_outdoor_air'].max()  # max outdoor temperature
        timestamp_temp_outdoor_max = df_raw.loc[:,'temperature_outdoor_air'].idxmax()

        # min outdoor temperature
        temp_outdoor_min = df_raw.loc[:,'temperature_outdoor_air'].min()  # min outdoor temperature
        timestamp_temp_outdoor_min = df_raw.loc[:,'temperature_outdoor_air'].idxmin()

        df_summary = pd.DataFrame([
            {"project_id":project_id, "variant_id":variant_id, "end_use":"temperature", "metric":"overheating_hours", "value":overheating_hours, "unit":"h"},
            {"project_id":project_id, "variant_id":variant_id, "end_use":"temperature", "metric":"temp_outdoor_max", "value":temp_outdoor_max, "unit":"°C"},
            {"project_id":project_id, "variant_id":variant_id, "end_use":"temperature", "metric":"temp_outdoor_min", "value":temp_outdoor_min, "unit":"°C"},
            {"project_id":project_id, "variant_id":variant_id, "end_use":"temperature", "metric":"timestamp_temp_outdoor_max", "value":timestamp_temp_outdoor_max, "unit":"index"},
            {"project_id":project_id, "variant_id":variant_id, "end_use":"temperature", "metric":"timestamp_temp_outdoor_min", "value":timestamp_temp_outdoor_min, "unit":"index"},
        ])

        return {"summary": df_summary}
