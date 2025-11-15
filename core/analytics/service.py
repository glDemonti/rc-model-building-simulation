import pandas as pd
from core.analytics.context import SimulationContext


class AnalyticsService:
    def __init__(self, config_repo, result_repo, adapters=None):
        self._config_repo = config_repo
        self._result_repo = result_repo
        self._adapters = adapters or []

    def compute_all(self, project_id: str, variant_id: str) -> SimulationContext:
        cfg = self._config_repo.read_raw()
        df_raw = self._result_repo.load_raw(project_id, variant_id)
        if df_raw is None:
            raise RuntimeError(
                f"Keine Rohresultate für Projekt {project_id} und Variante {variant_id} gefunden."
            )
        
        context = SimulationContext(
            project_id=project_id,
            variant_id=variant_id,
            df_raw=df_raw,
            cfg=cfg,
            dt_hours=None  # Placeholder for time step, to be computed if needed