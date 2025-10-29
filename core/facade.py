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

    # def save(self, project_id, cfg):

    # def to_model_inputs(self, cfg):

    # def run(self,cfg):


