import numpy as np
import scipy.io as sio

# Parameters and constants for the RC model
# =======================================================

# Load weather data from file
# ======================================================
# load weather data from .mat file
weather_data = sio.loadmat('basel_dry_ver2.mat')

# Extract the main table from the loaded data
table = weather_data['basel_dry']  

# access the weather data with validation
try: 
    ambient_temp = table[:, 1]      # Ambient temperature  [°C]
    beam_radiation = table[:, 5]    # Beam radiation       [W/m²]
    difd_radiation = table[:, 6]    # Diffuse radiation    [W/m²]
    sun_elevation = table[:, 8]     # Sun elevation        [°]
    sun_azimuth = table[:, 9]       # Sun azimuth          [°]

    print("\nSuccessfully loaded data:")
    print(f"Ambient temperature shape: {ambient_temp.shape}")
    print(f"First few values:")
    print(f"- Temperature: {ambient_temp[:5]}")
    print(f"- Beam radiation: {beam_radiation[:5]}")
    print(f"- Diffuse radiation: {difd_radiation[:5]}")

except IndexError as e:
    print(f"Error accessing data: {e}")
    print("Please check the structure of the loaded .mat file.")
    print("possible causes:")
    print("- Table has fewer columns than expected")
    print("- Data structure is not as expected")