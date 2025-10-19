import numpy as np
import pandas as pd
import scipy.io as sio

t_0 = pd.Timestamp('2023-01-01 00:00:00')
def date_range(n_hours):
    return pd.date_range(start=t_0, periods=n_hours, freq='h')

def load_sim_results():
    """
    Load simulation results from a .npz file and return the output temperatures.

    Args:
        None
    
    Returns:
        np.ndarray: Array of simulation results.

        todo: adjust if output results from file will have the right length
    """
    # Load the .npz file and extract the simulation results
    with np.load("adapters/py_out.npz") as npz:
        arrs = {
            # 'datetime': date_range(),  # generate datetime index
            'Innenlufttemperatur': npz['output_temperatures'][:,0],  # take only the first column with the Air temperature
            'heating_power': npz['output_heating_power'],
            'cooling_power': npz['output_cooling_power'],
            'lighting_electricity': npz['output_lighting_electricity'],
            'equipment_electricity': npz['output_equipment_electricity'],
        }
    # Find the minimum length among all arrays to ensure they can be combined into a DataFrame
    n = min(int(np.asarray(v).size) for v in arrs.values())
    arrs = {k: np.asarray(v).reshape(-1)[:n] for k, v in arrs.items()}

    df = pd.DataFrame(arrs)   
    df.insert(0, 'datetime', date_range(n)) # insert datetime as first column
    for c in df.columns:
        if c != 'datetime':
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df


def load_weather_data():
    """
    Load weather data from a .mat file and return it as a DataFrame.
    
    Returns:
        pd.DataFrame: DataFrame containing weather data.
    """
    weather_data = sio.loadmat('basel_dry_ver2.mat', squeeze_me=True, struct_as_record=False)
    table = np.asarray(weather_data['basel_dry'])  # Convert to numpy array for easier handling
    time_idx = table[:8760,0].astype(int)  # Extract time index (first column)
    df_weather = pd.DataFrame({
        'datetime': t_0 + pd.to_timedelta(time_idx - 1, unit='h'),
        'Aussenlufttemperatur':table[:8760,1],
        'relative_humidity':table[:8760,2],
        'wind_speed_x':table[:8760,3],
        'wind_speed_y':table[:8760,4],
        'direct_sun_radiation':table[:8760,5],
        'diffuse_sun_radiation':table[:8760,6],
        'sky_cover':table[:8760,7],
        'sun_elevation':table[:8760,8],
        'sun_azimuth':table[:8760,9]
    })
    for c in df_weather.columns:
        if c != 'datetime':
            df_weather[c] = pd.to_numeric(df_weather[c], errors='coerce')
    return df_weather


def make_df_temperatures():
    df_sim = load_sim_results()
    df_weather = load_weather_data()
    # Merge simulation and weather data on datetime
    df =  pd.merge(df_sim[["datetime", "Innenlufttemperatur"]],
                   df_weather[["datetime", "Aussenlufttemperatur"]],
                   on="datetime", how="inner"
                   )
    df = df.sort_values(by="datetime").dropna(subset=["datetime"])
    return df

