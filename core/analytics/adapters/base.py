
class BaseAdapter:
    def __init__(self, name: str, kind: str) -> None:
        self.name = name
        self.kind = kind
        self.required_raw_columns: set[str] = set()
        self.required_cfg_keys: set[str] = set()


    def compute(self, context: SimulationContext) -> dict:
        """
        Compute analytics based on the provided simulation context.
        Each adapter must override this method.
        """
        raise NotImplementedError
    