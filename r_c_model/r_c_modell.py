import numpy as np
import scipy.io as sio

# =======================================================
# Parameters and constants for the RC model
# =======================================================

# ------------------------------------------------------
# Definition of areas of building components [m²] in north, east, south, west order
# ------------------------------------------------------

# unshaded glazing area (without permanent obstacles like balconies)
unshaded_glazing_area_n = 0.825 * (2.3 * 12 + 1.2 * 6 + 3 * 2.07)  # North facade  [m²]
unshaded_glazing_area_e = 0.825 * (3.45 * 3 + 2.3 * 3 + 1.98 * 1)   # East facade   [m²]
unshaded_glazing_area_s = 0.825 * (1.73 * 2 + 5.18 * 2 + 1.98 * 4 + 1.2 * 6 + 2.07 * 1)  # South facade  [m²]
unshaded_glazing_area_w = 0.825 * (3.45 * 3 + 2.3 * 3 + 2.07 * 1)  # West facade   [m²]

# shaded glazing area (under permanent obstacles like balconies)
shaded_glazing_area_n = 0.0 # North facade  [m²]
shaded_glazing_area_e = 0.825 * (1.98 + 2) # East facade   [m²]
shaded_glazing_area_s = 0.825 * (1.73 * 4 + 5.18 * 4 + 1.98 * 1) # South facade  [m²]
shaded_glazing_area_w = 0.825 * (2.07 * 2) # West facade   [m²]

# ======================================================
# Load weather data from file
# ======================================================
# load weather data from .mat file
weather_data = sio.loadmat('basel_dry_ver2.mat')

'''
Read weather file from .mat file. 
The data starts from "00:00 18.12.2018" and ends at "23:00 31.12.2019".

The file contains a table with the following columns:
    First column - Time of the year, [hours]
    Second column - air temperature, [C]
    Third column - relative humidity, [%] (currently not used)
    Fourth column - wind speed in X-direction, [m/s] (currently not used)
    Fifth column - wind speed in Y-direction, [m/s] (currently not used)
    Sixth column - direct sun radiation, [W/m^2]
    Seventh column - diffuse sun radiation, [W/m^2]
    Eighth column - sky cover, [] (currently not used)
    Ninth column - sun elevation, [°]
    Tenth column - sun azimuth, [°]
'''

# Extract the main table from the loaded data
table = weather_data['basel_dry']

# access the weather data with validation
try: 
    ambient_temp = table[:, 1]      # Ambient temperature  [°C]
    beam_radiation = table[:, 5]    # Beam radiation       [W/m²]
    diff_radiation = table[:, 6]    # Diffuse radiation    [W/m²]
    sun_elevation = table[:, 8]     # Sun elevation        [°]
    sun_azimuth = table[:, 9]       # Sun azimuth          [°]

    print("\nSuccessfully loaded data:")
    print(f"Ambient temperature shape: {ambient_temp.shape}")
    print(f"First few values:")
    print(f"- Temperature: {ambient_temp[:5]}")
    print(f"- Beam radiation: {beam_radiation[:5]}")
    print(f"- Diffuse radiation: {diff_radiation[:5]}")

except IndexError as e:
    print(f"Error accessing data: {e}")
    print("Please check the structure of the loaded .mat file.")
    print("possible causes:")
    print("- Table has fewer columns than expected")
    print("- Data structure is not as expected")