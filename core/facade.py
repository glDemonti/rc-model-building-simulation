import copy
from dataclasses import dataclass
import pandas as pd
from pathlib import Path

@dataclass
class RunReport:
    ok: bool
    run_id: str
    message: str
    
class ConfigFacade:
    """
    
    """
    def __init__(self, repo, engine, result, evaluator=None, validator=None, mapper=None, analytics=None):
        self._repo = repo
        self._engine = engine
        self._evaluator = evaluator
        self._validator = validator
        self._mapper = mapper
        self._result = result
        self._analytics = analytics

    def load_config(self, project_id) -> dict:
        cfg = self._repo.read_raw()
        return cfg

    # def set(self, cfg: dict, patch: dict) -> EvalReport:
        
    # def validate(self, cfg):

    def save_config(self, project_id, cfg):
        # Evaluate expressions -> values
        cfg_copy = copy.deepcopy(cfg)
        cfg_evaluated, errors = self._evaluator.evaluate_cfg(cfg_copy)
        if errors:
            return False, "Fehler bei der Auswertung: " + "; ".join(errors)
              
       # save
        try:
            self._repo.write_raw(cfg_evaluated)
            return True, "Gespeichert"
        except Exception as e:
            return False, f"Speichern fehlgeschlagen: {e}"

    # def to_model_inputs(self, cfg):

    # def run(self,cfg):
    def get_context(self, project_id: str, variant_id: str):
        if self._analytics is None:
            raise RuntimeError("AnalyticsService not configured in ConfigFacade.")
        
        context = self._analytics.compute_all(project_id, variant_id)
        return context

    def run_simulation(self, project_id: str, variant_id: str, *, force: bool = False) -> RunReport:
        """quick and dirty implementation of start simulation
        """
        
        # start simulation
        df_raw = self._engine.run()
        
        self._result.save_raw(project_id, variant_id, df_raw)

        # return f"Simulation for project {project_id} started."
        return RunReport(
            ok=True,
            run_id="latest",
            message=f"Simulation for project {project_id} and variant {variant_id} completed successfully."
        )

    def latest_run(self, project_id) -> str | None:
        return f"Latest result for project {project_id}."

        # _prepare = 

        # _compute =

        # _persist =
    
    def load_timeseries(self, project_id: str, run_id="latest",) -> pd.DataFrame:
        """
        Transforms the simulationresults in to a DataFrame which contains the outsidetemperature, insidetemperature(room) , heatingpower and coolingpower.
        the return ist a DataFram with the name  
        """
        # return f"Timeseries data for project {project_id}, run {run_id}."
        # Import sim_io_mock from adapters, adjusting sys.path if necessary
        try:
            from adapters import sim_io_mock
        except ModuleNotFoundError:
            import sys, pathlib
            ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root (one above /ui)
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from adapters import sim_io_mock

        df_temperatures = sim_io_mock.make_df_temperatures()
        return df_temperatures

    def load_weatherdata(self, project_id: str) -> pd.DataFrame:
        """
        Loads the weatherdata as a DataFrame for the given project_id.
        """
        # Import sim_io_mock from adapters, adjusting sys.path if necessary
        try:
            from adapters import sim_io_mock
        except ModuleNotFoundError:
            import sys, pathlib
            ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root (one above /ui)
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from adapters import sim_io_mock

        df_weather = sim_io_mock.load_weather_data()
        return df_weather
    
    def load_power_df(self, project_id: str) ->pd.DataFrame:
        """
        Loads the power data as a DataFrame for the given project_id.
        """
        # Import sim_io_mock from adapters, adjusting sys.path if necessary
        try:
            from adapters import sim_io_mock
        except ModuleNotFoundError:
            import sys, pathlib
            ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root (one above /ui)
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from adapters import sim_io_mock

        df_power = sim_io_mock.make_df_loads()
        return df_power
    
    def get_summary(self, project_id: str, variant_id: str, ):
        result = self._analytics.compute_all(project_id, variant_id)
        return result["summary"]