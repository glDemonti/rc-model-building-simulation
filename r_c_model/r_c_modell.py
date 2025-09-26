import numpy as np
import scipy.io as sio

# =======================================================
#  Parameters and constants for the RC model
# =======================================================

# ------------------------------------------------------
# region: Definition of areas of building components [m²] in north, east, south, west order
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

# unshaded window frame area (without permanent obstacles like balcony)
unshaded_frame_area_n = 0.175 * (2.3 * 12 + 1.2 * 6 + 3 * 2.07)   # North facade  [m²]
unshaded_frame_area_e = 0.175 * (3.45 * 3 + 2.3 * 3 + 1.98 * 1)   # East facade   [m²]
unshaded_frame_area_s = 0.175 * (1.73 * 2 + 5.18 * 2 + 1.98 * 4 + 1.2 * 6 + 2.07 * 1)  # South facade  [m²]
unshaded_frame_area_w = 0.175 * (3.45 * 3 + 2.3 * 3 + 2.07 * 1)  # West facade   [m²]

# shaded window frame area (under permanent obstacles like balconies)
shaded_frame_area_n = 0.0  # North facade  [m²]
shaded_frame_area_e = 0.175 * (1.98 * 2)  # East facade   [m²]
shaded_frame_area_s = 0.175 * (1.73 * 4 + 5.18 * 4 + 1.98 * 8 + 2.07 * 2)   # South facade  [m²]
shaded_frame_area_w = 0.175 * (2.07 * 2)  # West facade   [m²]

# total glazing area
glazing_area_n = unshaded_glazing_area_n + shaded_glazing_area_n  # North facade  [m²]
glazing_area_e = unshaded_glazing_area_e + shaded_glazing_area_e  # East facade   [m²]
glazing_area_s = unshaded_glazing_area_s + shaded_glazing_area_s  # South facade  [m²]
glazing_area_w = unshaded_glazing_area_w + shaded_glazing_area_w  # West facade   [m²]

# total window frame area
frame_area_n = unshaded_frame_area_n + shaded_frame_area_n  # North facade  [m²]
frame_area_e = unshaded_frame_area_e + shaded_frame_area_e  # East facade   [m²]
frame_area_s = unshaded_frame_area_s + shaded_frame_area_s  # South facade  [m²]
frame_area_w = unshaded_frame_area_w + shaded_frame_area_w  # West facade   [m²]

# areas of external walls (excluding glazings and frames)
wall_area_n = 2.5 * 3 * (32.6 + 1.6 - 6.0) - glazing_area_n - frame_area_n # North facade [m^2], excluding glazings
wall_area_e = 2.5 * 3 * 14.0 - glazing_area_e - frame_area_e # East facade [m^2], excluding glazings
wall_area_s = 2.5 * 3 * (32.6 + 1.6) - glazing_area_s - frame_area_s # South facade [m^2], excluding glazings
wall_area_w = 2.5 * 3 * 14.0 - glazing_area_w - frame_area_w # West facade [m^2], excluding glazings

# areas of roof against unheated or ambiency     todo: check if correct
roof_area = 313.8       # Roof area [m²] excluding roof windows

# area of a floor against unheated or ground
floor_area = 313.8      # Floor area [m²]

# area of internal walls
int_wall_area =  (72.975 + 91.9 + 2.0 *19.75) * 3.0     # Internal wall area [m²] (both sides should be present)

# area of internal ceilings / floors
int_ceiling_area = 313.8 * 2.0 * 2.0     # Internal ceiling area [m²] (both sides should be present)

# area of walls against unheated zones like staircases
wall_against_unheated_area = (21.5 + 12.5 + 5.3) * 3.0  # Wall area against unheated zones [m²]

# orientation vectors of walls
surface_vector_north = np.array([0, 1, 0])   # North facade
surface_vector_east = np.array([1, 0, 0])    # East facade
surface_vector_south = np.array([0, -1, 0])  # South facade
surface_vector_west = np.array([-1, 0, 0])   # West facade
surface_vector_roof = np.array([0, 0, 1])   # Roof
# todo: make it with Pandas DataFrame? or a multipl vactor array?

# height of the building (needed for air temperature calculations)
building_height = 2.5 * 3  # Height of the building [m]

# summ of all areas of all constructions, excluding walls against unheated zones
total_area_constructions = (glazing_area_n + glazing_area_e + glazing_area_s + glazing_area_w +
                            frame_area_n + frame_area_e + frame_area_s + frame_area_w +
                            wall_area_n + wall_area_e + wall_area_s + wall_area_w +
                            roof_area + floor_area + int_wall_area + int_ceiling_area) # Total area of all constructions [m²] 
# endregion 

# ------------------------------------------------------
# region: Definition of thermal properties of building components
# ------------------------------------------------------

# Thermal Properties of window components
glazing_u_value = 0.7       # U-value of glazing [W/m²K]
glazing_g_value = 0.45      # g-value of glazing (fraction of solar radiation transmitted into the building) []
shading_g_value_reduction_factor = 0.14  # Reduction factor of g-value due to shading (e.g. balconies) []
frame_u_value = 2.0         # U-value of window frame [W/m²K]

# Thermal properties of opaque building components
wall_against_inheated_u_value = 1 / (2 / 8.0 + 0.17 / 0.79) # u-value of Wall against unheated zones [W/m²K]

# Thermal properties of inside layers of building components
wall_inside_lambda = 1.8 
roof_inside_lambda = 1.8
floor_inside_lambda = 1.8

# capacity density of inside layers of building components. (rho * c) [J/m³K]
wall_inside_capacity_density = 2400 * 1100
roof_inside_capacity_density = 2400 * 1100
floor_inside_capacity_density = 2400 * 1100

# thermal properties of outside layers of building components 
wall_outside_lambda = 0.031
roof_outside_lambda = 0.02
floor_outside_lambda = 0.03

# capacity density of outside layers of building components. (rho * c) [J/m³K]
wall_outside_capacity_density = 16 * 1400
roof_outside_capacity_density = 30 * 1400
floor_outside_capacity_density = 18 * 1400

# thermal properties of internal building components
int_wall_lambda = 0.79
int_ceiling_lambda = 1.8

# capacity density of internal building components. (rho * c) [J/m³K]
int_wall_capacity_density = 1070.0 * 850.0
int_ceiling_capacity_density = 2400.0 * 1100.0
# endregion

# ------------------------------------------------------
# region: thickness of layers of building components [m]
# ------------------------------------------------------

# thickness of layers of outside walls
wall_inside_thickness = 0.2  # thickness of inside layer of walls (brick) [m]
wall_outside_thickness = 0.1  # thickness of outside layer of walls (insulation) [m]

# thickness of layers of outside roof
roof_inside_thickness = 0.25  # thickness of inside layer of roof (concrete) [m]
roof_outside_thickness = 0.1   # thickness of outside layer of roof (insulation) [m]

# thickness of layers of floor against unheated zones or ground
floor_inside_thickness = 0.3   # thickness of inside layer of floor (concrete) [m]
floor_outside_thickness = 0.08  # thickness of outside layer of floor (insulation) [m]

# thickness of layers of internal walls
int_wall_thickness = 0.17       # thickness of internal walls (drywall) [m]
int_ceiling_thickness = 0.3654  # thickness of internal ceiling (drywall) [m]

# endregion

# ------------------------------------------------------
# region: Building thermal parameters
# ------------------------------------------------------
# total infiltration rate of the building
infiltration_rate = 0.194444 * 0.001 * floor_area * 3.0

# ventilation rate of the building (assumed to be always on)
air_ventilation_rate = 0.278 * 0.001 * floor_area * 3.0  # [m³/s]
heat_exchanger_efficiency = 0.0  # efficiency of heat exchanger in ventilation system []

# thermal bridges
thermal_bridges = 123.4 # thermal bridges [W/K]

# difference power input [W] 
occupancy_power = 70.0 * 0.033 * floor_area * 3.0
lighting_power = 2.7 * floor_area * 3.0
equipment_power = 8.0 * floor_area * 3.0

# shedules [0..1] for occupancy, lighting and equipment (24 values for 24 hours)
occupancy_schedule = [1 1 1 1 1 1 0.6 0.4 0 0 0 0 0.8 0.4 0 0 0 0.4 0.8 0.8 0.8 1 1 1]
lighting_schedule = [0 0 0 0 0 0 1 1 0 0 0 0 1 1 0 0 0 1 1 1 1 0 0 0]
equipment_schedule = [0.1 0.1 0.1 0.1 0.1 0.2 0.8 0.2 0.1 0.1 0.1 0.1 0.8 0.2 0.1 0.1 0.1 0.2 0.8 1.0 0.2 0.2 0.2 0.1]

# todo: change description of comments for better understanding

# endregion

# ======================================================
# region: Load weather data from file
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

# endregion