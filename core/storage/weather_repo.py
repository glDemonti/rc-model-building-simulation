import scipy.io as sio
import pandas as pd

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
    

    def write_processed(self, df)
        """
        Writes the processed weather data to a file.
        Path is defined in bootstrap.py
        """
        df.to_parquet(self.processed_path)
    
