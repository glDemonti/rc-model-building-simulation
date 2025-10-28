class ConfigFacade:
    """
    
    """
    def __init__(self, repo, engine, evaluator=None, validator=None):
        self._repo = repo
        self._engine = engine
        self._evaluator = evaluator
        self._validator = validator

    def load(self, project_id):

    def set(self, cfg, patch: dict[path -> exp_or_value]):
        
    def validate(self, cfg):

    def save(self, project_id, cfg):

    def to_model_inputs(self, cfg):

    def run(self,cfg):



