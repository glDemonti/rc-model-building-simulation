import numpy as np
import pandas as pd
import scipy.io as sio

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
        arrays = {
            'output_temperature': npz['output_temperatures'][:8759,0],  # take only the first column with the Air temperature
            'heating_power': npz['output_heating_power'][:8759],
            'cooling_power': npz['output_cooling_power'][:8759],
            'lighting_electricity': npz['output_lighting_electricity'][:8759],
            'equipment_electricity': npz['output_equipment_electricity'][:8759],
        }

    # find the target length (length of other arrays)
    target_length = arrays['heating_power'].size

    # Truncate temperature array if it's longer than target length
    # if arrays['output_temperature'].size > target_length:
    # arrays['output_temperature'] = arrays['output_temperature'][:target_length]
    
    # Flatten arrays and convert to DataFrame    
    arrays = {name: arr.flatten() for name, arr in arrays.items()}
    df = pd.DataFrame(arrays)
    return df

def load_weather_data():
    """
    Load weather data from a .mat file and return it as a DataFrame.
    
    Returns:
        pd.DataFrame: DataFrame containing weather data.
    """
    weather_data = sio.loadmat('basel_dry_ver2.mat', squeeze_me=True, struct_as_record=False)
    table = np.asarray(weather_data['basel_dry'])  # Convert to numpy array for easier handling
    df_weather = pd.DataFrame({
        'time':table[:8760,0],
        'air_temperature':table[:8760,1],
        'relative_humidity':table[:8760,2],
        'wind_speed_x':table[:8760,3],
        'wind_speed_y':table[:8760,4],
        'direct_sun_radiation':table[:8760,5],
        'diffuse_sun_radiation':table[:8760,6],
        'sky_cover':table[:8760,7],
        'sun_elevation':table[:8760,8],
        'sun_azimuth':table[:8760,9]
    })
    return df_weather

