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

        # overheating hours room temperature
        setpoint_sia = cfg['simulation_parameters']['overheating_threshold']['value']  # SIA 2024 cooling setpoint
        temperature_air_room = df_raw.loc[:,'temperature_air_room']
        overheating_hours = (temperature_air_room > setpoint_sia).sum()*dt_hours # [h]

        df_summary = pd.DataFrame([
            {"project_id":project_id, "variant_id":variant_id, "end_use":"temperature", "metric":"overheating_hours", "value":overheating_hours, "unit":"h"},
        ])

        return {"summary": df_summary}
