from pathlib import Path
import pandas as pd

class ResultRepository:
    def __init__(self, path) -> None:
        self._path = path

    def save_raw(self, df: pd.DataFrame) -> None:
        """
        Saves the raw simulation results (DataFrame) to a parquet file.
        Path is defined in bootstrap.py
        """
        df_raw = df

        # save results
        self._path.parent.mkdir(parents=True, exist_ok=True)
        df_raw.to_parquet(self._path)


    def load_raw(self) -> pd.DataFrame | None:
        """
        Loads the raw simulation results from a parquet file.
        Path is defined in bootstrap.py
        """
        path = self._path
        if not path.exists():
            return None
        df_raw = pd.read_parquet(path)
        return df_raw
