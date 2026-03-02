import pandas as pd
import numpy as np
from core.storage.weather_repo import WeatherRepository
from core.solar_utils import (
    SolarLocationManager,
    SolarPositionCalculator,
    SolarRadiationDecomposition,
)


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
            raise RuntimeError(
                f"Weather data file not found at {self._repo.processed_path}"
            )
        return df

    def process_and_store_weather(
        self,
        cfg: dict = None,
        processing_mode: str = "auto",
        verlaufzeit_enable: bool = False,
        verlaufzeit_days: float = 14,
    ) -> pd.DataFrame:
        """
        Reads the raw weather data file, processes it into a DataFrame,
        and stores the processed data.
        Supports .mat, .csv, .epw, and climate_station formats.

        Args:
            cfg: Configuration dict containing weather_start_date (EPW)
                 and location (all formats)
            processing_mode: CSV handling mode:
                - "auto": detect climate-station format automatically
                - "standardized": file already has required 10 columns
                - "calculate_missing": compute missing columns from
                  climate station input
            verlaufzeit_enable: Whether to prepend settling time
            verlaufzeit_days: Number of days to prepend from end
        """
        raw = self._repo.read_raw()
        if raw is None:
            raise RuntimeError(
                f"Raw weather data file not found at {self._repo.raw_path}"
            )

        # Get location from config or use defaults
        location_manager = (
            SolarLocationManager.from_config(cfg)
            if cfg
            else SolarLocationManager()
        )

        # Determine format based on return type from repository
        if isinstance(raw, dict):
            # MATLAB .mat file (returned as dict)
            df = self._mat_to_dataframe(raw, location_manager)
        elif isinstance(raw, pd.DataFrame):
            # CSV or EPW file (returned as DataFrame)
            file_extension = self._repo.raw_path.suffix.lower()
            if file_extension == ".csv":
                if processing_mode == "standardized":
                    df = self._csv_to_dataframe(raw, location_manager)
                elif processing_mode == "calculate_missing":
                    df = self._climate_station_to_dataframe(
                        raw,
                        location_manager,
                    )
                else:
                    # Auto-detect if it's climate station or standard CSV
                    is_climate_station = self._is_climate_station_format(raw)
                    if is_climate_station:
                        df = self._climate_station_to_dataframe(
                            raw,
                            location_manager,
                        )
                    else:
                        df = self._csv_to_dataframe(raw, location_manager)
            elif file_extension == ".epw":
                # EPW requires config for start_date
                start_date = None
                if cfg:
                    try:
                        start_date_str = (
                            cfg.get("simulation_parameters", {})
                            .get("weather_start_date", {})
                            .get("value")
                            or cfg.get("simulation_parameters", {})
                            .get("weather_start_date", {})
                            .get("expression")
                        )
                        if start_date_str:
                            start_date = pd.Timestamp(start_date_str)
                    except Exception as e:
                        print(
                            f"Warning: Could not parse weather_start_date "
                            f"from config: {e}"
                        )

                if start_date is None:
                    raise ValueError(
                        "EPW files require weather_start_date to be "
                        "configured in simulation_parameters"
                    )

                df = self._epw_to_dataframe(raw, start_date, location_manager)
            else:
                raise ValueError(
                    f"Unsupported file format: {file_extension}"
                )
        else:
            raise ValueError(
                f"Unexpected data type from read_raw(): {type(raw)}"
            )

        # Apply Verlaufzeit (settling time) if enabled
        if verlaufzeit_enable and verlaufzeit_days > 0:
            df = self._apply_verlaufzeit(df, verlaufzeit_days)

        self._repo.write_processed(df)
        return df

    def _apply_verlaufzeit(
        self, df: pd.DataFrame, verlaufzeit_days: float
    ) -> pd.DataFrame:
        """
        Apply settling time (Verlaufzeit) by prepending the last N days
        of data to the beginning.

        This allows the building thermal model to reach equilibrium
        before the actual simulation period starts.

        Args:
            df: Input DataFrame with datetime index
            verlaufzeit_days: Number of days to prepend from the end

        Returns:
            DataFrame with prepended settling period
        """
        # Calculate number of hours to prepend
        verlaufzeit_hours = int(verlaufzeit_days * 24)

        if len(df) < verlaufzeit_hours:
            print(
                f"Warning: Verlaufzeit ({verlaufzeit_days} days) is longer "
                f"than data length ({len(df)} hours). Using full dataset."
            )
            verlaufzeit_hours = len(df)

        # Extract the last N hours to prepend
        settling_data = df.iloc[-verlaufzeit_hours:].copy()

        # Calculate time offset for settling period
        # We want settling period to come before the main data
        if len(df) > 1:
            time_step = df.index[1] - df.index[0]
        else:
            time_step = pd.Timedelta(hours=1)
        settling_start = df.index[0] - time_step * verlaufzeit_hours

        # Create new datetime index for settling period
        settling_index = pd.date_range(
            start=settling_start,
            periods=verlaufzeit_hours,
            freq=time_step
        )
        settling_data.index = settling_index

        # Update timestamp column if it exists
        if "timestamp" in settling_data.columns:
            # Make timestamps negative for settling period
            settling_data["timestamp"] = np.arange(
                -verlaufzeit_hours, 0
            )

        # Concatenate settling period with main data
        df_with_verlaufzeit = pd.concat([settling_data, df])

        print(
            f"Applied Verlaufzeit: {verlaufzeit_days} days "
            f"({verlaufzeit_hours} hours) prepended"
        )

        return df_with_verlaufzeit

    def _is_climate_station_format(self, df: pd.DataFrame) -> bool:
        """
        Detect if a CSV DataFrame is in climate station format.

        Checks for German column names or expected climate station patterns.
        """
        if df.empty:
            return False

        columns_lower = [col.lower() for col in df.columns]

        # German climate station indicators
        german_indicators = [
            "temperatur",
            "feuchte",
            "windrichtung",
            "windstärke",
            "strahlung",
            "druck",
            "dämmerung",
        ]

        found_indicators = sum(
            1 for indicator in german_indicators
            if indicator in columns_lower
        )

        # If 3+ German columns found, it's likely a climate station
        return found_indicators >= 3

    def _mat_to_dataframe(
        self, raw, location_manager: SolarLocationManager = None
    ) -> pd.DataFrame:
        """
        Convert MATLAB .mat file to standardized DataFrame.
        Parses the timestamp column directly from the file.

        Args:
            raw: MATLAB .mat file data
            location_manager: SolarLocationManager for sun calculations
        """
        if location_manager is None:
            location_manager = SolarLocationManager()

        # Extract table from mat file
        key = next(k for k in raw.keys() if not k.startswith("__"))
        table = raw[key]

        # define column names
        columns = [
            "timestamp",  # time of the year, [hours]
            "air_temperature",  # air temperatur, [°C]
            "relative_humidity",  # relative humidity, [%]
            "wind_speed_x",  # wind speed in x direction, [m/s]
            "wind_speed_y",  # wind speed in y direction, [m/s]
            "solar_radiation_direct",  # direct solar radiation, [W/m2]
            "solar_radiation_diffuse",  # diffuse solar radiation, [W/m2]
            "sky_cover",  # sky cover, [%]
            "sun_elevation",  # sun elevation angle, [°]
            "sun_azimuth",  # sun azimuth angle, [°]
        ]
        # Create DataFrame.
        df = pd.DataFrame(table[:, : len(columns)], columns=columns)

        # Parse timestamp column as datetime
        df["datetime"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("datetime")
        df = df.drop("timestamp", axis=1)

        return df

    def _csv_to_dataframe(
        self, df: pd.DataFrame,
        location_manager: SolarLocationManager = None
    ) -> pd.DataFrame:
        """
        Convert CSV DataFrame to standardized format.
        Parses the timestamp column directly from the file.

        Args:
            df: Input DataFrame from CSV
            location_manager: SolarLocationManager for sun calculations
        """
        if location_manager is None:
            location_manager = SolarLocationManager()

        # Take only the first 10 columns (by position, not name)
        columns = [
            "timestamp",  # time of the year, [hours]
            "air_temperature",  # air temperatur, [°C]
            "relative_humidity",  # relative humidity, [%]
            "wind_speed_x",  # wind speed in x direction, [m/s]
            "wind_speed_y",  # wind speed in y direction, [m/s]
            "solar_radiation_direct",  # direct solar radiation, [W/m2]
            "solar_radiation_diffuse",  # diffuse solar radiation, [W/m2]
            "sky_cover",  # sky cover, [%]
            "sun_elevation",  # sun elevation angle, [°]
            "sun_azimuth",  # sun azimuth angle, [°]
        ]

        df = df.iloc[:, : len(columns)]
        df.columns = columns

        # Parse timestamp column as datetime
        df["datetime"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("datetime")
        df = df.drop("timestamp", axis=1)

        return df

    def _climate_station_to_dataframe(
        self, df: pd.DataFrame, location_manager: SolarLocationManager
    ) -> pd.DataFrame:
        """
        Convert climate station CSV to standardized format.

        Expects German column names and handles flexible column mapping.
        Required columns: Temperatur, Feuchte, Windstärke,
        Windrichtung, Strahlung Referenz/Global

        Args:
            df: Input DataFrame from climate station CSV
                with German headers
            location_manager: SolarLocationManager with station coordinates

        Returns:
            Standardized DataFrame with all required weather parameters
        """
        # Map German column names (case-insensitive) to standard fields
        columns_lower = {col.lower(): col for col in df.columns}

        # Extract required columns with flexible naming
        def get_column_value(df, possible_names):
            """Get column data using multiple possible names."""
            for name in possible_names:
                if name.lower() in columns_lower:
                    return df[columns_lower[name.lower()]].astype(float)
            raise ValueError(
                f"Required column not found. Tried: {possible_names}"
            )

        air_temperature = get_column_value(
            df, ["temperatur", "temperature", "temp"]
        )
        relative_humidity = get_column_value(
            df, ["feuchte", "humidity", "relative humidity"]
        )
        wind_speed = get_column_value(
            df, ["windstärke", "wind speed", "windspeed"]
        )
        wind_direction = get_column_value(
            df,
            ["windrichtung", "wind direction", "wind_direction"]
        )

        # Solar radiation - try multiple names
        global_radiation = get_column_value(
            df,
            [
                "strahlung referenz",
                "global radiation",
                "global_radiation",
                "strahlung global",
                "globalstrahlung",
            ],
        )

        # Create datetime index - assume hourly data
        # If there's a datetime column, use it
        datetime_col = None
        for possible_name in ["datum", "time", "datetime", "timestamp"]:
            if possible_name.lower() in columns_lower:
                datetime_col = columns_lower[possible_name.lower()]
                break

        if datetime_col:
            dt = pd.to_datetime(df[datetime_col])
        else:
            # No datetime column - assume hourly data for one year
            # starting Jan 1
            start_date = pd.Timestamp("2018-01-01 00:00:00")
            dt = pd.date_range(start=start_date, periods=len(df), freq="h")

        # Calculate wind components
        wind_direction_rad = np.radians(wind_direction)
        wind_speed_x = wind_speed * np.cos(wind_direction_rad)
        wind_speed_y = wind_speed * np.sin(wind_direction_rad)

        # Calculate sun position
        calculator = SolarPositionCalculator(
            location_manager.latitude, location_manager.longitude
        )
        sun_elevation = calculator.calculate_sun_elevation(dt)
        sun_azimuth = calculator.calculate_sun_azimuth(dt)

        # Decompose radiation using Erbs model
        (
            solar_radiation_direct,
            solar_radiation_diffuse,
        ) = SolarRadiationDecomposition.decompose_global_radiation(
            global_radiation.values, sun_elevation, dt
        )

        # Sky cover: estimate from diffuse fraction (optional)
        # Set to 0 if not available
        sky_cover = np.full(len(df), 0.0)

        # Build standardized DataFrame
        df_weather = pd.DataFrame(
            {
                "timestamp": np.arange(len(df)),  # sequential hours
                "air_temperature": air_temperature.values,
                "relative_humidity": relative_humidity.values,
                "wind_speed_x": wind_speed_x.values,
                "wind_speed_y": wind_speed_y.values,
                "solar_radiation_direct": solar_radiation_direct,
                "solar_radiation_diffuse": solar_radiation_diffuse,
                "sky_cover": sky_cover,
                "sun_elevation": sun_elevation,
                "sun_azimuth": sun_azimuth,
                "datetime": dt,
            }
        )

        # Set datetime as index
        df_weather = df_weather.set_index("datetime")

        return df_weather

    def _epw_to_dataframe(
        self,
        df: pd.DataFrame,
        start_date: pd.Timestamp = None,
        location_manager: SolarLocationManager = None,
    ) -> pd.DataFrame:
        """
        Convert EnergyPlus .epw DataFrame to standardized format.
        Uses Erbs model for radiation decomposition and
        location-aware sun calculations.

        Args:
            df: Input DataFrame from EPW
            start_date: Start date for datetime index
                (default: 2018-12-18 00:00:00)
            location_manager: SolarLocationManager for location-aware
                calculations
        """
        if location_manager is None:
            location_manager = SolarLocationManager()

        # Column mapping (0-based indices per EPW spec)
        # Note: EPW provides direct normal radiation
        # 0 Year, 1 Month, 2 Day, 3 Hour(1-24), 4 Minute,
        # 6 Dry Bulb Temp [°C], 8 Rel. Humidity [%],
        # 14 Direct Normal Radiation [W/m²],
        # 15 Diffuse Horizontal Radiation [W/m²],
        # 20 Wind Direction [deg], 21 Wind Speed [m/s],
        # 22 Total Sky Cover [%]

        air_temperature = df.iloc[:, 6].astype(float)
        relative_humidity = df.iloc[:, 8].astype(float)
        solar_radiation_direct = df.iloc[:, 14].astype(float)
        solar_radiation_diffuse = df.iloc[:, 15].astype(float)
        wind_direction = df.iloc[:, 20].astype(float)
        wind_speed = df.iloc[:, 21].astype(float)
        sky_cover = (
            df.iloc[:, 22].astype(float)
            if df.shape[1] > 22
            else np.full(len(df), 0.0)
        )

        # Use configurable start date for consistency across variants
        # This allows user to align different weather files on timeline
        start = (
            start_date
            if start_date is not None
            else pd.Timestamp("2018-12-18 00:00:00")
        )
        dt = pd.date_range(start=start, periods=len(df), freq="h")

        # Calculate wind components from speed and direction
        wind_direction_rad = np.radians(wind_direction)
        wind_speed_x = wind_speed * np.cos(wind_direction_rad)
        wind_speed_y = wind_speed * np.sin(wind_direction_rad)

        # Calculate sun position using location-aware calculator
        calculator = SolarPositionCalculator(
            location_manager.latitude, location_manager.longitude
        )
        sun_elevation = calculator.calculate_sun_elevation(dt)
        sun_azimuth = calculator.calculate_sun_azimuth(dt)

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
        df_weather = df_weather.dropna(
            subset=["datetime"]
        ).set_index("datetime")

        return df_weather
