import shutil
import pandas as pd
from pathlib import Path


class MeasurementsRepository:
    def __init__(self, path_raw: Path, path_processed: Path):
        self.path_raw = path_raw
        self.path_processed = path_processed

    def write_raw(self, temp_path: Path) -> None:
        """
        Copies the raw input measurement data file from temporary location to the repository location.
        Preserves the uploaded file extension (.csv or .xlsx) for proper format detection.
        If a file already exists at the destination, it will be deleted first.
        Temp path is provided by the upload component in the UI.
        Path of the repository is defined in bootstrap.py
        """
        # Preserve the uploaded file extension for proper format detection
        target_path = self.path_raw.with_suffix(temp_path.suffix)

        # Ensure target directory exists and remove any existing files (keep folder clean)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        for existing in target_path.parent.iterdir():
            if existing.is_file() and existing.suffix.lower() in [".csv", ".xlsx"]:
                existing.unlink()

        try:
            shutil.copy(temp_path, target_path)
            # Update path_raw so subsequent reads use the correct file and extension
            self.path_raw = target_path
            print(f"Copied measurements data file to {self.path_raw}")
        except FileNotFoundError:
            print(f"Error: Source file not found at {temp_path}")
        except PermissionError:
            print(f"Error: Permission denied when copying to {target_path}")

    def read_raw_csv(self):
        """
        Reads the raw .csv measurement data file and returns its content as a DataFrame.
        Path is defined in bootstrap.py
        """
        if not self.path_raw.exists():
            return None
        # Auto-detect separator: assume either ';' with decimal ',' or ',' with decimal '.'
        sample = ''
        try:
            with open(self.path_raw, 'r', encoding='utf-8', errors='ignore') as f:
                sample = ''.join(next(f, '') for _ in range(5))
        except StopIteration:
            pass

        semi = sample.count(';')
        comma = sample.count(',')
        if semi > comma:
            sep, decimal = ';', ','
        else:
            sep, decimal = ',', '.'

        # Read CSV with first row as header, skip row 1 (description/units row)
        df = pd.read_csv(self.path_raw, sep=sep, decimal=decimal, engine='python', header=0, skiprows=[1])
        return df
    
    def read_raw_excel(self):
        """
        Reads the raw .xlsx measurement data file and returns its content as a DataFrame.
        Path is defined in bootstrap.py
        """
        if not self.path_raw.exists():
            return None
        try:
            # Read Excel with string dtype first to prevent Excel auto-formatting issues
            # Use first row as header, skip row 1 (description/units row)
            df = pd.read_excel(self.path_raw, engine='openpyxl', dtype=str, header=0, skiprows=[1])
            
            # Convert numeric columns back to float (skip first column which is timestamp)
            for col in df.columns[1:]:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception:
                    pass  # Keep as string if conversion fails
            
            return df
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}. Please check that all data columns contain numeric values.")
    
    def read_raw(self):
        """Auto-detects file format and reads raw measurement data"""
        # If the configured path does not exist (e.g., after restart), try to find a file
        # with the same stem but any supported suffix in the same folder.
        if not self.path_raw.exists():
            candidates = list(self.path_raw.parent.glob(self.path_raw.stem + ".*"))
            for cand in candidates:
                if cand.suffix.lower() in [".csv", ".xlsx"]:
                    self.path_raw = cand
                    break
            if not self.path_raw.exists():
                return None
        
        file_extension = self.path_raw.suffix.lower()
        
        if file_extension == ".csv":
            return self.read_raw_csv()
        elif file_extension in [".xlsx", ".xls"]:
            return self.read_raw_excel()
        else:
            raise ValueError(f"Unsupported measurement file format: {file_extension}. Supported formats: .csv, .xlsx")

    def save_original_name(self, name):
        """
        Saves the original name of the uploaded measurements data file to a text file.
        Path is defined in bootstrap.py
        """
        orig_name_path = self.path_raw.with_suffix('.txt')
        with open(orig_name_path, 'w') as f:
            f.write(name)

    def get_original_name(self):
        """
        Retrieves the original name of the uploaded measurement file.
        Returns None if no file has been uploaded yet.
        """
        orig_name_path = self.path_raw.with_suffix('.txt')
        if not orig_name_path.exists():
            return None
        try:
            with open(orig_name_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None
