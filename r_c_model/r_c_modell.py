import numpy as np
import scipy.io as sio
import pandas as pd
from core.mapper import RCParams

class RCEngine:
    def __init__(self):
        pass

    def run(self, params: RCParams, weather_df: pd.DataFrame):
        
                
        # =======================================================
        #  Parameters and constants for the RC model
        # =======================================================

        # ------------------------------------------------------
        # region: Definition of areas of building components [m²] in north, east, south, west order
        # ------------------------------------------------------

        # unshaded glazing area (without permanent obstacles like balconies)
        unshaded_glazing_area_n = params.unshaded_glazing_area_n  # North facade  [m²]
        unshaded_glazing_area_e = params.unshaded_glazing_area_e   # East facade   [m²]
        unshaded_glazing_area_s = params.unshaded_glazing_area_s  # South facade  [m²]
        unshaded_glazing_area_w = params.unshaded_glazing_area_w  # West facade   [m²]

        # shaded glazing area (under permanent obstacles like balconies)
        shaded_glazing_area_n = params.shaded_glazing_area_n  # North facade  [m²]
        shaded_glazing_area_e = params.shaded_glazing_area_e  # East facade   [m²]
        shaded_glazing_area_s = params.shaded_glazing_area_s  # South facade  [m²]
        shaded_glazing_area_w = params.shaded_glazing_area_w  # West facade   [m²]

        # unshaded window frame area (without permanent obstacles like balcony)
        unshaded_frame_area_n = params.unshaded_frame_area_n  # North facade  [m²]
        unshaded_frame_area_e = params.unshaded_frame_area_e  # East facade   [m²]
        unshaded_frame_area_s = params.unshaded_frame_area_s  # South facade  [m²]
        unshaded_frame_area_w = params.unshaded_frame_area_w  # West facade   [m²]

        # shaded window frame area (under permanent obstacles like balconies)
        shaded_frame_area_n = params.shaded_frame_area_n  # North facade  [m²]
        shaded_frame_area_e = params.shaded_frame_area_e  # East facade   [m²]
        shaded_frame_area_s = params.shaded_frame_area_s  # South facade  [m²]
        shaded_frame_area_w = params.shaded_frame_area_w  # West facade   [m²]

        # total glazing area
        glazing_area_n = params.glazing_area_n  # North facade  [m²]
        glazing_area_e = params.glazing_area_e  # East facade   [m²]
        glazing_area_s = params.glazing_area_s  # South facade  [m²]
        glazing_area_w = params.glazing_area_w  # West facade   [m²]

        # total window frame area
        frame_area_n = params.frame_area_n  # North facade  [m²]
        frame_area_e = params.frame_area_e  # East facade   [m²]
        frame_area_s = params.frame_area_s  # South facade  [m²]
        frame_area_w = params.frame_area_w  # West facade   [m²]

        # areas of external walls (excluding glazings and frames)
        wall_area_n = params.wall_area_n   # North facade [m^2], excluding glazings
        wall_area_e = params.wall_area_e   # East facade [m^2], excluding glazings
        wall_area_s = params.wall_area_s   # South facade [m^2], excluding glazings
        wall_area_w = params.wall_area_w   # West facade [m^2], excluding glazings

        # areas of roof against unheated or ambiency     todo: check if correct
        roof_area = params.roof_area       # Roof area [m²] excluding roof windows

        # area of a floor against unheated or ground
        floor_area = params.floor_area      # Floor area [m²]

        # area of internal walls
        int_wall_area = params.int_wall_area       # Internal wall area [m²] (both sides should be present)

        # area of internal ceilings / floors
        int_ceiling_area = params.int_ceiling_area     # Internal ceiling area [m²] (both sides should be present)

        # area of walls against unheated zones like staircases
        wall_against_unheated_area = params.wall_against_unheated_area  # Wall area against unheated zones [m²]

        # orientation vectors of walls
        surface_vector_north = np.array([0, 1, 0])   # North facade
        surface_vector_east = np.array([1, 0, 0])    # East facade
        surface_vector_south = np.array([0, -1, 0])  # South facade
        surface_vector_west = np.array([-1, 0, 0])   # West facade
        surface_vector_roof = np.array([0, 0, 1])   # Roof

        # todo: make it with Pandas DataFrame? or a multipl vactor array?

        # height of the building (needed for air temperature calculations)
        building_height = params.building_height  # Height of the building [m]

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
        glazing_u_value = params.glazing_u_value       # U-value of glazing [W/m²K]
        glazing_g_value = params.glazing_g_value      # g-value of glazing (fraction of solar radiation transmitted into the building) []
        shading_g_value_reduction_factor = params.shading_g_value_reduction_factor  # Reduction factor of g-value due to shading (e.g. balconies) []
        frame_u_value = params.frame_u_value         # U-value of window frame [W/m²K]

        # Thermal properties of opaque building components
        wall_against_unheated_u_value = params.wall_against_unheated_u_value # u-value of Wall against unheated zones [W/m²K]

        # Thermal properties of inside layers of building components
        wall_inside_lambda = params.wall_inside_lambda 
        roof_inside_lambda = params.roof_inside_lambda
        floor_inside_lambda = params.floor_inside_lambda

        # capacity density of inside layers of building components. (rho * c) [J/m³K]
        wall_inside_capacity_density = params.wall_inside_capacity_density
        roof_inside_capacity_density = params.roof_inside_capacity_density
        floor_inside_capacity_density = params.floor_inside_capacity_density

        # thermal properties of outside layers of building components 
        wall_outside_lambda = params.wall_outside_lambda
        roof_outside_lambda = params.roof_outside_lambda
        floor_outside_lambda = params.floor_outside_lambda

        # capacity density of outside layers of building components. (rho * c) [J/m³K]
        wall_outside_capacity_density = params.wall_outside_capacity_density
        roof_outside_capacity_density = params.roof_outside_capacity_density
        floor_outside_capacity_density = params.floor_outside_capacity_density

        # thermal properties of internal building components
        int_wall_lambda = params.int_wall_lambda
        int_ceiling_lambda = params.int_ceiling_lambda

        # capacity density of internal building components. (rho * c) [J/m³K]
        int_wall_capacity_density = params.int_wall_capacity_density
        int_ceiling_capacity_density = params.int_ceiling_capacity_density
        # endregion

        # ------------------------------------------------------
        # region: thickness of layers of building components [m]
        # ------------------------------------------------------

        # thickness of layers of outside walls
        wall_inside_thickness = params.wall_inside_thickness  # thickness of inside layer of walls (brick) [m]
        wall_outside_thickness = params.wall_outside_thickness  # thickness of outside layer of walls (insulation) [m]

        # thickness of layers of outside roof
        roof_inside_thickness = params.roof_inside_thickness  # thickness of inside layer of roof (concrete) [m]
        roof_outside_thickness = params.roof_outside_thickness   # thickness of outside layer of roof (insulation) [m]

        # thickness of layers of floor against unheated zones or ground
        floor_inside_thickness = params.floor_inside_thickness   # thickness of inside layer of floor (concrete) [m]
        floor_outside_thickness = params.floor_outside_thickness  # thickness of outside layer of floor (insulation) [m]

        # thickness of layers of internal walls
        int_wall_thickness = params.int_wall_thickness       # thickness of internal walls (drywall) [m]
        int_ceiling_thickness = params.int_ceiling_thickness  # thickness of internal ceiling (drywall) [m]

        # endregion

        # ------------------------------------------------------
        # region: Building thermal parameters
        # ------------------------------------------------------
        # total infiltration rate of the building
        infiltration_rate = params.infiltration_rate_specific * floor_area # [1/h]

        # ventilation rate of the building (assumed to be always on)
        air_ventilation_rate = params.air_ventilation_rate_specific * floor_area  # [m³/s]
        heat_exchanger_efficiency = params.heat_exchanger_efficiency  # efficiency of heat exchanger in ventilation system []

        # thermal bridges
        thermal_bridges = params.thermal_bridges  # thermal bridges [W/K]

        # difference power input [W] 
        occupancy_power = params.occupancy_power_per_area * floor_area  # occupancy power [W]
        lighting_power = params.lighting_power_per_area * floor_area    # lighting power [W]
        equipment_power = params.equipment_power_per_area * floor_area  # equipment power [W]

        # shedules [0..1] for occupancy, lighting and equipment (24 values for 24 hours)
        occupancy_schedule = params.occupancy_schedule
        lighting_schedule = params.lighting_schedule
        equipment_schedule = params.equipment_schedule


        # todo: change description of comments for better understanding

        # endregion

        # ======================================================
        # region: Load weather data from file
        # ======================================================

        # access weather data from DataFrame
        ambient_temp = weather_df['air_temperature'].to_numpy(dtype=float)              # Ambient temperature  [°C]
        beam_radiation = weather_df['solar_radiation_direct'].to_numpy(dtype=float)     # Beam radiation       [W/m²]
        diff_radiation = weather_df['solar_radiation_diffuse'].to_numpy(dtype=float)    # Diffuse radiation    [W/m²]
        sun_elevation = weather_df['sun_elevation'].to_numpy(dtype=float)               # Sun elevation        [°]
        sun_azimuth = weather_df['sun_azimuth'].to_numpy(dtype=float)                   # Sun azimuth          [°]

        # ------------------------------------------------------
        # region: Calculation of sun vector and global radiation
        # ------------------------------------------------------
        # definition of sund vector and global radiation
        sun_vector = np.zeros((sun_elevation.size, 3))  # Initialize sund vector array
        global_radiation = np.zeros(sun_elevation.size)    # Initialize global radiation array

        # calculation of sun vector and global radiation
        mask = sun_elevation > 0.0  # Only calculate for positive sun elevations
        sun_vector[mask, 0] = np.cos(np.deg2rad(sun_elevation[mask])) * np.sin(np.deg2rad(sun_azimuth[mask]))  # X-component
        sun_vector[mask, 1] = np.cos(np.deg2rad(sun_elevation[mask])) * np.cos(np.deg2rad(sun_azimuth[mask]))  # Y-component
        sun_vector[mask, 2] = -np.sin(np.deg2rad(sun_elevation[mask]))  # Z-component

        global_radiation = diff_radiation - beam_radiation * sun_vector[:, 2]  # Global radiation on horizontal surface [W/m²]

        # endregion

        # ------------------------------------------------------
        # region: Calculation of the sun flux on building surfaces: direct + diffuse + reflected
        # ------------------------------------------------------
        # initialization of sun flux arrays for each facade and roof
        sun_flux_north = np.zeros(len(sun_elevation))  # Initialize sun flux array for north facade
        sun_flux_east = np.zeros(len(sun_elevation))   # Initialize sun flux array for east facade
        sun_flux_south = np.zeros(len(sun_elevation))  # Initialize sun flux array for south facade
        sun_flux_west = np.zeros(len(sun_elevation))   # Initialize sun flux array for west facade
        sun_flux_roof = np.zeros_like(global_radiation)   # Initialize sun flux array for roof


        # Sun flux on north facade [W/m²]
        sun_flux_north[mask] = (
            -beam_radiation[mask] * np.minimum(0.0, 
                surface_vector_north[0] * sun_vector[mask, 0] +
                surface_vector_north[1] * sun_vector[mask, 1] +
                surface_vector_north[2] * sun_vector[mask, 2]
            ) +
            0.5 * diff_radiation[mask] +
            0.2 * 0.5 * global_radiation[mask]
        )  

        # Sun flux on east facade [W/m²]
        sun_flux_east[mask] = (
            -beam_radiation[mask] * np.minimum(0.0,
                surface_vector_east[0] * sun_vector[mask, 0] + 
                surface_vector_east[1] * sun_vector[mask, 1] + 
                surface_vector_east[2] * sun_vector[mask, 2]
            ) + 
            0.5 * diff_radiation[mask] + 
            0.2 * 0.5 * global_radiation[mask]
        )

        # sun flux on west facade [W/m²]
        sun_flux_west[mask] = (
            -beam_radiation[mask] * np.minimum(0.0,
                surface_vector_west[0] * sun_vector[mask, 0] + 
                surface_vector_west[1] * sun_vector[mask, 1] + 
                surface_vector_west[2] * sun_vector[mask, 2]
            ) + 
            0.5 * diff_radiation[mask] + 
            0.2 * 0.5 * global_radiation[mask]
        )

        # sun flux on south facade [W/m²]
        sun_flux_south[mask] = (
            -beam_radiation[mask] * np.minimum(0.0,
                surface_vector_south[0] * sun_vector[mask, 0] + 
                surface_vector_south[1] * sun_vector[mask, 1] + 
                surface_vector_south[2] * sun_vector[mask, 2]
            ) + 
            0.5 * diff_radiation[mask] + 
            0.2 * 0.5 * global_radiation[mask]
        )

        # sun flux on roof [W/m²]
        sun_flux_roof[mask] = global_radiation[mask]  # Roof is horizontal, so sun flux equals global radiation

        # endregion

        # ------------------------------------------------------
        # region: deffinition of simulation parameters
        # ------------------------------------------------------

        # simulation time step
        time_step = params.time_step  # [s]

        # surface heat transfer coefficients of internal surfaces
        surf_htc_in =  params.surf_htc_in  # internal surface heat transfer coefficient [W/m²K]

        # surface heat transfer coefficients of external surfaces
        surf_htc_out = params.surf_htc_out  # external surface heat transfer coefficient [W/m²K]

        # heating and cooling setpoints
        heating_setpoint = params.heating_setpoint  # heating setpoint temperature [°C]
        cooling_setpoint = params.cooling_setpoint  # cooling setpoint temperature [°C]

        # distribution of internal heat gains to air and building constructions
        int_heat_gain_to_air_coef = 0.6
        int_heat_gain_to_glazing_n_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_n / total_area_constructions
        int_heat_gain_to_glazing_e_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_e / total_area_constructions
        int_heat_gain_to_glazing_s_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_s / total_area_constructions
        int_heat_gain_to_glazing_w_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_w / total_area_constructions
        int_heat_gain_to_frame_n_coef = (1 - int_heat_gain_to_air_coef) * frame_area_n / total_area_constructions
        int_heat_gain_to_frame_e_coef = (1 - int_heat_gain_to_air_coef) * frame_area_e / total_area_constructions
        int_heat_gain_to_frame_s_coef = (1 - int_heat_gain_to_air_coef) * frame_area_s / total_area_constructions
        int_heat_gain_to_frame_w_coef = (1 - int_heat_gain_to_air_coef) * frame_area_w / total_area_constructions
        int_heat_gain_to_wall_n_coef = (1 - int_heat_gain_to_air_coef) * wall_area_n / total_area_constructions
        int_heat_gain_to_wall_e_coef = (1 - int_heat_gain_to_air_coef) * wall_area_e / total_area_constructions
        int_heat_gain_to_wall_s_coef = (1 - int_heat_gain_to_air_coef) * wall_area_s / total_area_constructions
        int_heat_gain_to_wall_w_coef = (1 - int_heat_gain_to_air_coef) * wall_area_w / total_area_constructions
        int_heat_gain_to_roof_coef = (1 - int_heat_gain_to_air_coef) * roof_area / total_area_constructions
        int_heat_gain_to_floor_coef = (1 - int_heat_gain_to_air_coef) * floor_area / total_area_constructions
        int_heat_gain_to_int_wall_coef = (1 - int_heat_gain_to_air_coef) * int_wall_area / total_area_constructions
        int_heat_gain_to_int_ceiling_coef = (1 - int_heat_gain_to_air_coef) * int_ceiling_area / total_area_constructions

        # distribution of solar heat gains on building constructions
        sun_heat_gain_to_outside_glazing = 0.25 * (1.0 - glazing_g_value)
        sun_heat_gain_to_inside_glazing = 0.25 * (1.0 - glazing_g_value) * glazing_g_value
        sun_heat_gain_to_int_wall = (1.0 - 0.25 * (1.0 - glazing_g_value)) * glazing_g_value * int_wall_area / (int_wall_area + int_ceiling_area)
        sun_heat_gain_to_int_ceiling = (1.0 - 0.25 * (1.0 - glazing_g_value)) * glazing_g_value * int_ceiling_area / (int_wall_area + int_ceiling_area)

        # distribution of lighting power according to north, east, south, west orientation
        lighting_north_side = wall_area_n / (wall_area_n + wall_area_e + wall_area_s + wall_area_w)
        lighting_east_side = wall_area_e / (wall_area_n + wall_area_e + wall_area_s + wall_area_w)
        lighting_south_side = wall_area_s / (wall_area_n + wall_area_e + wall_area_s + wall_area_w)
        lighting_west_side = wall_area_w / (wall_area_n + wall_area_e + wall_area_s + wall_area_w)

        # surface heat transfer coefficients for radiation exchange between internal surfaces
        surf_rad_htc = 4.0

        # radiation heat transfer coefficients between internal walls and other internal surfaces
        surf_rad_htc_int_wall_glazing_n = surf_rad_htc * int_wall_area * glazing_area_n / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_glazing_e = surf_rad_htc * int_wall_area * glazing_area_e / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_glazing_s = surf_rad_htc * int_wall_area * glazing_area_s / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_glazing_w = surf_rad_htc * int_wall_area * glazing_area_w / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_frame_n = surf_rad_htc * int_wall_area * frame_area_n / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_frame_e = surf_rad_htc * int_wall_area * frame_area_e / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_frame_s = surf_rad_htc * int_wall_area * frame_area_s / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_frame_w = surf_rad_htc * int_wall_area * frame_area_w / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_wall_n = surf_rad_htc * int_wall_area * wall_area_n / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_wall_e = surf_rad_htc * int_wall_area * wall_area_e / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_wall_s = surf_rad_htc * int_wall_area * wall_area_s / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_wall_w = surf_rad_htc * int_wall_area * wall_area_w / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_roof = surf_rad_htc * int_wall_area * roof_area / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_floor = surf_rad_htc * int_wall_area * floor_area / (total_area_constructions - int_wall_area)
        surf_rad_htc_int_wall_int_ceiling = surf_rad_htc * int_wall_area * int_ceiling_area / (total_area_constructions - int_wall_area)

        # radiation heat transfer coefficients between internal ceilings and other internal surfaces
        surf_rad_htc_int_ceiling_glazing_n = surf_rad_htc * int_ceiling_area * glazing_area_n / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_glazing_e = surf_rad_htc * int_ceiling_area * glazing_area_e / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_glazing_s = surf_rad_htc * int_ceiling_area * glazing_area_s / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_glazing_w = surf_rad_htc * int_ceiling_area * glazing_area_w / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_frame_n = surf_rad_htc * int_ceiling_area * frame_area_n / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_frame_e = surf_rad_htc * int_ceiling_area * frame_area_e / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_frame_s = surf_rad_htc * int_ceiling_area * frame_area_s / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_frame_w = surf_rad_htc * int_ceiling_area * frame_area_w / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_wall_n = surf_rad_htc * int_ceiling_area * wall_area_n / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_wall_e = surf_rad_htc * int_ceiling_area * wall_area_e / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_wall_s = surf_rad_htc * int_ceiling_area * wall_area_s / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_wall_w = surf_rad_htc * int_ceiling_area * wall_area_w / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_roof = surf_rad_htc * int_ceiling_area * roof_area / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_floor = surf_rad_htc * int_ceiling_area * floor_area / (total_area_constructions - int_ceiling_area)
        surf_rad_htc_int_ceiling_int_wall = surf_rad_htc_int_wall_int_ceiling

        # endregion

        # initialization of left matrix for a system of linear equations
        left_matrix = np.zeros((49, 49))

        # definition of the lines of the system of linear equations
        line_air = 0     # line for air temperature node

        line_in_glazing_n = 1  # line for inside glazing temperature in north direction
        line_in_glazing_e = 2  # line for inside glazing temperature in east direction
        line_in_glazing_s = 3  # line for inside glazing temperature in south direction
        line_in_glazing_w = 4  # line for inside glazing temperature in west direction

        line_out_glazing_n = 5  # line for outside glazing temperature in north direction
        line_out_glazing_e = 6  # line for outside glazing temperature in east direction
        line_out_glazing_s = 7  # line for outside glazing temperature in south direction
        line_out_glazing_w = 8  # line for outside glazing temperature in west direction

        line_in_frame_n = 9   # line for inside frame temperature in north direction
        line_in_frame_e = 10  # line for inside frame temperature in east direction
        line_in_frame_s = 11  # line for inside frame temperature in south direction
        line_in_frame_w = 12  # line for inside frame temperature in west direction

        line_out_frame_n = 13  # line for outside frame temperature in north direction
        line_out_frame_e = 14  # line for outside frame temperature in east direction
        line_out_frame_s = 15  # line for outside frame temperature in south direction
        line_out_frame_w = 16  # line for outside frame temperature in west direction

        line_wall_n_1 = 17  # line for the 1. node of the external wall in noth direction
        line_wall_e_1 = 18  # line for the 1. node of the external wall in east direction
        line_wall_s_1 = 19  # line for the 1. node of the external wall in south direction
        line_wall_w_1 = 20  # line for the 1. node of the external wall in west direction
        line_roof_1 = 21    # line for the 1. node of the roof
        line_floor_1 = 22   # line for the 1. node of the floor
        line_int_wall_1 = 23  # line for the 1. node of the internal walls
        line_int_ceiling_1 = 24  # line for the 1. node of the internal ceilings

        line_wall_n_2 = 25  # line for the 2. node of the external wall in noth direction
        line_wall_e_2 = 26  # line for the 2. node of the external wall in east direction
        line_wall_s_2 = 27  # line for the 2. node of the
        line_wall_w_2 = 28  # line for the 2. node of the external wall in west direction
        line_roof_2 = 29    # line for the 2. node of the roof
        line_floor_2 = 30   # line for the 2. node of the floor
        line_int_wall_2 = 31  # line for the 2. node of the internal walls
        line_int_ceiling_2 = 32  # line for the 2. node of the internal ceilings

        line_wall_n_3 = 33  # line for the 3. node of the external wall in noth direction
        line_wall_e_3 = 34  # line for the 3. node of the external wall in east direction
        line_wall_s_3 = 35  # line for the 3. node of the external wall in south direction
        line_wall_w_3 = 36  # line for the 3. node of the external wall in west direction
        line_roof_3 = 37    # line for the 3. node of the roof
        line_floor_3 = 38   # line for the 3. node of the floor
        line_int_wall_3 = 39  # line for the 3. node of the internal walls
        line_int_ceiling_3 = 40  # line for the 3. node of the internal ceilings

        line_wall_n_4 = 41  # line for the 4. node of the external wall in noth direction
        line_wall_e_4 = 42  # line for the 4. node of the external wall in east direction
        line_wall_s_4 = 43  # line for the 4. node of the external wall in south direction
        line_wall_w_4 = 44  # line for the 4. node of the external wall in west direction
        line_roof_4 = 45    # line for the 4. node of the roof
        line_floor_4 = 46   # line for the 4. node of the floor
        line_int_wall_4 = 47  # line for the 4. node of the internal walls
        line_int_ceiling_4 = 48  # line for the 4. node of the internal ceilings

        # ------------------------------------------------------
        # region: Definition of the values in the left matrix
        # ------------------------------------------------------

        # air temperature equation
        left_matrix[line_air, line_air] = (building_height * floor_area * 1006 * 1.185 +
            surf_htc_in * total_area_constructions *time_step + 
            (thermal_bridges + wall_against_unheated_u_value * wall_against_unheated_area) * time_step +
            (infiltration_rate + air_ventilation_rate * (1.0 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step)
        left_matrix[line_air, line_in_glazing_n] = -surf_htc_in * time_step * glazing_area_n
        left_matrix[line_air, line_in_glazing_e] = -surf_htc_in * time_step * glazing_area_e
        left_matrix[line_air, line_in_glazing_s] = -surf_htc_in * time_step * glazing_area_s
        left_matrix[line_air, line_in_glazing_w] = -surf_htc_in * time_step * glazing_area_w
        left_matrix[line_air, line_in_frame_n] = -surf_htc_in * time_step * frame_area_n
        left_matrix[line_air, line_in_frame_e] = -surf_htc_in * time_step * frame_area_e
        left_matrix[line_air, line_in_frame_s] = -surf_htc_in * time_step * frame_area_s
        left_matrix[line_air, line_in_frame_w] = -surf_htc_in * time_step * frame_area_w
        left_matrix[line_air, line_wall_n_1] = -surf_htc_in * time_step * wall_area_n
        left_matrix[line_air, line_wall_e_1] = -surf_htc_in * time_step * wall_area_e
        left_matrix[line_air, line_wall_s_1] = -surf_htc_in * time_step * wall_area_s
        left_matrix[line_air, line_wall_w_1] = -surf_htc_in * time_step * wall_area_w
        left_matrix[line_air, line_roof_1] = -surf_htc_in * time_step * roof_area
        left_matrix[line_air, line_floor_1] = -surf_htc_in * time_step * floor_area
        left_matrix[line_air, line_int_wall_1] = -surf_htc_in * time_step * int_wall_area
        left_matrix[line_air, line_int_ceiling_1] = -surf_htc_in * time_step * int_ceiling_area

        # temperature of the inside node of glazing in north direction
        left_matrix[line_in_glazing_n, line_air] = left_matrix[line_air, line_in_glazing_n]
        left_matrix[line_in_glazing_n, line_out_glazing_n] = -glazing_area_n * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out)
        left_matrix[line_in_glazing_n, line_int_wall_1] = -surf_rad_htc_int_wall_glazing_n * time_step
        left_matrix[line_in_glazing_n, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_glazing_n * time_step

        left_matrix[line_in_glazing_n, line_in_glazing_n] = (
            - left_matrix[line_in_glazing_n, line_air]
            - left_matrix[line_in_glazing_n, line_out_glazing_n]
            - left_matrix[line_in_glazing_n, line_int_wall_1]
            - left_matrix[line_in_glazing_n, line_int_ceiling_1]
        )

        # temperature of the inside node of glazing in east direction
        left_matrix[line_in_glazing_e, line_air] = left_matrix[line_air, line_in_glazing_e]
        left_matrix[line_in_glazing_e, line_out_glazing_e] = -glazing_area_e * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out)
        left_matrix[line_in_glazing_e, line_int_wall_1] = -surf_rad_htc_int_wall_glazing_e * time_step
        left_matrix[line_in_glazing_e, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_glazing_e * time_step

        left_matrix[line_in_glazing_e, line_in_glazing_e] = (
            - left_matrix[line_in_glazing_e, line_air]
            - left_matrix[line_in_glazing_e, line_out_glazing_e]
            - left_matrix[line_in_glazing_e, line_int_wall_1]
            - left_matrix[line_in_glazing_e, line_int_ceiling_1]
        )

        # temperature of the inside node of glazing in south direction
        left_matrix[line_in_glazing_s, line_air] = left_matrix[line_air, line_in_glazing_s]
        left_matrix[line_in_glazing_s, line_out_glazing_s] = -glazing_area_s * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out)
        left_matrix[line_in_glazing_s, line_int_wall_1] = -surf_rad_htc_int_wall_glazing_s * time_step
        left_matrix[line_in_glazing_s, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_glazing_s * time_step

        left_matrix[line_in_glazing_s, line_in_glazing_s] = (
            - left_matrix[line_in_glazing_s, line_air]
            - left_matrix[line_in_glazing_s, line_out_glazing_s]
            - left_matrix[line_in_glazing_s, line_int_wall_1]
            - left_matrix[line_in_glazing_s, line_int_ceiling_1]
        )

        # temperature of the inside node of glazing in west direction
        left_matrix[line_in_glazing_w, line_air] = left_matrix[line_air, line_in_glazing_w]
        left_matrix[line_in_glazing_w, line_out_glazing_w] = -glazing_area_w * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out)
        left_matrix[line_in_glazing_w, line_int_wall_1] = -surf_rad_htc_int_wall_glazing_w * time_step
        left_matrix[line_in_glazing_w, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_glazing_w * time_step

        # temperature of the inside node of glazing in west direction
        left_matrix[line_in_glazing_w, line_in_glazing_w] = (
            - left_matrix[line_in_glazing_w, line_air]
            - left_matrix[line_in_glazing_w, line_out_glazing_w]
            - left_matrix[line_in_glazing_w, line_int_wall_1]
            - left_matrix[line_in_glazing_w, line_int_ceiling_1]
        )

        # temperature of the outside node of glazing in north direction
        left_matrix[line_out_glazing_n, line_in_glazing_n] = left_matrix[line_in_glazing_n, line_out_glazing_n]
        left_matrix[line_out_glazing_n, line_out_glazing_n] = -left_matrix[line_out_glazing_n, line_in_glazing_n] + glazing_area_n * surf_htc_out * time_step

        # temperature of the outside node of glazing in east direction
        left_matrix[line_out_glazing_e, line_in_glazing_e] = left_matrix[line_in_glazing_e, line_out_glazing_e]
        left_matrix[line_out_glazing_e, line_out_glazing_e] = -left_matrix[line_out_glazing_e, line_in_glazing_e] + glazing_area_e * surf_htc_out * time_step

        # temperature of the outside node of glazing in south direction
        left_matrix[line_out_glazing_s, line_in_glazing_s] = left_matrix[line_in_glazing_s, line_out_glazing_s]
        left_matrix[line_out_glazing_s, line_out_glazing_s] = -left_matrix[line_out_glazing_s, line_in_glazing_s] + glazing_area_s * surf_htc_out * time_step

        # temperature of the outside node of glazing in west direction
        left_matrix[line_out_glazing_w, line_in_glazing_w] = left_matrix[line_in_glazing_w, line_out_glazing_w]
        left_matrix[line_out_glazing_w, line_out_glazing_w] = -left_matrix[line_out_glazing_w, line_in_glazing_w] + glazing_area_w * surf_htc_out * time_step

        # temperature of the inside node of noth window frame
        left_matrix[line_in_frame_n, line_air] = left_matrix[line_air, line_in_frame_n]
        left_matrix[line_in_frame_n, line_out_frame_n] = -frame_area_n * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out)
        left_matrix[line_in_frame_n, line_int_wall_1] = -surf_rad_htc_int_wall_frame_n * time_step
        left_matrix[line_in_frame_n, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_frame_n * time_step

        left_matrix[line_in_frame_n, line_in_frame_n] = (
            - left_matrix[line_in_frame_n, line_air]
            - left_matrix[line_in_frame_n, line_out_frame_n]
            - left_matrix[line_in_frame_n, line_int_wall_1]
            - left_matrix[line_in_frame_n, line_int_ceiling_1]
        )

        # temperature of the inside node of east window frame
        left_matrix[line_in_frame_e, line_air] = left_matrix[line_air, line_in_frame_e]
        left_matrix[line_in_frame_e, line_out_frame_e] = -frame_area_e * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out)
        left_matrix[line_in_frame_e, line_int_wall_1] = -surf_rad_htc_int_wall_frame_e * time_step
        left_matrix[line_in_frame_e, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_frame_e * time_step

        left_matrix[line_in_frame_e, line_in_frame_e] = (
            - left_matrix[line_in_frame_e, line_air]
            - left_matrix[line_in_frame_e, line_out_frame_e]
            - left_matrix[line_in_frame_e, line_int_wall_1]
            - left_matrix[line_in_frame_e, line_int_ceiling_1]
        )

        # temperature of the inside node of south window frame
        left_matrix[line_in_frame_s, line_air] = left_matrix[line_air, line_in_frame_s]
        left_matrix[line_in_frame_s, line_out_frame_s] = -frame_area_s * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out)
        left_matrix[line_in_frame_s, line_int_wall_1] = -surf_rad_htc_int_wall_frame_s * time_step
        left_matrix[line_in_frame_s, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_frame_s * time_step

        left_matrix[line_in_frame_s, line_in_frame_s] = (
            - left_matrix[line_in_frame_s, line_air]
            - left_matrix[line_in_frame_s, line_out_frame_s]
            - left_matrix[line_in_frame_s, line_int_wall_1]
            - left_matrix[line_in_frame_s, line_int_ceiling_1]
        )

        # temperature of the inside node of west window frame
        left_matrix[line_in_frame_w, line_air] = left_matrix[line_air, line_in_frame_w]
        left_matrix[line_in_frame_w, line_out_frame_w] = -frame_area_w * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out)
        left_matrix[line_in_frame_w, line_int_wall_1] = -surf_rad_htc_int_wall_frame_w * time_step
        left_matrix[line_in_frame_w, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_frame_w * time_step

        left_matrix[line_in_frame_w, line_in_frame_w] = (
            - left_matrix[line_in_frame_w, line_air]
            - left_matrix[line_in_frame_w, line_out_frame_w]
            - left_matrix[line_in_frame_w, line_int_wall_1]
            - left_matrix[line_in_frame_w, line_int_ceiling_1]
        )

        # temperature of the outside node of north window frame
        left_matrix[line_out_frame_n, line_in_frame_n] = left_matrix[line_in_frame_n, line_out_frame_n]
        left_matrix[line_out_frame_n, line_out_frame_n] = -left_matrix[line_out_frame_n, line_in_frame_n] + frame_area_n * surf_htc_out * time_step

        # temperature of the outside node of east window frame
        left_matrix[line_out_frame_e, line_in_frame_e] = left_matrix[line_in_frame_e, line_out_frame_e]
        left_matrix[line_out_frame_e, line_out_frame_e] = -left_matrix[line_out_frame_e, line_in_frame_e] + frame_area_e * surf_htc_out * time_step

        # temperature of the outside node of south window frame
        left_matrix[line_out_frame_s, line_in_frame_s] = left_matrix[line_in_frame_s, line_out_frame_s]
        left_matrix[line_out_frame_s, line_out_frame_s] = -left_matrix[line_out_frame_s, line_in_frame_s] + frame_area_s * surf_htc_out * time_step

        # temperature of the outside node of west window frame
        left_matrix[line_out_frame_w, line_in_frame_w] = left_matrix[line_in_frame_w, line_out_frame_w]
        left_matrix[line_out_frame_w, line_out_frame_w] = -left_matrix[line_out_frame_w, line_in_frame_w] + frame_area_w * surf_htc_out * time_step

        # temperature of the 1. node of the external wall in north direction
        left_matrix[line_wall_n_1, line_air] = left_matrix[line_air, line_wall_n_1]
        left_matrix[line_wall_n_1, line_wall_n_2] = -wall_area_n * time_step * wall_inside_lambda / wall_inside_thickness / 0.75
        left_matrix[line_wall_n_1, line_int_wall_1] = -surf_rad_htc_int_wall_wall_n * time_step
        left_matrix[line_wall_n_1, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_wall_n * time_step

        left_matrix[line_wall_n_1, line_wall_n_1] = (
            wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5
            - left_matrix[line_wall_n_1, line_air]
            - left_matrix[line_wall_n_1, line_wall_n_2]
            - left_matrix[line_wall_n_1, line_int_wall_1]
            - left_matrix[line_wall_n_1, line_int_ceiling_1]
        )

        # temperature of the 1. node of the external wall in east direction
        left_matrix[line_wall_e_1, line_air] = left_matrix[line_air, line_wall_e_1]
        left_matrix[line_wall_e_1, line_wall_e_2] = -wall_area_e * time_step * wall_inside_lambda / wall_inside_thickness / 0.75
        left_matrix[line_wall_e_1, line_int_wall_1] = -surf_rad_htc_int_wall_wall_e * time_step
        left_matrix[line_wall_e_1, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_wall_e * time_step

        left_matrix[line_wall_e_1, line_wall_e_1] = (
            wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5
            - left_matrix[line_wall_e_1, line_air]
            - left_matrix[line_wall_e_1, line_wall_e_2]
            - left_matrix[line_wall_e_1, line_int_wall_1]
            - left_matrix[line_wall_e_1, line_int_ceiling_1]
        )

        # temperature of the 1. node of the external wall in south direction
        left_matrix[line_wall_s_1, line_air] = left_matrix[line_air, line_wall_s_1]
        left_matrix[line_wall_s_1, line_wall_s_2] = -wall_area_s * time_step * wall_inside_lambda / wall_inside_thickness / 0.75
        left_matrix[line_wall_s_1, line_int_wall_1] = -surf_rad_htc_int_wall_wall_s * time_step
        left_matrix[line_wall_s_1, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_wall_s * time_step

        left_matrix[line_wall_s_1, line_wall_s_1] = (
            wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5
            - left_matrix[line_wall_s_1, line_air]
            - left_matrix[line_wall_s_1, line_wall_s_2]
            - left_matrix[line_wall_s_1, line_int_wall_1]
            - left_matrix[line_wall_s_1, line_int_ceiling_1]
        )

        # temperature of the 1. node of the external wall in west direction
        left_matrix[line_wall_w_1, line_air] = left_matrix[line_air, line_wall_w_1]
        left_matrix[line_wall_w_1, line_wall_w_2] = -wall_area_w * time_step * wall_inside_lambda / wall_inside_thickness / 0.75
        left_matrix[line_wall_w_1, line_int_wall_1] = -surf_rad_htc_int_wall_wall_w * time_step
        left_matrix[line_wall_w_1, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_wall_w * time_step

        left_matrix[line_wall_w_1, line_wall_w_1] = (
            wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5
            - left_matrix[line_wall_w_1, line_air]
            - left_matrix[line_wall_w_1, line_wall_w_2]
            - left_matrix[line_wall_w_1, line_int_wall_1]
            - left_matrix[line_wall_w_1, line_int_ceiling_1]
        )

        # temperature of the 1. node of the roof
        left_matrix[line_roof_1, line_air] = left_matrix[line_air, line_roof_1]
        left_matrix[line_roof_1, line_roof_2] = -roof_area * time_step * roof_inside_lambda / roof_inside_thickness / 0.75
        left_matrix[line_roof_1, line_int_wall_1] = -surf_rad_htc_int_wall_roof * time_step
        left_matrix[line_roof_1, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_roof * time_step

        left_matrix[line_roof_1, line_roof_1] = (
            roof_area * roof_inside_capacity_density * roof_inside_thickness * 0.5
            - left_matrix[line_roof_1, line_air]
            - left_matrix[line_roof_1, line_roof_2]
            - left_matrix[line_roof_1, line_int_wall_1]
            - left_matrix[line_roof_1, line_int_ceiling_1]
        )

        # temperature of the 1. node of the floor
        left_matrix[line_floor_1, line_air] = left_matrix[line_air, line_floor_1]
        left_matrix[line_floor_1, line_floor_2] = -floor_area * time_step * floor_inside_lambda / floor_inside_thickness / 0.75
        left_matrix[line_floor_1, line_int_wall_1] = -surf_rad_htc_int_wall_floor * time_step
        left_matrix[line_floor_1, line_int_ceiling_1] = -surf_rad_htc_int_ceiling_floor * time_step

        left_matrix[line_floor_1, line_floor_1] = (
            floor_area * floor_inside_capacity_density * floor_inside_thickness * 0.5
            - left_matrix[line_floor_1, line_air]
            - left_matrix[line_floor_1, line_floor_2]
            - left_matrix[line_floor_1, line_int_wall_1]
            - left_matrix[line_floor_1, line_int_ceiling_1]
        )

        # temperature of the 1. node of the internal walls
        left_matrix[line_int_wall_1, line_air] = left_matrix[line_air, line_int_wall_1]
        left_matrix[line_int_wall_1, line_int_wall_2] = -int_wall_area * time_step * int_wall_lambda / int_wall_thickness / (0.125 + 0.0625)
        left_matrix[line_int_wall_1, line_in_glazing_n] = left_matrix[line_in_glazing_n, line_int_wall_1]
        left_matrix[line_int_wall_1, line_in_glazing_e] = left_matrix[line_in_glazing_e, line_int_wall_1]
        left_matrix[line_int_wall_1, line_in_glazing_s] = left_matrix[line_in_glazing_s, line_int_wall_1]
        left_matrix[line_int_wall_1, line_in_glazing_w] = left_matrix[line_in_glazing_w, line_int_wall_1]
        left_matrix[line_int_wall_1, line_in_frame_n] = left_matrix[line_in_frame_n, line_int_wall_1]
        left_matrix[line_int_wall_1, line_in_frame_e] = left_matrix[line_in_frame_e, line_int_wall_1]
        left_matrix[line_int_wall_1, line_in_frame_s] = left_matrix[line_in_frame_s, line_int_wall_1]
        left_matrix[line_int_wall_1, line_in_frame_w] = left_matrix[line_in_frame_w, line_int_wall_1]
        left_matrix[line_int_wall_1, line_wall_n_1] = left_matrix[line_wall_n_1, line_int_wall_1]
        left_matrix[line_int_wall_1, line_wall_e_1] = left_matrix[line_wall_e_1, line_int_wall_1]
        left_matrix[line_int_wall_1, line_wall_s_1] = left_matrix[line_wall_s_1, line_int_wall_1]
        left_matrix[line_int_wall_1, line_wall_w_1] = left_matrix[line_wall_w_1, line_int_wall_1]
        left_matrix[line_int_wall_1, line_roof_1] = left_matrix[line_roof_1, line_int_wall_1]
        left_matrix[line_int_wall_1, line_floor_1] = left_matrix[line_floor_1, line_int_wall_1]
        left_matrix[line_int_wall_1, line_int_ceiling_1] = -surf_rad_htc_int_wall_int_ceiling * time_step

        left_matrix[line_int_wall_1, line_int_wall_1] = (
            int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125
            - left_matrix[line_int_wall_1, line_air]
            - left_matrix[line_int_wall_1, line_int_wall_2]
            - left_matrix[line_int_wall_1, line_in_glazing_n]
            - left_matrix[line_int_wall_1, line_in_glazing_e]
            - left_matrix[line_int_wall_1, line_in_glazing_s]
            - left_matrix[line_int_wall_1, line_in_glazing_w]
            - left_matrix[line_int_wall_1, line_in_frame_n]
            - left_matrix[line_int_wall_1, line_in_frame_e]
            - left_matrix[line_int_wall_1, line_in_frame_s]
            - left_matrix[line_int_wall_1, line_in_frame_w]
            - left_matrix[line_int_wall_1, line_wall_n_1]
            - left_matrix[line_int_wall_1, line_wall_e_1]
            - left_matrix[line_int_wall_1, line_wall_s_1]
            - left_matrix[line_int_wall_1, line_wall_w_1]
            - left_matrix[line_int_wall_1, line_roof_1]
            - left_matrix[line_int_wall_1, line_floor_1]
            - left_matrix[line_int_wall_1, line_int_ceiling_1]
        )

        # temperature of the 1. node of the internal ceilings
        left_matrix[line_int_ceiling_1, line_air] = left_matrix[line_air, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_int_ceiling_2] = -int_ceiling_area * time_step * int_ceiling_lambda / int_ceiling_thickness / (0.125 + 0.0625)
        left_matrix[line_int_ceiling_1, line_in_glazing_n] = left_matrix[line_in_glazing_n, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_in_glazing_e] = left_matrix[line_in_glazing_e, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_in_glazing_s] = left_matrix[line_in_glazing_s, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_in_glazing_w] = left_matrix[line_in_glazing_w, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_in_frame_n] = left_matrix[line_in_frame_n, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_in_frame_e] = left_matrix[line_in_frame_e, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_in_frame_s] = left_matrix[line_in_frame_s, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_in_frame_w] = left_matrix[line_in_frame_w, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_wall_n_1] = left_matrix[line_wall_n_1, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_wall_e_1] = left_matrix[line_wall_e_1, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_wall_s_1] = left_matrix[line_wall_s_1, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_wall_w_1] = left_matrix[line_wall_w_1, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_roof_1] = left_matrix[line_roof_1, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_floor_1] = left_matrix[line_floor_1, line_int_ceiling_1]
        left_matrix[line_int_ceiling_1, line_int_wall_1] = left_matrix[line_int_wall_1, line_int_ceiling_1]

        left_matrix[line_int_ceiling_1, line_int_ceiling_1] = (
            int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125
            - left_matrix[line_int_ceiling_1, line_air]
            - left_matrix[line_int_ceiling_1, line_int_ceiling_2]
            - left_matrix[line_int_ceiling_1, line_in_glazing_n]
            - left_matrix[line_int_ceiling_1, line_in_glazing_e]
            - left_matrix[line_int_ceiling_1, line_in_glazing_s]
            - left_matrix[line_int_ceiling_1, line_in_glazing_w]
            - left_matrix[line_int_ceiling_1, line_in_frame_n]
            - left_matrix[line_int_ceiling_1, line_in_frame_e]
            - left_matrix[line_int_ceiling_1, line_in_frame_s]
            - left_matrix[line_int_ceiling_1, line_in_frame_w]
            - left_matrix[line_int_ceiling_1, line_wall_n_1]
            - left_matrix[line_int_ceiling_1, line_wall_e_1]
            - left_matrix[line_int_ceiling_1, line_wall_s_1]
            - left_matrix[line_int_ceiling_1, line_wall_w_1]
            - left_matrix[line_int_ceiling_1, line_roof_1]
            - left_matrix[line_int_ceiling_1, line_floor_1]
            - left_matrix[line_int_ceiling_1, line_int_wall_1]
        )

        # temperature of the 2. node of the external wall in north direction
        left_matrix[line_wall_n_2, line_wall_n_1] = left_matrix[line_wall_n_1, line_wall_n_2]
        left_matrix[line_wall_n_2, line_wall_n_3] = -wall_area_n * time_step * 1 / (1 / wall_inside_lambda * wall_inside_thickness *  0.25 + 1 / wall_outside_lambda * wall_outside_thickness * 0.25)
        left_matrix[line_wall_n_2, line_wall_n_2] = (
            wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5
            - left_matrix[line_wall_n_2, line_wall_n_1]
            - left_matrix[line_wall_n_2, line_wall_n_3]
        )

        # temperature of the 2. node of the external wall in east direction
        left_matrix[line_wall_e_2, line_wall_e_1] = left_matrix[line_wall_e_1, line_wall_e_2]
        left_matrix[line_wall_e_2, line_wall_e_3] = -wall_area_e * time_step * 1 / (1 / wall_inside_lambda * wall_inside_thickness *  0.25 + 1 / wall_outside_lambda * wall_outside_thickness * 0.25)
        left_matrix[line_wall_e_2, line_wall_e_2] = (
            wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5
            - left_matrix[line_wall_e_2, line_wall_e_1]
            - left_matrix[line_wall_e_2, line_wall_e_3]
        )

        # temperature of the 2. node of the external wall in south direction
        left_matrix[line_wall_s_2, line_wall_s_1] = left_matrix[line_wall_s_1, line_wall_s_2]
        left_matrix[line_wall_s_2, line_wall_s_3] = -wall_area_s * time_step * 1 / (1 / wall_inside_lambda * wall_inside_thickness *  0.25 + 1 / wall_outside_lambda * wall_outside_thickness * 0.25)
        left_matrix[line_wall_s_2, line_wall_s_2] = (
            wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5
            - left_matrix[line_wall_s_2, line_wall_s_1]
            - left_matrix[line_wall_s_2, line_wall_s_3]
        )

        # temperature of the 2. node of the external wall in west direction
        left_matrix[line_wall_w_2, line_wall_w_1] = left_matrix[line_wall_w_1, line_wall_w_2]
        left_matrix[line_wall_w_2, line_wall_w_3] = -wall_area_w * time_step * 1 / (1 / wall_inside_lambda * wall_inside_thickness *  0.25 + 1 / wall_outside_lambda * wall_outside_thickness * 0.25)
        left_matrix[line_wall_w_2, line_wall_w_2] = (
            wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5
            - left_matrix[line_wall_w_2, line_wall_w_1]
            - left_matrix[line_wall_w_2, line_wall_w_3]
        )

        # temperature of the 2. node of the roof
        left_matrix[line_roof_2, line_roof_1] = left_matrix[line_roof_1, line_roof_2]
        left_matrix[line_roof_2, line_roof_3] = -roof_area * time_step * 1 / (1 / roof_inside_lambda * roof_inside_thickness *  0.25 + 1 / roof_outside_lambda * roof_outside_thickness * 0.25)
        left_matrix[line_roof_2, line_roof_2] = (
            roof_area * roof_inside_capacity_density * roof_inside_thickness * 0.5
            - left_matrix[line_roof_2, line_roof_1]
            - left_matrix[line_roof_2, line_roof_3]
        )

        # temperature of the 2. node of the floor
        left_matrix[line_floor_2, line_floor_1] = left_matrix[line_floor_1, line_floor_2]
        left_matrix[line_floor_2, line_floor_3] = -floor_area * time_step * 1 / (1 / floor_inside_lambda * floor_inside_thickness *  0.25 + 1 / floor_outside_lambda * floor_outside_thickness * 0.25)
        left_matrix[line_floor_2, line_floor_2] = (
            floor_area * floor_inside_capacity_density * floor_inside_thickness * 0.5
            - left_matrix[line_floor_2, line_floor_1]
            - left_matrix[line_floor_2, line_floor_3]
        )

        # temperature of the 2. node of the internal walls
        left_matrix[line_int_wall_2, line_int_wall_1] = left_matrix[line_int_wall_1, line_int_wall_2]
        left_matrix[line_int_wall_2, line_int_wall_3] = -int_wall_area * time_step * 1 / (1 / int_wall_lambda * int_wall_thickness *   0.125)
        left_matrix[line_int_wall_2, line_int_wall_2] = (
            int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125
            - left_matrix[line_int_wall_2, line_int_wall_1]
            - left_matrix[line_int_wall_2, line_int_wall_3]
        )

        # temperature of the 2. node of the internal ceilings
        left_matrix[line_int_ceiling_2, line_int_ceiling_1] = left_matrix[line_int_ceiling_1, line_int_ceiling_2]
        left_matrix[line_int_ceiling_2, line_int_ceiling_3] = -int_ceiling_area * time_step * 1 / (1 / int_ceiling_lambda * int_ceiling_thickness *   0.125)
        left_matrix[line_int_ceiling_2, line_int_ceiling_2] = (
            int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125
            - left_matrix[line_int_ceiling_2, line_int_ceiling_1]
            - left_matrix[line_int_ceiling_2, line_int_ceiling_3]
        )

        # temperature of the 3. node of the external wall in north direction
        left_matrix[line_wall_n_3, line_wall_n_2] = left_matrix[line_wall_n_2, line_wall_n_3]
        left_matrix[line_wall_n_3, line_wall_n_4] = -wall_area_n * time_step * wall_outside_lambda / wall_outside_thickness / 0.75
        left_matrix[line_wall_n_3, line_wall_n_3] = (
            wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5
            - left_matrix[line_wall_n_3, line_wall_n_2]
            - left_matrix[line_wall_n_3, line_wall_n_4]
        )

        # temperature of the 3. node of the external wall in east direction
        left_matrix[line_wall_e_3, line_wall_e_2] = left_matrix[line_wall_e_2, line_wall_e_3]
        left_matrix[line_wall_e_3, line_wall_e_4] = -wall_area_e * time_step * wall_outside_lambda / wall_outside_thickness / 0.75
        left_matrix[line_wall_e_3, line_wall_e_3] = (
            wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5
            - left_matrix[line_wall_e_3, line_wall_e_2]
            - left_matrix[line_wall_e_3, line_wall_e_4]
        )

        # temperature of the 3. node of the external wall in south direction
        left_matrix[line_wall_s_3, line_wall_s_2] = left_matrix[line_wall_s_2, line_wall_s_3]
        left_matrix[line_wall_s_3, line_wall_s_4] = -wall_area_s * time_step * wall_outside_lambda / wall_outside_thickness / 0.75
        left_matrix[line_wall_s_3, line_wall_s_3] = (
            wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5
            - left_matrix[line_wall_s_3, line_wall_s_2]
            - left_matrix[line_wall_s_3, line_wall_s_4]
        )

        # temperature of the 3. node of the external wall in west direction
        left_matrix[line_wall_w_3, line_wall_w_2] = left_matrix[line_wall_w_2, line_wall_w_3]
        left_matrix[line_wall_w_3, line_wall_w_4] = -wall_area_w * time_step * wall_outside_lambda / wall_outside_thickness / 0.75
        left_matrix[line_wall_w_3, line_wall_w_3] = (
            wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5
            - left_matrix[line_wall_w_3, line_wall_w_2]
            - left_matrix[line_wall_w_3, line_wall_w_4]
        )

        # temperature of the 3. node of the roof
        left_matrix[line_roof_3, line_roof_2] = left_matrix[line_roof_2, line_roof_3]
        left_matrix[line_roof_3, line_roof_4] = -roof_area * time_step * roof_outside_lambda / roof_outside_thickness / 0.75
        left_matrix[line_roof_3, line_roof_3] = (
            roof_area * roof_outside_capacity_density * roof_outside_thickness * 0.5
            - left_matrix[line_roof_3, line_roof_2]
            - left_matrix[line_roof_3, line_roof_4]
        )

        # temperature of the 3. node of the floor
        left_matrix[line_floor_3, line_floor_2] = left_matrix[line_floor_2, line_floor_3]
        left_matrix[line_floor_3, line_floor_4] = -floor_area * time_step * floor_outside_lambda / floor_outside_thickness / 0.75
        left_matrix[line_floor_3, line_floor_3] = (
            floor_area * floor_outside_capacity_density * floor_outside_thickness * 0.5
            - left_matrix[line_floor_3, line_floor_2]
            - left_matrix[line_floor_3, line_floor_4]
        )

        # temperature of the 3. node of the internal walls
        left_matrix[line_int_wall_3, line_int_wall_2] = left_matrix[line_int_wall_2, line_int_wall_3]
        left_matrix[line_int_wall_3, line_int_wall_4] = -int_wall_area * time_step * 1 / (1 / int_wall_lambda * int_wall_thickness *   0.125)
        left_matrix[line_int_wall_3, line_int_wall_3] = (
            int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125
            - left_matrix[line_int_wall_3, line_int_wall_2]
            - left_matrix[line_int_wall_3, line_int_wall_4]
        )

        # temperature of the 3. node of the internal ceilings
        left_matrix[line_int_ceiling_3, line_int_ceiling_2] = left_matrix[line_int_ceiling_2, line_int_ceiling_3]
        left_matrix[line_int_ceiling_3, line_int_ceiling_4] = -int_ceiling_area * time_step * 1 / (1 / int_ceiling_lambda * int_ceiling_thickness *   0.125)
        left_matrix[line_int_ceiling_3, line_int_ceiling_3] = (
            int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125
            - left_matrix[line_int_ceiling_3, line_int_ceiling_2]
            - left_matrix[line_int_ceiling_3, line_int_ceiling_4]
        )

        # temperature of the 4. node of the external wall in north direction
        left_matrix[line_wall_n_4, line_wall_n_3] = left_matrix[line_wall_n_3, line_wall_n_4]
        left_matrix[line_wall_n_4, line_wall_n_4] = (
            wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5
            + wall_area_n * surf_htc_out * time_step
            - left_matrix[line_wall_n_4, line_wall_n_3]
        )

        # temperature of the 4. node of the external wall in east direction
        left_matrix[line_wall_e_4, line_wall_e_3] = left_matrix[line_wall_e_3, line_wall_e_4]
        left_matrix[line_wall_e_4, line_wall_e_4] = (
            wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5
            + wall_area_e * surf_htc_out * time_step
            - left_matrix[line_wall_e_4, line_wall_e_3]
        )

        # temperature of the 4. node of the external wall in south direction
        left_matrix[line_wall_s_4, line_wall_s_3] = left_matrix[line_wall_s_3, line_wall_s_4]
        left_matrix[line_wall_s_4, line_wall_s_4] = (
            wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5
            + wall_area_s * surf_htc_out * time_step
            - left_matrix[line_wall_s_4, line_wall_s_3]
        )

        # temperature of the 4. node of the external wall in west direction
        left_matrix[line_wall_w_4, line_wall_w_3] = left_matrix[line_wall_w_3, line_wall_w_4]
        left_matrix[line_wall_w_4, line_wall_w_4] = (
            wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5
            + wall_area_w * surf_htc_out * time_step
            - left_matrix[line_wall_w_4, line_wall_w_3]
        )

        # temperature of the 4. node of the roof
        left_matrix[line_roof_4, line_roof_3] = left_matrix[line_roof_3, line_roof_4]
        left_matrix[line_roof_4, line_roof_4] = (
            roof_area * roof_outside_capacity_density * roof_outside_thickness * 0.5
            + roof_area * surf_htc_out * time_step
            - left_matrix[line_roof_4, line_roof_3]
        )

        # temperature of the 4. node of the floor
        left_matrix[line_floor_4, line_floor_3] = left_matrix[line_floor_3, line_floor_4]
        left_matrix[line_floor_4, line_floor_4] = (
            floor_area * floor_outside_capacity_density * floor_outside_thickness * 0.5
            + floor_area * surf_htc_out * time_step
            - left_matrix[line_floor_4, line_floor_3]
        )

        # temperature of the 4. node of the internal walls
        left_matrix[line_int_wall_4, line_int_wall_3] = left_matrix[line_int_wall_3, line_int_wall_4]
        left_matrix[line_int_wall_4, line_int_wall_4] = (
            int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125
            - left_matrix[line_int_wall_4, line_int_wall_3]
        )

        # temperature of the 4. node of the internal ceilings
        left_matrix[line_int_ceiling_4, line_int_ceiling_3] = left_matrix[line_int_ceiling_3, line_int_ceiling_4]
        left_matrix[line_int_ceiling_4, line_int_ceiling_4] = (
            int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125
            - left_matrix[line_int_ceiling_4, line_int_ceiling_3]
        )

        # endregion

        #  --------------------------------------------------------------
        # calculate inverse matrix
        #  --------------------------------------------------------------
        inverse_matrix = np.linalg.inv(left_matrix)

        #  --------------------------------------------------------------
        # get the amount of hours from the weather data
        #  --------------------------------------------------------------
        weather_file_size = ambient_temp.size

        # --------------------------------------------------------------
        # declare initial and resulting temperature vectors
        # --------------------------------------------------------------
        initial_temperatures = np.full(49, 20.0) # initial temperature vector (49 temperatures)
        output_temperatures = np.zeros((8760, 49))
        output_heating_power = np.zeros((8760, 1))
        output_cooling_power = np.zeros((8760, 1))
        output_lighting_electricity = np.zeros((8760, 1))
        output_equipment_electricity = np.zeros((8760, 1))

        #  --------------------------------------------------------------
        # region: run the simulation for the number of hours in the weather data
        #  --------------------------------------------------------------
        right_matrix = np.zeros(49, dtype=float)

        steps_per_hour = int(3600 / time_step)

        # hour_counter = 1

        for i in range(1, weather_file_size): # loop over all hours in the weather data. i = 1..N-1 (actual hour)
            hour = (i % 24) or 24 # hour = 1..24 (ensure hour is between 1 and 24) (modulo and fallback operation)
            for k in range(steps_per_hour): # loop over all time steps in one hour. k = 0..steps_per_hour-1
                alpha = (k + 1) * time_step / 3600 # alpha = 0..1 (fraction of the hour)
                i_prev = i - 1 # index for previous hour
                i_curr = i     # index for current hour


                # interpolation of wather data
                interpolated_amb_temp = ambient_temp[i_prev] + alpha * (ambient_temp[i_curr] - ambient_temp[i_prev])
                interpolated_sun_flux_n = sun_flux_north[i_prev] + alpha * (sun_flux_north[i_curr] - sun_flux_north[i_prev])
                interpolated_sun_flux_e = sun_flux_east[i_prev] + alpha * (sun_flux_east[i_curr] - sun_flux_east[i_prev])
                interpolated_sun_flux_s = sun_flux_south[i_prev] + alpha * (sun_flux_south[i_curr] - sun_flux_south[i_prev])
                interpolated_sun_flux_w = sun_flux_west[i_prev] + alpha * (sun_flux_west[i_curr] - sun_flux_west[i_prev])
                interpolated_sun_flux_r = sun_flux_roof[i_prev] + alpha * ( sun_flux_roof[i_curr] - sun_flux_roof[i_prev])
                interpolated_diff_rad = diff_radiation[i_prev] + alpha * (diff_radiation[i_curr] - diff_radiation[i_prev])
                interpolated_global_rad = global_radiation[i_prev] + alpha * (global_radiation[i_curr] - global_radiation[i_prev])
                interpolated_shading_flux = (0.5 * interpolated_diff_rad + 0.2 * 0.5 * interpolated_global_rad)
                interpolated_ground_temp = 15 - 5 * np.cos(np.deg2rad((i_curr - 31 * 2 * 24) *360 / 8760))
                interpolated_unheated_temp = 18 - 3 * np.cos(np.deg2rad((i_curr - 31 * 2 * 24) *360 / 8760))
            
                # calculation of shading
                shading_value_shaded_windows_north = 1.0
                shading_value_shaded_windows_east = 1.0
                shading_value_shaded_windows_south = 1.0
                shading_value_shaded_windows_west = 1.0
            
                if initial_temperatures[line_air] > 23.0 and interpolated_shading_flux > 200.0:
                    shading_value_shaded_windows_north = shading_g_value_reduction_factor
                    shading_value_shaded_windows_east = shading_g_value_reduction_factor
                    shading_value_shaded_windows_south = shading_g_value_reduction_factor
                    shading_value_shaded_windows_west = shading_g_value_reduction_factor
                
                shading_value_unshaded_windows_north = 1.0
                shading_value_unshaded_windows_east = 1.0
                shading_value_unshaded_windows_south = 1.0
                shading_value_unshaded_windows_west = 1.0

                if initial_temperatures[line_air] > 23.0:
                    if interpolated_sun_flux_n > 200.0:
                        shading_value_unshaded_windows_north = shading_g_value_reduction_factor
                    if interpolated_sun_flux_e > 200.0:
                        shading_value_unshaded_windows_east = shading_g_value_reduction_factor
                    if interpolated_sun_flux_s > 200.0:
                        shading_value_unshaded_windows_south = shading_g_value_reduction_factor
                    if interpolated_sun_flux_w > 200.0:
                        shading_value_unshaded_windows_west = shading_g_value_reduction_factor

                total_sun_heat_gain = (
                    shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n  
                    + shading_value_shaded_windows_north * shaded_glazing_area_n * interpolated_shading_flux  
                    + shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e 
                    + shading_value_shaded_windows_east * shaded_glazing_area_e * interpolated_shading_flux 
                    + shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s 
                    + shading_value_shaded_windows_south * shaded_glazing_area_s * interpolated_shading_flux 
                    + shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w 
                    + shading_value_shaded_windows_west * shaded_glazing_area_w * interpolated_shading_flux
                )

                int_heat_gain = occupancy_schedule[hour-1] * occupancy_power + equipment_schedule[hour-1] * equipment_power

                if lighting_schedule[hour-1] > 0:
                    if ((shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n
                        + shading_value_shaded_windows_north * shaded_glazing_area_n * interpolated_shading_flux) / glazing_area_n) < 15.0:
                            int_heat_gain = int_heat_gain + lighting_schedule[hour-1] * lighting_power * lighting_north_side
                    
                    if ((
                        shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e
                        + shading_value_shaded_windows_east * shaded_glazing_area_e * interpolated_shading_flux) / glazing_area_e) < 15.0:
                            int_heat_gain = int_heat_gain + lighting_schedule[hour-1] * lighting_power * lighting_east_side
                    
                    if ((
                        shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s 
                        + shading_value_shaded_windows_south * shaded_glazing_area_s * interpolated_shading_flux) / glazing_area_s) < 15.0:
                            int_heat_gain = int_heat_gain + lighting_schedule[hour-1] * lighting_power * lighting_south_side

                    if ((
                        shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w
                        + shading_value_shaded_windows_west * shaded_glazing_area_w * interpolated_shading_flux) / glazing_area_w) < 15.0:
                            int_heat_gain = int_heat_gain + lighting_schedule[hour-1] * lighting_power * lighting_west_side
                
                # air temperature equation
                right_matrix[line_air] = (
                    building_height * floor_area * 1006 * 1.185 * initial_temperatures[line_air]
                    + wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp
                    + thermal_bridges * time_step * interpolated_amb_temp
                    + (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp
                    + int_heat_gain_to_air_coef * int_heat_gain * time_step
                )

                # temperature of the inside nod of the north glazing
                right_matrix[line_in_glazing_n] = (
                        int_heat_gain_to_glazing_n_coef * int_heat_gain * time_step
                        + time_step * sun_heat_gain_to_inside_glazing * (
                            shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n
                            + shading_value_shaded_windows_north * shaded_glazing_area_n * interpolated_shading_flux
                        )
                )

                # temperature of the inside nod of the east glazing
                right_matrix[line_in_glazing_e] = (
                        int_heat_gain_to_glazing_e_coef * int_heat_gain * time_step
                        + time_step * sun_heat_gain_to_inside_glazing * (
                            shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e
                            + shading_value_shaded_windows_east * shaded_glazing_area_e * interpolated_shading_flux
                        )
                )

                # temperature of the inside nod of the south glazing
                right_matrix[line_in_glazing_s] = (
                        int_heat_gain_to_glazing_s_coef * int_heat_gain * time_step
                        + time_step * sun_heat_gain_to_inside_glazing * (
                            shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s
                            + shading_value_shaded_windows_south * shaded_glazing_area_s * interpolated_shading_flux
                        )
                )

                # temperature of the inside nod of the west glazing
                right_matrix[line_in_glazing_w] = (
                        int_heat_gain_to_glazing_w_coef * int_heat_gain * time_step
                        + time_step * sun_heat_gain_to_inside_glazing * (
                            shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w
                            + shading_value_shaded_windows_west * shaded_glazing_area_w * interpolated_shading_flux
                        )
                )

                # temperature of the outside nod of the north glazing
                right_matrix[line_out_glazing_n] = (
                    time_step * sun_heat_gain_to_outside_glazing * (
                        shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n
                        + shading_value_shaded_windows_north * shaded_glazing_area_n * interpolated_shading_flux
                        )
                    + interpolated_amb_temp * glazing_area_n * surf_htc_out * time_step
                )
                        
                # temperature of the outside nod of the east glazing
                right_matrix[line_out_glazing_e] = (
                    time_step * sun_heat_gain_to_outside_glazing * (
                        shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e
                        + shading_value_shaded_windows_east * shaded_glazing_area_e * interpolated_shading_flux
                        )
                    + interpolated_amb_temp * glazing_area_e * surf_htc_out * time_step
                )

                # temperature of the outside nod of the south glazing
                right_matrix[line_out_glazing_s] = (
                    time_step * sun_heat_gain_to_outside_glazing * (
                        shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s
                        + shading_value_shaded_windows_south * shaded_glazing_area_s * interpolated_shading_flux
                        )
                    + interpolated_amb_temp * glazing_area_s * surf_htc_out * time_step
                )

                # temperature of the outside nod of the west glazing
                right_matrix[line_out_glazing_w] = (
                    time_step * sun_heat_gain_to_outside_glazing * (
                        shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w
                        + shading_value_shaded_windows_west * shaded_glazing_area_w * interpolated_shading_flux
                        )
                    + interpolated_amb_temp * glazing_area_w * surf_htc_out * time_step
                )

                # temperature of the inside node of the north window frame
                right_matrix[line_in_frame_n] = int_heat_gain_to_frame_n_coef * int_heat_gain * time_step

                # temperature of the inside node of the east window frame
                right_matrix[line_in_frame_e] = int_heat_gain_to_frame_e_coef * int_heat_gain * time_step

                # temperature of the inside node of the south window frame
                right_matrix[line_in_frame_s] = int_heat_gain_to_frame_s_coef * int_heat_gain * time_step

                # temperature of the inside node of the west window frame
                right_matrix[line_in_frame_w] = int_heat_gain_to_frame_w_coef * int_heat_gain * time_step

                # temperature of the outside node of the north window frame
                right_matrix[line_out_frame_n] = (
                    (unshaded_frame_area_n * interpolated_sun_flux_n + shaded_frame_area_n * interpolated_shading_flux) * 0.8 * time_step
                    + interpolated_amb_temp * frame_area_n * surf_htc_out * time_step
                )

                # temperature of the outside node of the east window frame
                right_matrix[line_out_frame_e] = (
                    (unshaded_frame_area_e * interpolated_sun_flux_e + shaded_frame_area_e * interpolated_shading_flux) * 0.8 * time_step
                    + interpolated_amb_temp * frame_area_e * surf_htc_out * time_step
                )

                # temperature of the outside node of the south window frame
                right_matrix[line_out_frame_s] = (
                    (unshaded_frame_area_s * interpolated_sun_flux_s + shaded_frame_area_s * interpolated_shading_flux) * 0.8 * time_step
                    + interpolated_amb_temp * frame_area_s * surf_htc_out * time_step
                )

                # temperature of the outside node of the west window frame
                right_matrix[line_out_frame_w] = (
                    (unshaded_frame_area_w * interpolated_sun_flux_w + shaded_frame_area_w * interpolated_shading_flux) * 0.8 * time_step
                    + interpolated_amb_temp * frame_area_w * surf_htc_out * time_step
                )

                # temperature of the 1. node of north wall
                right_matrix[line_wall_n_1] = (
                    wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_n_1]
                    + int_heat_gain_to_wall_n_coef * int_heat_gain * time_step
                )

                # temperature of the 1. node of east wall
                right_matrix[line_wall_e_1] = (
                    wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_e_1]
                    + int_heat_gain_to_wall_e_coef * int_heat_gain * time_step
                )

                # temperature of the 1. node of south wall
                right_matrix[line_wall_s_1] = (
                    wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_s_1]
                    + int_heat_gain_to_wall_s_coef * int_heat_gain * time_step
                )

                # temperature of the 1. node of west wall
                right_matrix[line_wall_w_1] = (
                    wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_w_1]
                    + int_heat_gain_to_wall_w_coef * int_heat_gain * time_step
                )

                # temperature of the 1. node of the roof
                right_matrix[line_roof_1] = (
                    roof_area * roof_inside_capacity_density * roof_inside_thickness * 0.5 * initial_temperatures[line_roof_1]
                    + int_heat_gain_to_roof_coef * int_heat_gain * time_step
                )
                
                # temperature of the 1. node of the floor
                right_matrix[line_floor_1] = (
                    floor_area * floor_inside_capacity_density * floor_inside_thickness * 0.5 * initial_temperatures[line_floor_1]
                    + int_heat_gain_to_floor_coef * int_heat_gain * time_step
                )
                
                # temperature of the 1. node of the internal walls
                right_matrix[line_int_wall_1] = (
                    int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures[line_int_wall_1]
                    + sun_heat_gain_to_int_wall * total_sun_heat_gain * time_step
                    + int_heat_gain_to_int_wall_coef * int_heat_gain * time_step
                )

                # temperature of the 1. node of the internal ceilings
                right_matrix[line_int_ceiling_1] = (
                    int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures[line_int_ceiling_1]
                    + sun_heat_gain_to_int_ceiling * total_sun_heat_gain * time_step
                    + int_heat_gain_to_int_ceiling_coef * int_heat_gain * time_step
                )

                # temperature of the 2. node of the north wall
                right_matrix[line_wall_n_2] = (
                    wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_n_2]
                )

                # temperature of the 2. node of the east wall
                right_matrix[line_wall_e_2] = (
                    wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_e_2]
                )

                # temperature of the 2. node of the south wall
                right_matrix[line_wall_s_2] = (
                    wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_s_2]
                )

                # temperature of the 2. node of the west wall
                right_matrix[line_wall_w_2] = (
                    wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_w_2]
                )

                # temperature of the 2. node of the roof
                right_matrix[line_roof_2] = (
                    roof_area * roof_inside_capacity_density * roof_inside_thickness * 0.5 * initial_temperatures[line_roof_2]
                )

                # temperature of the 2. node of the floor
                right_matrix[line_floor_2] = (
                    floor_area * floor_inside_capacity_density * floor_inside_thickness * 0.5 * initial_temperatures[line_floor_2]
                )

                # temperature of the 2. node of the internal walls
                right_matrix[line_int_wall_2] = (
                    int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures[line_int_wall_2]
                )

                # temperature of the 2. node of the internal ceilings
                right_matrix[line_int_ceiling_2] = (
                    int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures[line_int_ceiling_2]
                )

                # temperature of the 3. node of the north wall
                right_matrix[line_wall_n_3] = (
                    wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_n_3]
                )

                # temperature of the 3. node of the east wall
                right_matrix[line_wall_e_3] = (
                    wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_e_3]
                )
                # temperature of the 3. node of the south wall
                right_matrix[line_wall_s_3] = (
                    wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_s_3]
                )

                # temperature of the 3. node of the west wall
                right_matrix[line_wall_w_3] = (
                    wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_w_3]
                )

                # temperature of the 3. node of the roof
                right_matrix[line_roof_3] = (
                    roof_area * roof_outside_capacity_density * roof_outside_thickness * 0.5 * initial_temperatures[line_roof_3]
                )

                # temperature of the 3. node of the floor
                right_matrix[line_floor_3] = (
                    floor_area * floor_outside_capacity_density * floor_outside_thickness * 0.5 * initial_temperatures[line_floor_3]
                )
                # temperature of the 3. node of the internal walls
                right_matrix[line_int_wall_3] = (
                    int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures[line_int_wall_3]
                )
                # temperature of the 3. node of the internal ceilings
                right_matrix[line_int_ceiling_3] = (
                    int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures[line_int_ceiling_3]
                )
                # temperature of the 4. node of the north wall
                right_matrix[line_wall_n_4] = (
                    wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_n_4]
                    + interpolated_amb_temp * wall_area_n * surf_htc_out * time_step
                    + 0.8 * interpolated_sun_flux_n * wall_area_n * time_step
                )
                # temperature of the 4. node of the east wall
                right_matrix[line_wall_e_4] = (
                    wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_e_4]
                    + interpolated_amb_temp * wall_area_e * surf_htc_out * time_step
                    + 0.8 * interpolated_sun_flux_e * wall_area_e * time_step
                )
                # temperature of the 4. node of the south wall
                right_matrix[line_wall_s_4] = (
                    wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_s_4]
                    + interpolated_amb_temp * wall_area_s * surf_htc_out * time_step
                    + 0.8 * interpolated_sun_flux_s * wall_area_s * time_step
                )
                # temperature of the 4. node of the west wall
                right_matrix[line_wall_w_4] = (
                    wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_w_4]
                    + interpolated_amb_temp * wall_area_w * surf_htc_out * time_step
                    + 0.8 * interpolated_sun_flux_w * wall_area_w * time_step
                )
                # temperature of the 4. node of the roof
                right_matrix[line_roof_4] = (
                    roof_area * roof_outside_capacity_density * roof_outside_thickness * 0.5 * initial_temperatures[line_roof_4]
                    + interpolated_amb_temp * roof_area * surf_htc_out * time_step
                    + 0.8 * interpolated_sun_flux_r * roof_area * time_step
                )
                # temperature of the 4. node of the floor
                right_matrix[line_floor_4] = (
                    floor_area * floor_outside_capacity_density * floor_outside_thickness * 0.5 * initial_temperatures[line_floor_4]
                    + interpolated_ground_temp * floor_area * surf_htc_out * time_step
                )

                # temperature of the 4. node of the internal walls
                right_matrix[line_int_wall_4] = (
                    int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures[line_int_wall_4]
                )
                # temperature of the 4. node of the internal ceilings
                right_matrix[line_int_ceiling_4] = (
                    int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures[line_int_ceiling_4]
                )

                initial_temperatures = inverse_matrix @ right_matrix

                heating_power = 0.0
                cooling_power = 0.0

                if initial_temperatures[line_air] < heating_setpoint:
                    for j in range(5):
                        heating_power = heating_power + left_matrix[line_air, line_air] * (heating_setpoint - initial_temperatures[line_air].item()) / time_step
                        right_matrix[line_air] = (
                            building_height * floor_area * 1006 * 1.185 * initial_temperatures[line_air].item()
                            + wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp
                            + thermal_bridges * time_step * interpolated_amb_temp
                            + (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp
                            + int_heat_gain_to_air_coef * int_heat_gain * time_step
                            + heating_power * time_step
                        )
                        initial_temperatures = inverse_matrix @ right_matrix

                elif initial_temperatures[line_air] > cooling_setpoint:
                    for j in range(5):
                        cooling_power = cooling_power + left_matrix[line_air, line_air] * (initial_temperatures[line_air].item() - cooling_setpoint) / time_step
                        right_matrix[line_air] = (
                            building_height * floor_area * 1006 * 1.185 * initial_temperatures[line_air].item()
                            + wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp
                            + thermal_bridges * time_step * interpolated_amb_temp
                            + (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp
                            + int_heat_gain_to_air_coef * int_heat_gain * time_step
                            - cooling_power * time_step
                        )
                        initial_temperatures = inverse_matrix @ right_matrix

                skip_hours = weather_file_size - 8760 # to store only the last year of the simulation results
                if i > skip_hours:
                    out_idx = i - skip_hours
                    output_heating_power[out_idx] += heating_power * time_step / 3600
                    output_cooling_power[out_idx] += cooling_power * time_step / 3600
                    output_lighting_electricity[out_idx] += (
                        (int_heat_gain - occupancy_schedule[hour - 1] * occupancy_power - equipment_schedule[hour - 1] * equipment_power) * time_step / 3600
                    )
                    output_equipment_electricity[out_idx] += (
                        equipment_schedule[hour - 1] * equipment_power * time_step / 3600
                    )
                # if i > weather_file_size - 8760:
                #     out_idx = i -1 - weather_file_size + 8760
                #     output_heating_power[out_idx] += heating_power * time_step / 3600
            skip_hours = weather_file_size - 8760
            if i > skip_hours:
                out_idx = i - skip_hours
                output_temperatures[out_idx, :] = initial_temperatures


        # output_heating_power_sum = output_heating_power.sum() / 1e6
        # output_cooling_power_sum = output_cooling_power.sum() / 1e6
        # output_lighting_electricity_sum = output_lighting_electricity.sum() / 1e6
        # output_equipment_electricity_sum = output_equipment_electricity.sum() / 1e6
        # endregion

        Temp_outside_air = ambient_temp[-8760:]

        if isinstance(weather_df.index, pd.DatetimeIndex):
            # takes the datetime index form the last year of the weather data.
            # This is useful when the weather data more the one year.
            result_index = weather_df.index[-output_temperatures.shape[0]:]
        else:
            # fallback to RangeIndex if no DatetimeIndex is available
            result_index = pd.RangeIndex(output_temperatures.shape[0]) 

        #  return results as a DataFrame
        df_raw = pd.DataFrame({
            'temperature_outdoor_air': ambient_temp[-output_temperatures.shape[0]:],    # [°C]
            'temperature_air_room': output_temperatures[:, 0],                          # [°C]
            'temperature_in_glazing_north': output_temperatures[:, 1],                  # [°C]
            'temperature_in_glazing_east': output_temperatures[:, 2],                   # [°C]
            'temperature_in_glazing_south': output_temperatures[:, 3],                  # [°C]
            'temperature_in_glazing_west': output_temperatures[:, 4],                   # [°C]
            'temperature_out_glazing_north': output_temperatures[:, 5],                 # [°C]
            'temperature_out_glazing_east': output_temperatures[:, 6],                  # [°C]
            'temperature_out_glazing_south': output_temperatures[:, 7],                 # [°C]
            'temperature_out_glazing_west': output_temperatures[:, 8],                  # [°C]
            'temperature_in_frame_north': output_temperatures[:, 9],                    # [°C]
            'temperature_in_frame_east': output_temperatures[:, 10],                    # [°C]
            'temperature_in_frame_south': output_temperatures[:, 11],                   # [°C]
            'temperature_in_frame_west': output_temperatures[:, 12],                    # [°C]
            'temperature_out_frame_north': output_temperatures[:, 13],                  # [°C]
            'temperature_out_frame_east': output_temperatures[:, 14],                   # [°C]
            'temperature_out_frame_south': output_temperatures[:, 15],                  # [°C]
            'temperature_out_frame_west': output_temperatures[:, 16],                   # [°C]
            'temperature_wall_n_1': output_temperatures[:, 17],                         # [°C]
            'temperature_wall_e_1': output_temperatures[:, 18],                         # [°C]
            'temperature_wall_s_1': output_temperatures[:, 19],                         # [°C]
            'temperature_wall_w_1': output_temperatures[:, 20],                         # [°C]
            'temperature_roof_1': output_temperatures[:, 21],                           # [°C]
            'temperature_floor_1': output_temperatures[:, 22],                          # [°C]
            'temperature_int_wall_1': output_temperatures[:, 23],                       # [°C]
            'temperature_int_ceiling_1': output_temperatures[:, 24],                    # [°C]
            'temperature_wall_n_2': output_temperatures[:, 25],                         # [°C]
            'temperature_wall_e_2': output_temperatures[:, 26],                         # [°C]
            'temperature_wall_s_2': output_temperatures[:, 27],                         # [°C]
            'temperature_wall_w_2': output_temperatures[:, 28],                         # [°C]
            'temperature_roof_2': output_temperatures[:, 29],                           # [°C]
            'temperature_floor_2': output_temperatures[:, 30],                          # [°C]
            'temperature_int_wall_2': output_temperatures[:, 31],                       # [°C]
            'temperature_int_ceiling_2': output_temperatures[:, 32],                    # [°C]
            'temperature_wall_n_3': output_temperatures[:, 33],                         # [°C]
            'temperature_wall_e_3': output_temperatures[:, 34],                         # [°C]
            'temperature_wall_s_3': output_temperatures[:, 35],                         # [°C]
            'temperature_wall_w_3': output_temperatures[:, 36],                         # [°C]
            'temperature_roof_3': output_temperatures[:, 37],                           # [°C]
            'temperature_floor_3': output_temperatures[:, 38],                          # [°C]
            'temperature_int_wall_3': output_temperatures[:, 39],                       # [°C]
            'temperature_int_ceiling_3': output_temperatures[:, 40],                    # [°C]
            'temperature_wall_n_4': output_temperatures[:, 41],                         # [°C]
            'temperature_wall_e_4': output_temperatures[:, 42],                         # [°C]
            'temperature_wall_s_4': output_temperatures[:, 43],                         # [°C]
            'temperature_wall_w_4': output_temperatures[:, 44],                         # [°C]
            'temperature_roof_4': output_temperatures[:, 45],                           # [°C]
            'temperature_floor_4': output_temperatures[:, 46],                          # [°C]
            'temperature_int_wall_4': output_temperatures[:, 47],                       # [°C]
            'temperature_int_ceiling_4': output_temperatures[:, 48],                    # [°C]
            'output_heating_power': output_heating_power.flatten(),                     # [W]
            'output_cooling_power': output_cooling_power.flatten(),                     # [W]
            'output_lighting_electricity': output_lighting_electricity.flatten(),       # [W]
            'output_equipment_electricity': output_equipment_electricity.flatten(),     # [W]
        }, index=result_index)

        df_raw.index.name = "datetime"

        print("Simulation finished.")    
        return df_raw

# print(f"total heating power = {output_heating_power_sum} MWh")
# print(f"total cooling power = {output_cooling_power_sum} MWh")
# print(f"total lighting electricity = {output_lighting_electricity_sum} MWh")
# print(f"total equipment electricity = {output_equipment_electricity_sum} MWh")

# # save results as a binary file
# np.savez(
#     'py_out.npz', 
#     output_temperatures=output_temperatures, 
#     output_heating_power=output_heating_power, 
#     output_cooling_power=output_cooling_power, 
#     output_lighting_electricity=output_lighting_electricity, 
#     output_equipment_electricity=output_equipment_electricity,
#     left_matrix=left_matrix)
