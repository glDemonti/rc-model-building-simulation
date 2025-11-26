import scipy.io as sio
import pandas as pd
from pathlib import Path

class WeatherRepository:
    def __init__(self, path_raw: Path, path_processed: Path):
        self.raw_path = path_raw
        self.processed_path = path_processed

    def read_raw_mat(self):
        """
        Reads the raw .mat weather data file and returns its content.
        Path is defined in bootstrap.py
        """
        if not self.raw_path.exists():
            return None
        
        return sio.loadmat(self.raw_path)
    
    def read_processed(self):
        """
        Reads the processed weather data from a file.
        Path is defined in bootstrap.py
        """
        if not self.processed_path.exists():
            return None
        
        return pd.read_parquet(self.processed_path)

    def write_processed(self, df) -> None:
        """
        Writes the processed weather data to a file.
        Path is defined in bootstrap.py
        """
        self.processed_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(self.processed_path)
    
