import pandas as pd
from core.storage.weather_repo import WeatherRepository

class WeatherService:

    def __init__(self, repo: WeatherRepository):
        self._repo = repo

    def load_weather(self) -> pd.DataFrame:
        raw = self._repo.read_raw_mat()
        if raw is None:
            raise RuntimeError(f"Weather data file not found at {self._repo.raw_path}")
        
        weather_df = self._to_dataframe(raw)

        # Save processed data for future use
        self._repo.write_processed(weather_df)

        return weather_df
    
    
    def _to_dataframe(self, raw) -> pd.DataFrame:
        # Extract table from mat file
        table= raw['basel_dry']

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