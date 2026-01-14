import pandas as pd
import numpy as np
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
    
    def process_and_store_weather(self, cfg: dict = None) -> pd.DataFrame:
        """
        Reads the raw weather data file, processes it into a DataFrame, and stores the processed data.
        Supports .mat, .csv, and .epw formats.
        
        Args:
            cfg: Configuration dict containing weather_start_date (required only for EPW files)
        """
        raw = self._repo.read_raw()
        if raw is None:
            raise RuntimeError(f"Raw weather data file not found at {self._repo.raw_path}")
        
        # Determine format based on return type from repository
        if isinstance(raw, dict):
            # MATLAB .mat file (returned as dict) - uses fixed reference date
            df = self._mat_to_dataframe(raw)
        elif isinstance(raw, pd.DataFrame):
            # CSV or EPW file (returned as DataFrame)
            file_extension = self._repo.raw_path.suffix.lower()
            if file_extension == ".csv":
                # CSV uses fixed reference date
                df = self._csv_to_dataframe(raw)
            elif file_extension == ".epw":
                # EPW requires config for start_date
                start_date = None
                if cfg:
                    try:
                        start_date_str = cfg.get("simulation_parameters", {}).get("weather_start_date", {}).get("value") or \
                                         cfg.get("simulation_parameters", {}).get("weather_start_date", {}).get("expression")
                        if start_date_str:
                            start_date = pd.Timestamp(start_date_str)
                    except Exception as e:
                        print(f"Warning: Could not parse weather_start_date from config: {e}")
                
                if start_date is None:
                    raise ValueError("EPW files require weather_start_date to be configured in simulation_parameters")
                
                df = self._epw_to_dataframe(raw, start_date)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        else:
            raise ValueError(f"Unexpected data type from read_raw(): {type(raw)}")
        
        self._repo.write_processed(df)
        return df

    def _mat_to_dataframe(self, raw) -> pd.DataFrame:
        """Convert MATLAB .mat file to standardized DataFrame.
        Parses the timestamp column directly from the file.
        
        Args:
            raw: MATLAB .mat file data
        """
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

        # Parse timestamp column as datetime
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('datetime')
        df = df.drop('timestamp', axis=1)

        return df

    def _csv_to_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert CSV DataFrame to standardized format.
        Parses the timestamp column directly from the file.
        
        Args:
            df: Input DataFrame from CSV
        """
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
        
        # Parse timestamp column as datetime
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('datetime')
        df = df.drop('timestamp', axis=1)
        
        return df

    def _epw_to_dataframe(self, df: pd.DataFrame, start_date: pd.Timestamp = None) -> pd.DataFrame:
        """Convert EnergyPlus .epw DataFrame to standardized format (per EPW spec).
        Matches the same data extraction as .mat files to ensure consistency.
        
        Args:
            df: Input DataFrame from EPW
            start_date: Optional start date for datetime index when EPW calendar is not used (default: 2018-12-18 00:00:00)
        """
        import numpy as np

        # Column mapping (0-based indices per EPW spec)
        # 0 Year, 1 Month, 2 Day, 3 Hour(1-24), 4 Minute,
        # 6 Dry Bulb Temp [°C], 8 Rel. Humidity [%],
        # 14 Direct Normal Radiation [W/m²], 15 Diffuse Horizontal Radiation [W/m²],
        # 20 Wind Direction [deg], 21 Wind Speed [m/s],
        # 22 Total Sky Cover [%] (fallback if needed)

        air_temperature = df.iloc[:, 6].astype(float)
        relative_humidity = df.iloc[:, 8].astype(float)
        solar_radiation_direct = df.iloc[:, 14].astype(float)
        solar_radiation_diffuse = df.iloc[:, 15].astype(float)
        wind_direction = df.iloc[:, 20].astype(float)
        wind_speed = df.iloc[:, 21].astype(float)
        sky_cover = df.iloc[:, 22].astype(float) if df.shape[1] > 22 else np.full(len(df), 0.0)

        # Use configurable start date instead of EPW calendar for consistency across variants
        # This allows user to align different weather files on the same timeline
        start = start_date if start_date is not None else pd.Timestamp("2018-12-18 00:00:00")
        dt = pd.date_range(start=start, periods=len(df), freq="h")

        # Calculate wind components from speed and direction (same as .mat file decomposition)
        wind_direction_rad = np.radians(wind_direction)
        wind_speed_x = wind_speed * np.cos(wind_direction_rad)
        wind_speed_y = wind_speed * np.sin(wind_direction_rad)

        # Calculate sun elevation and azimuth using simplified solar position algorithm
        # This provides consistent values between .mat and .epw formats
        sun_elevation = self._calculate_sun_elevation(dt)
        sun_azimuth = self._calculate_sun_azimuth(dt)

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
                "sun_elevation": sun_elevation,
                "sun_azimuth": sun_azimuth,
                "datetime": dt,
            }
        )

        # Set datetime as index; drop rows with invalid datetime
        df_weather = df_weather.dropna(subset=["datetime"]).set_index("datetime")

        return df_weather

    def _calculate_sun_elevation(self, datetimes: pd.DatetimeIndex) -> np.ndarray:
        """Calculate solar elevation angle using simplified solar position algorithm.
        
        Args:
            datetimes: Sequence of datetime values aligned with the weather records
            
        Returns:
            Array of sun elevation angles in degrees
        """
        import numpy as np

        dates = pd.DatetimeIndex(datetimes)

        # Basel, Switzerland coordinates
        latitude = 47.5596
        longitude = 7.5922

        # Calculate day of year
        day_of_year = dates.dayofyear.values

        # Simplified calculation using standard solar equations
        # Declination angle
        B = 360.0 * (day_of_year - 1) / 365.0
        B_rad = np.radians(B)
        declination = 23.45 * np.sin(B_rad)

        # Time offset based on provided datetimes
        time_offset = dates.hour + dates.minute / 60.0
        hour_angle = 15.0 * (time_offset - 12.0) + (longitude - 15.0)

        # Solar elevation angle
        lat_rad = np.radians(latitude)
        decl_rad = np.radians(declination)
        hour_angle_rad = np.radians(hour_angle)

        sin_elev = np.sin(lat_rad) * np.sin(decl_rad) + np.cos(lat_rad) * np.cos(decl_rad) * np.cos(hour_angle_rad)
        elevation = np.degrees(np.arcsin(np.clip(sin_elev, -1, 1)))

        return elevation
    
    def _calculate_sun_azimuth(self, datetimes: pd.DatetimeIndex) -> np.ndarray:
        """Calculate solar azimuth angle using simplified solar position algorithm.
        
        Args:
            datetimes: Sequence of datetime values aligned with the weather records
            
        Returns:
            Array of sun azimuth angles in degrees (0=North, 90=East, 180=South, 270=West)
        """
        import numpy as np

        dates = pd.DatetimeIndex(datetimes)

        # Basel, Switzerland coordinates
        latitude = 47.5596
        longitude = 7.5922

        # Calculate day of year
        day_of_year = dates.dayofyear.values

        # Simplified calculation using standard solar equations
        # Declination angle
        B = 360.0 * (day_of_year - 1) / 365.0
        B_rad = np.radians(B)
        declination = 23.45 * np.sin(B_rad)

        # Time offset based on provided datetimes
        time_offset = dates.hour + dates.minute / 60.0
        hour_angle = 15.0 * (time_offset - 12.0) + (longitude - 15.0)

        # Solar azimuth angle
        lat_rad = np.radians(latitude)
        decl_rad = np.radians(declination)
        hour_angle_rad = np.radians(hour_angle)

        # Azimuth calculation (0=North, increases clockwise)
        numerator = np.sin(hour_angle_rad)
        denominator = np.sin(lat_rad) * np.cos(hour_angle_rad) - np.cos(lat_rad) * np.tan(decl_rad)
        azimuth = np.degrees(np.arctan2(numerator, denominator))
        azimuth = (azimuth + 180) % 360  # Convert to 0-360 range

        return azimuth