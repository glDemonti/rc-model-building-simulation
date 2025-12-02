import pandas as pd
from core.storage.measurements_repo import MeasurementsRepository

class MeasureService:
    def __init__(self, repo:MeasurementsRepository):
        self._repo = repo

    def process_and_store_measurements(self) -> pd.DataFrame:
        df = self._repo.read_raw()
        return df