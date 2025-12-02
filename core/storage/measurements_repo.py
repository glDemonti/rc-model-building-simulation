import shutil
import pandas as pd
from pathlib import Path


class MeasurementsRepository:
    def __init__(self, path_raw: Path, path_processed: Path):
        self.path_raw = path_raw
        self.path_processed = path_processed

    def write_raw(self, temp_path: Path):
        self.path_raw.parent.mkdir(parents=True, exist_ok=True)
        try:
            if self.path_raw.exists():
                self.path_raw.unlink()  # delete existing file
            shutil.copy(temp_path, self.path_raw)
            print(f"Copied measurements data file to {self.path_raw}")
        except FileNotFoundError:
            print(f"Error: Source file not found at {temp_path}")
        except PermissionError:
            print(f"Error: Permission denied when copying to {self.path_raw}")

    def read_raw(self):
        if not self.path_raw.exists():
            return None
        return pd.read_csv(self.path_raw)

    def safe_original_name(self, name):
        """
        Saves the original name of the uploaded measurements data file to a text file.
        Path is defined in bootstrap.py


        """
        orig_name_path = self.path_raw.with_suffix('.txt')
        with open(orig_name_path, 'w') as f:
            f.write(name)