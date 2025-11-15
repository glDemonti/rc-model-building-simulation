
from core.analytics.context import SimulationContext


class AnalyticsService:
    def __init__(self, config_repo, result_repo, adapters):
        self._config_repo = config_repo
        self._result_repo = result_repo
        self._adapters = adapters

    def compute_all(self, project_id: str, variant_id: str) -> SimulationContext:
        context = SimulationContext(
            project_id=project_id,
            variant_id=variant_id,
            df_raw=self._result_repo,
            cfg=self._config_repo,
            dt_hours=None  # Placeholder for time step information
        )
        return context
