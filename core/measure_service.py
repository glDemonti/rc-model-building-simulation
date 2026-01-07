import pandas as pd
from core.storage.measurements_repo import MeasurementsRepository

class MeasureService:
    def __init__(self, repo:MeasurementsRepository):
        self._repo = repo

    def process_and_store_measurements(self) -> pd.DataFrame:
        df = self._repo.read_raw()
        self._validate_dataframe(df)
        return df

    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """
        Validate basic structure of measurement data by position.
        
        Expected column structure (by position, not by name):
        - Col 0: datetime - Zeitstempel (Datum/Zeit)
        - Col 1: numeric - Aussentemperatur
        - Col 2: numeric - Raumtemperatur
        - Col 3: numeric - Heizleistung
        - Col 4: numeric - Kühlleistung
        
        Column names are irrelevant - position is what matters!
        
        The user is responsible for providing correctly formatted data
        in the correct order for accurate analysis.
        """
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("Die Messdaten-Datei ist leer oder ungültig.")

        # Check we have at least 5 columns
        if len(df.columns) < 5:
            raise ValueError(
                f"Die Datei hat zu wenige Spalten ({len(df.columns)}). "
                "Erwartet mindestens 5 Spalten: Datum/Zeit, Aussentemperatur, Raumtemperatur, Heizleistung, Kühlleistung"
            )

        # Check first column is time-like
        time_col = df.columns[0]
        times = pd.to_datetime(df[time_col], errors="coerce", dayfirst=True)
        if times.isna().all():
            raise ValueError(
                f"Spalte 1 ('{time_col}') enthält keine gültigen Zeitstempel. "
                "Erwartet z.B. 'dd.mm.yyyy HH:MM' oder ISO-Format."
            )

        # Check columns 2-5 are numeric
        for i in range(1, 5):
            col = df.columns[i]
            # Try to convert to numeric
            numeric_check = pd.to_numeric(df[col], errors="coerce")
            if numeric_check.isna().all():
                raise ValueError(
                    f"Spalte {i+1} ('{col}') enthält keine numerischen Werte. "
                    f"Erwartung für Position {i+1}: {'Aussentemperatur' if i==1 else 'Raumtemperatur' if i==2 else 'Heizleistung' if i==3 else 'Kühlleistung'}"
                )