import copy
from dataclasses import dataclass
import pandas as pd

@dataclass
class RunReport:
    ok: bool
    run_id: str
    message: str
    
class ConfigFacade:
    """
    
    """
    def __init__(self, repo, engine, evaluator=None, validator=None, mapper=None):
        self._repo = repo
        self._engine = engine
        self._evaluator = evaluator
        self._validator = validator
        self._mapper = mapper

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

    def run_simulation(self, project_id: str, *, force: bool = False) -> RunReport:
        return f"Simulation for project {project_id} started."

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