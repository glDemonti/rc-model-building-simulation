import scipy.io as sio
import pandas as pd
from pathlib import Path
import shutil

class WeatherRepository:
    def __init__(self, path_raw: Path, path_processed: Path):
        self.raw_path = path_raw
        self.processed_path = path_processed

    def write_raw(self, temp_path: Path) -> None:
        """
        Copies the raw input wather data file from temporary location to the repository location.
        Temp path is provided by the upload component in the UI.
        Path of the repository is defined in bootstrap.py
        """
        self.raw_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy(temp_path, self.raw_path)
            print(f"Copied weather data file to {self.raw_path}")
        except FileNotFoundError:
            print (f"Error: Source file not found at {temp_path}")
        except PermissionError:
            print (f"Error: Permission denied when copying to {self.raw_path}")
               

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
    
    def save_original_name(self, name: str) -> None:
        """
        Saves the original name of the uploaded weather data file to a text file.
        Path is defined in bootstrap.py
        """
        orig_name_path = self.raw_path.with_suffix('.txt')
        with open(orig_name_path, 'w') as f:
            f.write(name)
