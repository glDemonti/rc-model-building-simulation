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
            'Innentemperatur Verglasung Nord': npz['output_temperatures'][:,1],  # take the second column with the Glazing temperature internal north
            'Innentemperatur Verglasung Ost': npz['output_temperatures'][:,2],  # take the third column with the Glazing temperature internal east
            'Innentemperatur Verglasung Süd': npz['output_temperatures'][:,3],  # take the fourth column with the Glazing temperature internal south
            'Innentemperatur Verglasung West': npz['output_temperatures'][:,4],  # take the fifth column with the Glazing temperature internal west
            'Aussentemperatur Verglasung Nord': npz['output_temperatures'][:,5],  # take the sixth column with the Glazing temperature external north
            'Aussentemperatur Verglasung Ost': npz['output_temperatures'][:,6],  # take the seventh column with the Glazing temperature external east
            'Aussentemperatur Verglasung Süd': npz['output_temperatures'][:,7],  # take the eighth column with the Glazing temperature external south
            'Aussentemperatur Verglasung West': npz['output_temperatures'][:,8],  # take the ninth column with the Glazing temperature external west
            'Inenntemperatur Fensterrahmen Nord': npz['output_temperatures'][:,9],  # take the tenth column with the Window frame temperature internal north
            'Inenntemperatur Fensterrahmen Ost': npz['output_temperatures'][:,10],  # take the eleventh column with the Window frame temperature internal east
            'Inenntemperatur Fensterrahmen Süd': npz['output_temperatures'][:,11],  # take the twelfth column with the Window frame temperature internal south
            'Inenntemperatur Fensterrahmen West': npz['output_temperatures'][:,12],  # take the thirteenth column with the Window frame temperature internal west
            'Aussentemperatur Fensterrahmen Nord': npz['output_temperatures'][:,13],  # take the fourteenth column with the Window frame temperature external north
            'Aussentemperatur Fensterrahmen Ost': npz['output_temperatures'][:,14],  # take the fifteenth column with the Window frame temperature external east
            'Aussentemperatur Fensterrahmen Süd': npz['output_temperatures'][:,15],  # take the sixteenth column with the Window frame temperature external south
            'Aussentemperatur Fensterrahmen West': npz['output_temperatures'][:,16],  # take the seventeenth column with the Window frame temperature external west
            'Temperatur 1. Knoten Aussenwand Nord': npz['output_temperatures'][:,17],  # take the eighteenth column with the Temperature 1st node external wall north
            'Temperatur 1. Knoten Aussenwand Ost': npz['output_temperatures'][:,18],  # take the nineteenth column with the Temperature 1st node external wall east
            'Temperatur 1. Knoten Aussenwand Süd': npz['output_temperatures'][:,19],  # take the twentieth column with the Temperature 1st node external wall south
            'Temperatur 1. Knoten Aussenwand West': npz['output_temperatures'][:,20],  # take the twenty-first column with the Temperature 1st node external wall west
            'Temperatur 1. Knoten Dach': npz['output_temperatures'][:,21],  # take the twenty-second column with the Temperature 1st node roof
            'Temperatur 1. Knoten Boden': npz['output_temperatures'][:,22],  # take the twenty-third column with the Temperature 1st node floor
            'Temperatur 1. Knoten Innenwand': npz['output_temperatures'][:,23],  # take the twenty-fourth column with the Temperature 1st node internal wall
            'Temperatur 1. Knoten Innendecke': npz['output_temperatures'][:,24],  # take the twenty-fifth column with the Temperature 1st node internal ceiling
            'Temperatur 2. Knoten Aussenwand Nord': npz['output_temperatures'][:,25],  # take the twenty-sixth column with the Temperature 2nd node external wall north
            'Temperatur 2. Knoten Aussenwand Ost': npz['output_temperatures'][:,26],  # take the twenty-seventh column with the Temperature 2nd node external wall east
            'Temperatur 2. Knoten Aussenwand Süd': npz['output_temperatures'][:,27],  # take the twenty-eighth column with the Temperature 2nd node external wall south
            'Temperatur 2. Knoten Aussenwand West': npz['output_temperatures'][:,28],  # take the twenty-ninth column with the Temperature 2nd node external wall west
            'Temperatur 2. Knoten Dach': npz['output_temperatures'][:,29],  # take the thirtyieth column with the Temperature 2nd node roof
            'Temperatur 2. Knoten Boden': npz['output_temperatures'][:,30],  # take the thirty-first column with the Temperature 2nd node floor
            'Temperatur 2. Knoten Innenwand': npz['output_temperatures'][:,31],  # take the thirty-second column with the Temperature 2nd node internal wall
            'Temperatur 2. Knoten Innendecke': npz['output_temperatures'][:,32],  # take the thirty-third column with the Temperature 2nd node internal ceiling
            'Temperatur 3. Knoten Aussenwand Nord': npz['output_temperatures'][:,33],  # take the thirty-fourth column with the Temperature 3rd node external wall north
            'Temperatur 3. Knoten Aussenwand Ost': npz['output_temperatures'][:,34],  # take the thirty-fifth column with the Temperature 3rd node external wall east
            'Temperatur 3. Knoten Aussenwand Süd': npz['output_temperatures'][:,35],  # take the thirty-sixth column with the Temperature 3rd node external wall south
            'Temperatur 3. Knoten Aussenwand West': npz['output_temperatures'][:,36],  # take the thirty-seventh column with the Temperature 3rd node external wall west
            'Temperatur 3. Knoten Dach': npz['output_temperatures'][:,37],  # take the thirty-eighth column with the Temperature 3rd node roof
            'Temperatur 3. Knoten Boden': npz['output_temperatures'][:,38],  # take the thirty-ninth column with the Temperature 3rd node floor
            'Temperatur 3. Knoten Innenwand': npz['output_temperatures'][:,39],  # take the fortieth column with the Temperature 3rd node internal wall
            'Temperatur 3. Knoten Innendecke': npz['output_temperatures'][:,40],  # take the forty-first column with the Temperature 3rd node internal ceiling
            'Temperatur 4. Knoten Aussenwand Nord': npz['output_temperatures'][:,41],  # take the forty-second column with the Temperature 4th node external wall north
            'Temperatur 4. Knoten Aussenwand Ost': npz['output_temperatures'][:,42],  # take the forty-third column with the Temperature 4th node external wall east
            'Temperatur 4. Knoten Aussenwand Süd': npz['output_temperatures'][:,43],  # take the forty-fourth column with the Temperature 4th node external wall south
            'Temperatur 4. Knoten Aussenwand West': npz['output_temperatures'][:,44],  # take the forty-fifth column with the Temperature 4th node external wall west
            'Temperatur 4. Knoten Dach': npz['output_temperatures'][:,45],  # take the forty-sixth column with the Temperature 4th node roof
            'Temperatur 4. Knoten Boden': npz['output_temperatures'][:,46],  # take the forty-seventh column with the Temperature 4th node floor
            'Temperatur 4. Knoten Innenwand': npz['output_temperatures'][:,47],  # take the forty-eighth column with the Temperature 4th node internal wall
            'Temperatur 4. Knoten Innendecke': npz['output_temperatures'][:,48],  # take the forty-ninth column with the Temperature 4th node internal ceiling
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
    df =  pd.merge(df_sim[["datetime",
                            # "Innenlufttemperatur", 
                            'Innentemperatur Verglasung Nord',
                            'Innentemperatur Verglasung Ost',
                            'Innentemperatur Verglasung Süd', 
                            'Innentemperatur Verglasung West',
                            'Aussentemperatur Verglasung Nord',
                            'Aussentemperatur Verglasung Ost',
                            'Aussentemperatur Verglasung Süd',
                            'Aussentemperatur Verglasung West',
                            'Inenntemperatur Fensterrahmen Nord',
                            'Inenntemperatur Fensterrahmen Ost',
                            'Inenntemperatur Fensterrahmen Süd', 
                            'Inenntemperatur Fensterrahmen West',
                            'Aussentemperatur Fensterrahmen Nord',
                            'Aussentemperatur Fensterrahmen Ost',
                            'Aussentemperatur Fensterrahmen Süd',
                            'Aussentemperatur Fensterrahmen West',
                            "Temperatur 1. Knoten Aussenwand Nord",
                            "Temperatur 1. Knoten Aussenwand Ost",
                            "Temperatur 1. Knoten Aussenwand Süd",
                            "Temperatur 1. Knoten Aussenwand West",
                            "Temperatur 1. Knoten Dach",
                            "Temperatur 1. Knoten Boden",
                            "Temperatur 1. Knoten Innenwand",
                            "Temperatur 1. Knoten Innendecke",
                            "Temperatur 2. Knoten Aussenwand Nord",
                            "Temperatur 2. Knoten Aussenwand Ost",
                            "Temperatur 2. Knoten Aussenwand Süd",
                            "Temperatur 2. Knoten Aussenwand West",
                            "Temperatur 2. Knoten Dach",
                            "Temperatur 2. Knoten Boden",
                            "Temperatur 2. Knoten Innenwand",
                            "Temperatur 2. Knoten Innendecke",
                            "Temperatur 3. Knoten Aussenwand Nord",
                            "Temperatur 3. Knoten Aussenwand Ost",
                            "Temperatur 3. Knoten Aussenwand Süd",
                            "Temperatur 3. Knoten Aussenwand West",
                            "Temperatur 3. Knoten Dach",
                            "Temperatur 3. Knoten Boden",
                            "Temperatur 3. Knoten Innenwand",
                            "Temperatur 3. Knoten Innendecke",
                            "Temperatur 4. Knoten Aussenwand Nord",
                            "Temperatur 4. Knoten Aussenwand Ost",
                            "Temperatur 4. Knoten Aussenwand Süd",
                            "Temperatur 4. Knoten Aussenwand West",
                            "Temperatur 4. Knoten Dach",
                            "Temperatur 4. Knoten Boden",
                            "Temperatur 4. Knoten Innenwand",
                            "Temperatur 4. Knoten Innendecke",
                            

                            ]],
                   df_weather[["datetime", "Aussenlufttemperatur"]],
                   on="datetime", how="inner"
                   )
    df = df.sort_values(by="datetime").dropna(subset=["datetime"])
    return df

