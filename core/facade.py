import copy

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

    def load(self, project_id) -> dict:
        cfg = self._repo.read_raw()
        return cfg

    # def set(self, cfg: dict, patch: dict) -> EvalReport:
        
    # def validate(self, cfg):

    def save(self, project_id, cfg):
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

        _prepare = 

        _compute =

        _persist =
    
    def load_timeseries(self, project_id: str, run_id="latest",) -> pd.DataFrame:
        return f"Timeseries data for project {project_id}, run {run_id}."
