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
        # Preserve the uploaded file extension for proper format detection
        target_path = self.raw_path.with_suffix(temp_path.suffix)

        # Ensure target directory exists and remove any existing files (keep folder clean)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        for existing in target_path.parent.iterdir():
            if existing.is_file():
                existing.unlink()

        try:
            shutil.copy(temp_path, target_path)
            # Update raw_path so subsequent reads use the correct file and extension
            self.raw_path = target_path
            print(f"Copied weather data file to {self.raw_path}")
        except FileNotFoundError:
            print(f"Error: Source file not found at {temp_path}")
        except PermissionError:
            print(f"Error: Permission denied when copying to {target_path}")
               

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
        # Auto-detect separator/decimal: assume either ';' with decimal ',' or ',' with decimal '.'
        sample = ''
        try:
            with open(self.raw_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample = ''.join(next(f, '') for _ in range(5))
        except StopIteration:
            pass

        semi = sample.count(';')
        comma = sample.count(',')
        if semi > comma:
            sep, decimal = ';', ','
        else:
            sep, decimal = ',', '.'

        return pd.read_csv(self.raw_path, sep=sep, decimal=decimal, engine='python')
    
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
        # If the configured path does not exist (e.g., after restart), try to find a file
        # with the same stem but any supported suffix in the same folder.
        if not self.raw_path.exists():
            candidates = list(self.raw_path.parent.glob(self.raw_path.stem + ".*"))
            for cand in candidates:
                if cand.suffix.lower() in [".mat", ".csv", ".epw"]:
                    self.raw_path = cand
                    break
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
