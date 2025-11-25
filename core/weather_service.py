import scipy.io as sio
import pandas as pd
from pathlib import Path

class WeatherService:

    def __init__(self, repo: WeatherRepository):
        self._repo = repo

    def load_weather(self, project_id: str) -> pd.DataFrame:
        raw = self._repo.read_raw_mat(project_id)
        weather_df = self._to_dataframe(raw)

        # Save processed data for future use
        self._repo.write_processed(weather_df)

        return weather_df
    
    
    def _to_datafram(self, raw)
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
        df = pd.DataFrame(raw, columns)

        return df