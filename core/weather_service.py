import pandas as pd
from pathlib import Path
from core.storage.weather_repo import WeatherRepository

class WeatherService:

    def __init__(self, repo: WeatherRepository):
        self._repo = repo

    def load_weather(self) -> pd.DataFrame:
        """
        Loads the processed weather data from the repository.
        Used for the simulation.
        """
        df = self._repo.read_processed()
        if df is None:
            raise RuntimeError(f"Weather data file not found at {self._repo.processed_path}")
        return df
    
    def process_and_store_weather(self) -> pd.DataFrame:
        """
        Reads the raw weather data file, processes it into a DataFrame, and stores the processed data.
        Supports .mat, .csv, and .epw formats.
        """
        raw = self._repo.read_raw()
        if raw is None:
            raise RuntimeError(f"Raw weather data file not found at {self._repo.raw_path}")
        
        # Determine format based on return type from repository
        if isinstance(raw, dict):
            # MATLAB .mat file (returned as dict)
            df = self._mat_to_dataframe(raw)
        elif isinstance(raw, pd.DataFrame):
            # CSV or EPW file (returned as DataFrame)
            file_extension = self._repo.raw_path.suffix.lower()
            if file_extension == ".csv":
                df = self._csv_to_dataframe(raw)
            elif file_extension == ".epw":
                df = self._epw_to_dataframe(raw)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        else:
            raise ValueError(f"Unexpected data type from read_raw(): {type(raw)}")
        
        self._repo.write_processed(df)
        return df

    def _mat_to_dataframe(self, raw) -> pd.DataFrame:
        """Convert MATLAB .mat file to standardized DataFrame"""
        # Extract table from mat file
        key = next(k for k in raw.keys() if not k.startswith("__"))
        table = raw[key]

        # define column names
        columns = [
            "timestamp",                # time of the year, [hours]
            "air_temperature",          # air temperatur, [°C]
            "relative_humidity",        # relative humidity, [%]
            "wind_speed_x",             # wind speed in x direction, [m/s]
            "wind_speed_y",             # wind speed in y direction, [m/s]
            "solar_radiation_direct",   # direct solar radiation, [W/m2]
            "solar_radiation_diffuse",  # diffuse solar radiation, [W/m2]
            "sky_cover",                # sky cover, [%]
            "sun_elevation",            # sun elevation angle, [°]
            "sun_azimuth"               # sun azimuth angle, [°]
            ]
        # Create DataFrame. 
        df = pd.DataFrame(table[:, :len(columns)], columns=columns)

        # Convert timestamp to datetime
        start = pd.Timestamp("2018-12-18 00:00:00")
        df['datetime'] = pd.date_range(start=start, periods=len(df), freq='h')
        df = df.set_index('datetime')

        return df

    def _csv_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert CSV DataFrame to standardized format"""
        # Take only the first 10 columns (by position, not name)
        columns = [
            "timestamp",                # time of the year, [hours]
            "air_temperature",          # air temperatur, [°C]
            "relative_humidity",        # relative humidity, [%]
            "wind_speed_x",             # wind speed in x direction, [m/s]
            "wind_speed_y",             # wind speed in y direction, [m/s]
            "solar_radiation_direct",   # direct solar radiation, [W/m2]
            "solar_radiation_diffuse",  # diffuse solar radiation, [W/m2]
            "sky_cover",                # sky cover, [%]
            "sun_elevation",            # sun elevation angle, [°]
            "sun_azimuth"               # sun azimuth angle, [°]
            ]
        
        df = df.iloc[:, :len(columns)]
        df.columns = columns
        
        # Convert timestamp to datetime
        start = pd.Timestamp("2018-12-18 00:00:00")
        df['datetime'] = pd.date_range(start=start, periods=len(df), freq='h')
        df = df.set_index('datetime')
        
        return df

    def _epw_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert EnergyPlus .epw DataFrame to standardized format (per EPW spec)."""
        import numpy as np

        # Column mapping (0-based indices per EPW spec)
        # 0 Year, 1 Month, 2 Day, 3 Hour(1-24), 4 Minute,
        # 6 Dry Bulb Temp [°C], 8 Rel. Humidity [%],
        # 14 Direct Normal Radiation [W/m²], 15 Diffuse Horizontal Radiation [W/m²],
        # 20 Wind Direction [deg], 21 Wind Speed [m/s],
        # 22 Total Sky Cover [%] (fallback if needed)

        year = df.iloc[:, 0]
        month = df.iloc[:, 1]
        day = df.iloc[:, 2]
        hour = df.iloc[:, 3]
        minute = df.iloc[:, 4]

        air_temperature = df.iloc[:, 6]
        relative_humidity = df.iloc[:, 8]
        solar_radiation_direct = df.iloc[:, 14]
        solar_radiation_diffuse = df.iloc[:, 15]
        wind_direction = df.iloc[:, 20]
        wind_speed = df.iloc[:, 21]
        sky_cover = df.iloc[:, 22] if df.shape[1] > 22 else 0

        # Convert to datetime; EPW hours are 1-24 -> shift to 0-23 by subtracting 1 hour
        dt = pd.to_datetime(
            {
                "year": year.astype(int),
                "month": month.astype(int),
                "day": day.astype(int),
                "hour": (hour.astype(int) - 1).clip(lower=0),
                "minute": minute.astype(int),
            },
            errors="coerce",
        )

        # Calculate wind components from speed and direction
        wind_direction_rad = np.radians(wind_direction)
        wind_speed_x = wind_speed * np.cos(wind_direction_rad)
        wind_speed_y = wind_speed * np.sin(wind_direction_rad)

        # Build standardized DataFrame
        df_weather = pd.DataFrame(
            {
                "timestamp": np.arange(len(df)),  # sequential hours
                "air_temperature": air_temperature,
                "relative_humidity": relative_humidity,
                "wind_speed_x": wind_speed_x,
                "wind_speed_y": wind_speed_y,
                "solar_radiation_direct": solar_radiation_direct,
                "solar_radiation_diffuse": solar_radiation_diffuse,
                "sky_cover": sky_cover,
                "sun_elevation": 0.0,  # not present in EPW
                "sun_azimuth": 0.0,    # not present in EPW
                "datetime": dt,
            }
        )

        # Set datetime as index; drop rows with invalid datetime
        df_weather = df_weather.dropna(subset=["datetime"]).set_index("datetime")

        return df_weather