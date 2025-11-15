import pandas as pd

class SimulationContext:
    def __init__(self, project_id: str, variant_id: str, df_raw: pd.DataFrame, cfg: dict, dt_hours: float | None):
        self.project_id = project_id
        self.variant_id = variant_id
        self.df_raw = df_raw
        self.cfg = cfg
        self.dt_hours = dt_hours