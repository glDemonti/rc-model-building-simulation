import pandas as pd
from core.analytics.context import SimulationContext


class AnalyticsService:
    def __init__(self, config_repo, result_repo, adapters: list):
        self._config_repo = config_repo
        self._result_repo = result_repo
        self._adapters = adapters

    def compute_all(self, project_id: str, variant_id: str) -> dict:
        # load config
        cfg = self._config_repo.read_raw()
        # load raw results
        df_raw = self._result_repo.load_raw()
        if df_raw is None:
            raise RuntimeError(
                f"Keine Rohresultate für Projekt {project_id} und Variante {variant_id} gefunden."
            )
        
        # TODO: add Timestep computation if needed
        # dt_hours = (df_raw["datetime"].iloc[1]-df_raw["datetime"].iloc[0]).total_seconds() / 3600
        dt_hours = 1.0  # timestep of 1h
        # build context
        context = SimulationContext(
            project_id=project_id,
            variant_id=variant_id,
            df_raw=df_raw,
            cfg=cfg,
            dt_hours=dt_hours  # Placeholder for time step, to be computed if needed
        )


        # summary adapters
        all_summaries = []
        all_timeseries = []
        all_monthly_timeseries = []

        for adapter in self._adapters:
            missing_cols = adapter.required_raw_columns - set(context.df_raw.columns)
            if missing_cols:
                raise RuntimeError(
                    f"Adapter '{adapter.name}' benötigt fehlende Spalten in Rohdaten: {missing_cols}"
                )

            results = adapter.compute(context)

            df_summary = results.get("summary")
            if df_summary is not None and not df_summary.empty:
                all_summaries.append(df_summary)
            
            df_timeseries = results.get("timeseries")
            if df_timeseries is not None and not df_timeseries.empty:
                all_timeseries.append(df_timeseries)

            df_monthly_timeseries = results.get("monthly_timeseries")
            if df_monthly_timeseries is not None and not df_monthly_timeseries.empty:
                all_monthly_timeseries.append(df_monthly_timeseries)

        print(df_monthly_timeseries)
        if all_summaries:
            summary_df = pd.concat(all_summaries, ignore_index=True)
        else:
            summary_df = pd.DataFrame()

        if all_timeseries:
            ts = pd.concat(all_timeseries, axis=1, join="inner")
            ts = ts.loc[:, ~ts.columns.duplicated()]
            timeseries_df = ts
        else:
            timeseries_df = pd.DataFrame()

        if all_monthly_timeseries:
            mt = pd.concat(all_monthly_timeseries, axis=1, join="inner")
            mt = mt.loc[:, ~mt.columns.duplicated()]
            monthly_timeseries_df = mt


        return {
            "context": context,
            "summary": summary_df,
            "timeseries": timeseries_df,
            "monthly_timeseries": monthly_timeseries_df
        }
