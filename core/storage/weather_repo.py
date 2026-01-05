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
        If a file already exists at the destination, it will be deleated first.
        Temp path is provided by the upload component in the UI.
        Path of the repository is defined in bootstrap.py
        """
        self.raw_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if self.raw_path.exists():
                self.raw_path.unlink() # delete existing file
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
    
    def read_raw_csv(self):
        """
        Reads the raw .csv weather data file and returns its content as a DataFrame.
        Path is defined in bootstrap.py
        """
        if not self.raw_path.exists():
            return None
        return pd.read_csv(self.raw_path)
    
    def read_raw_epw(self):
        """
        Reads the raw .epw weather data file and returns its content as a DataFrame.
        Path is defined in bootstrap.py
        """
        if not self.raw_path.exists():
            return None
        # EPW files have a header of 8 lines, skip them
        return pd.read_csv(
            self.raw_path,
            skiprows=8,
            header=None,
            names=list(range(35))  # EPW files have 35 columns
        )
    
    def read_raw(self):
        """Auto-detects file format and reads raw weather data"""
        if not self.raw_path.exists():
            return None
        
        file_extension = self.raw_path.suffix.lower()
        
        if file_extension == ".mat":
            return self.read_raw_mat()
        elif file_extension == ".csv":
            return self.read_raw_csv()
        elif file_extension == ".epw":
            return self.read_raw_epw()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def read_processed(self):
        """
        Reads the processed weather data from a file.
        Path is defined in bootstrap.py
        """
        if not self.processed_path.exists():
            return None
        
        return pd.read_parquet(self.processed_path)

    def write_processed(self, df: pd.DataFrame) -> None:
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
