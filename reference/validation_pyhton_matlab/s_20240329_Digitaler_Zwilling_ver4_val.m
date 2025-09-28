clear
% 1. Read weather file from "basel_dry.mat". The data starts from "00:00 18.12.2018" and ends at "23:00 31.12.2019"
% First column - Time of the year, [hours]
% Second column - air temperature, [C]
% Thrid column - relative humidity, [%] (currently not used)
% Fourth column - wind speed in X-direction, [m/s] (currently not used)
% Fifth column - wind speed in Y-direction, [m/s] (currently not used)
% Sixth column - direct sun radiation, [W/m^2]
% Seventh column - diffuse sun radiation, [W/m^2]
% Eigth column - sky cover, [] (currently not used)
% Nineth column - sun elevation, [°]
% Tenth column - sun azimuth, [°]
load("basel_dry_ver2.mat");
ambient_temp = basel_dry(:,2);
beam_radiation = basel_dry(:,6);
diff_radiation = basel_dry(:,7);
sun_elevation = basel_dry(:,9);
sun_azimuth = basel_dry(:,10);

% 2. Definition of areas and surface vectors of building constructions per
% north, east, south and west directions

% - unshaded (without permanent obstacles like balcony) glazing area
unshaded_glazing_area_n = 0.825 * (2.3 * 12 + 1.2 * 6 + 3 * 2.07); % [m^2]
unshaded_glazing_area_e = 0.825 * (3.45 * 3 + 2.3 * 3 + 1.98 * 1); % [m^2]
unshaded_glazing_area_s = 0.825 * (1.73 * 2 + 5.18 * 2 + 1.98 * 4 + 1.2 * 6 + 2.07 * 1); % [m^2]
unshaded_glazing_area_w = 0.825 * (3.45 * 3 + 2.3 * 3 + 2.07 * 1); % [m^2]

% - shaded (under permanent obstacle like balcony) glazing area
shaded_glazing_area_n = 0.0; % [m^2]
shaded_glazing_area_e = 0.825 * (1.98 * 2); % [m^2]
shaded_glazing_area_s = 0.825 * (1.73 * 4 + 5.18 * 4 + 1.98 * 8 + 2.07 * 2); % [m^2]
shaded_glazing_area_w = 0.825 * (2.07 * 2); % [m^2]

% - unshaded (without permanent obstacles like balcony) window frame area
unshaded_frame_area_n = 0.175 * (2.3 * 12 + 1.2 * 6 + 3 * 2.07); % [m^2]
unshaded_frame_area_e = 0.175 * (3.45 * 3 + 2.3 * 3 + 1.98 * 1); % [m^2]
unshaded_frame_area_s = 0.175 * (1.73 * 2 + 5.18 * 2 + 1.98 * 4 + 1.2 * 6 + 2.07 * 1); % [m^2]
unshaded_frame_area_w = 0.175 * (3.45 * 3 + 2.3 * 3 + 2.07 * 1); % [m^2]

% - shaded (under permanent obstacle like balcony) window frame area
shaded_frame_area_n = 0.0; % [m^2]
shaded_frame_area_e = 0.175 * (1.98 * 2); % [m^2]
shaded_frame_area_s = 0.175 * (1.73 * 4 + 5.18 * 4 + 1.98 * 8 + 2.07 * 2); % [m^2]
shaded_frame_area_w = 0.175 * (2.07 * 2); % [m^2]

% - total glazing area
glazing_area_n = unshaded_glazing_area_n + shaded_glazing_area_n; % [m^2]
glazing_area_e = unshaded_glazing_area_e + shaded_glazing_area_e; % [m^2]
glazing_area_s = unshaded_glazing_area_s + shaded_glazing_area_s; % [m^2]
glazing_area_w = unshaded_glazing_area_w + shaded_glazing_area_w; % [m^2]

% - total wibdiw frame area
frame_area_n = unshaded_frame_area_n + shaded_frame_area_n; % [m^2]
frame_area_e = unshaded_frame_area_e + shaded_frame_area_e; % [m^2]
frame_area_s = unshaded_frame_area_s + shaded_frame_area_s; % [m^2]
frame_area_w = unshaded_frame_area_w + shaded_frame_area_w; % [m^2]

% - areas of external walls
wall_area_n = 2.5 * 3 * (32.6 + 1.6 - 6.0) - glazing_area_n - frame_area_n; % [m^2], excluding glazings
wall_area_e = 2.5 * 3 * 14.0 - glazing_area_e - frame_area_e; % [m^2], excluding glazings
wall_area_s = 2.5 * 3 * (32.6 + 1.6) - glazing_area_s - frame_area_s; % [m^2], excluding glazings
wall_area_w = 2.5 * 3 * 14.0 - glazing_area_w - frame_area_w; % [m^2], excluding glazings

% - area of a roof against unheated or ambiency
roof_area = 313.8; % [m^2], excluding glazings

% - area of a floor against unheated or ground
floor_area = 313.8; % [m^2], excluding glazings

% - area of internal walls
int_wall_area = (72.975 + 91.9 + 2.0 * 19.75) * 3.0 ; % [m^2], both sides should be present

% - area of internal ceilings / floors
int_ceiling_area = 313.8 * 2.0 * 2.0; % [m^2], both sides should be present

% - area of walls against unheated zone like staircase
wall_against_unheated_area = (21.5 + 12.5 + 5.3) * 3.0;

% - orientation vectors of walls
surface_vector_north = [0.0 1.0 0.0];
surface_vector_east = [1.0 0.0 0.0];
surface_vector_south = [0.0 -1.0 0.0];
surface_vector_west = [-1.0 0.0 0.0];
surface_vector_roof = [0.0 0.0 1.0];

% - height of a building (needed for air temperature calculation)
building_height = 2.5 * 3; % [m]

% - sum of areas of all constructions excluding  walls against unheated
% zones
total_area_constructions = ...
    glazing_area_n + glazing_area_e + ...
    glazing_area_s + glazing_area_w + ...
    frame_area_n + frame_area_e + ...
    frame_area_s + frame_area_w + ...
    wall_area_n + wall_area_e + ...
    wall_area_s + wall_area_w + ...
    roof_area + floor_area + int_wall_area + int_ceiling_area;

% 2. Definition of U-values, G-values, T-values, (thermal capacities * density), thermal conductivity of building constructions 
glazing_u_value = 0.7;
glazing_g_value = 0.45;
shading_g_value_reduction_factor = 0.14;
frame_u_value = 2.0;

wall_against_unheated_u_value = 1 / (2 / 8.0 + 0.17 / 0.79);

wall_inside_lyamda = 1.8;
roof_inside_lyamda = 1.8;
floor_inside_lyamda = 1.8;

wall_inside_capacity_density = 2400 * 1100;
roof_inside_capacity_density = 2400 * 1100;
floor_inside_capacity_density = 2400 * 1100;

wall_outside_lyamda = 0.031;
roof_outside_lyamda = 0.02;
floor_outside_lyamda = 0.03;

wall_outside_capacity_density = 16 * 1400;
roof_outside_capacity_density = 30 * 1400;
floor_outside_capacity_density = 18 * 1400;

int_wall_lyamda = 0.79;
int_ceiling_lyamda = 1.8;

int_wall_capacity_density = 1070.0 * 850.0;
int_ceiling_capacity_density = 2400.0 * 1100.0;

% 3. Thickness of building constructions [m]

% - outside walls: inside layer - brick layer, outside layer - insulation
wall_inside_thickness = 0.2;
wall_outside_thickness = 0.1;

% - outside roof: inside layer - concrete layer, outside layer - insulation
roof_inside_thickness = 0.25;
roof_outside_thickness = 0.1;

% - floor against unheated zone / ground: inside layer - concrete layer, outside layer - insulation
floor_inside_thickness = 0.3;
floor_outside_thickness = 0.08;

% - internal walls and ceilings - no insulation layer
int_wall_thickness = 0.17;
int_ceiling_thickness = 0.3654;

% 4. Total infiltration rate [m^3/s]
infiltration_rate = 0.194444 * 0.001 * floor_area * 3.0;

% 5. Ventilation rate [m^3/s] (assumed to be always on) and heat-exchanger efficiency
air_ventilation_rate = 0.278 * 0.001 * floor_area * 3.0;
heat_exchanger_efficiency = 0.0;

% 6. Thermal bridges [W/K]
thermal_bridges = 123.4;

% 6. Differce power inputs [W]
occupancy_power = 70.0 * 0.033 * floor_area * 3.0;
lighting_power = 2.7 * floor_area * 3.0;
equipment_power = 8.0 * floor_area * 3.0;

% 7. Schedules [0..1]
occupancy_schedule = [1 1 1 1 1 1 0.6 0.4 0 0 0 0 0.8 0.4 0 0 0 0.4 0.8 0.8 0.8 1 1 1];
lighting_schedule = [0 0 0 0 0 0 1 1 0 0 0 0 1 1 0 0 0 1 1 1 1 0 0 0];
equipment_schedule = [0.1 0.1 0.1 0.1 0.1 0.2 0.8 0.2 0.1 0.1 0.1 0.1 0.8 0.2 0.1 0.1 0.1 0.2 0.8 1.0 0.2 0.2 0.2 0.1];

% 8. Definition of sun vector and global radiation
sun_vector = zeros(9096, 3);
global_radiation = zeros(9096, 1);
for i=1:9096
    if sun_elevation(i) > 0.0
       sun_vector(i, 1) = cosd(sun_elevation(i)) * sind(sun_azimuth(i));
       sun_vector(i, 2) = cosd(sun_elevation(i)) * cosd(sun_azimuth(i));
       sun_vector(i, 3) = -sind(sun_elevation(i));       
    end
    global_radiation(i) = diff_radiation(i) - beam_radiation(i) * sun_vector(i, 3);
end

% 9. Calculation of the sun flux on building surfaces: direct + diffuse + reflected, [W/m^2]
sun_flux_north = zeros(9096, 1);
sun_flux_east = zeros(9096, 1);
sun_flux_west = zeros(9096, 1);
sun_flux_south = zeros(9096, 1);
sun_flux_roof = zeros(9096, 1);
for i=1:9096
    if sun_elevation(i) > 0.0
        sun_flux_north(i) = -beam_radiation(i) * min(0.0, surface_vector_north(1) * sun_vector(i, 1) + surface_vector_north(2) * sun_vector(i, 2) + surface_vector_north(3) * sun_vector(i, 3)) + ...
            0.5 * diff_radiation(i) + ...
            0.2 * 0.5 * global_radiation(i);
        sun_flux_east(i) = -beam_radiation(i) * min(0.0, surface_vector_east(1) * sun_vector(i, 1) + surface_vector_east(2) * sun_vector(i, 2) + surface_vector_east(3) * sun_vector(i, 3)) + ...
            0.5 * diff_radiation(i) + ...
            0.2 * 0.5 * global_radiation(i);
        sun_flux_west(i) = -beam_radiation(i) * min(0.0, surface_vector_west(1) * sun_vector(i, 1) + surface_vector_west(2) * sun_vector(i, 2) + surface_vector_west(3) * sun_vector(i, 3)) + ...
            0.5 * diff_radiation(i) + ...
            0.2 * 0.5 * global_radiation(i);
        sun_flux_south(i) = -beam_radiation(i) * min(0.0, surface_vector_south(1) * sun_vector(i, 1) + surface_vector_south(2) * sun_vector(i, 2) + surface_vector_south(3) * sun_vector(i, 3)) + ...
            0.5 * diff_radiation(i) + ...
            0.2 * 0.5 * global_radiation(i);
        sun_flux_roof(i) = global_radiation(i);
    end
end

% 10. Definition of simulation parameters

% - simulation time step
time_step = 5.0 * 60; % [s]

% - surface heat transfer coefficient of internal surfaces
surf_htc_in = 4.5; % [W/m^2/K]

% - surface heat transfer coefficient of external surfaces
surf_htc_out = 23; % [W/m^2/K]

% - heating setpoint
heating_setpoint = 21; % [°C]

% - cooling setpoint
cooling_setpoint = 26; % [°C]

% - distribution of internal heat gains on building obstacles
int_heat_gain_to_air_coef = 0.6;
int_heat_gain_to_glazing_n_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_n / total_area_constructions;
int_heat_gain_to_glazing_e_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_e / total_area_constructions;
int_heat_gain_to_glazing_s_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_s / total_area_constructions;
int_heat_gain_to_glazing_w_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_w / total_area_constructions;
int_heat_gain_to_frame_n_coef = (1 - int_heat_gain_to_air_coef) * frame_area_n / total_area_constructions;
int_heat_gain_to_frame_e_coef = (1 - int_heat_gain_to_air_coef) * frame_area_e / total_area_constructions;
int_heat_gain_to_frame_s_coef = (1 - int_heat_gain_to_air_coef) * frame_area_s / total_area_constructions;
int_heat_gain_to_frame_w_coef = (1 - int_heat_gain_to_air_coef) * frame_area_w / total_area_constructions;
int_heat_gain_to_wall_n_coef = (1 - int_heat_gain_to_air_coef) * wall_area_n / total_area_constructions;
int_heat_gain_to_wall_e_coef = (1 - int_heat_gain_to_air_coef) * wall_area_e / total_area_constructions;
int_heat_gain_to_wall_s_coef = (1 - int_heat_gain_to_air_coef) * wall_area_s / total_area_constructions;
int_heat_gain_to_wall_w_coef = (1 - int_heat_gain_to_air_coef) * wall_area_w / total_area_constructions;
int_heat_gain_to_roof_coef = (1 - int_heat_gain_to_air_coef) * roof_area / total_area_constructions;
int_heat_gain_to_floor_coef = (1 - int_heat_gain_to_air_coef) * floor_area / total_area_constructions;
int_heat_gain_to_int_wall_coef = (1 - int_heat_gain_to_air_coef) * int_wall_area / total_area_constructions;
int_heat_gain_to_int_ceiling_coef = (1 - int_heat_gain_to_air_coef) * int_ceiling_area / total_area_constructions;

% - distribution of solar heat gains on building obstacles
sun_heat_gain_to_outside_glazing = 0.25 * (1.0 - glazing_g_value);
sun_heat_gain_to_inside_glazing = 0.25 * (1.0 - glazing_g_value) * glazing_g_value;
sun_heat_gain_to_int_wall = (1.0 - 0.25 * (1.0 - glazing_g_value)) * glazing_g_value * int_wall_area / (int_wall_area + int_ceiling_area);
sun_heat_gain_to_int_ceiling = (1.0 - 0.25 * (1.0 - glazing_g_value)) * glazing_g_value * int_ceiling_area / (int_wall_area + int_ceiling_area);

% - distribution of lightning power according to north, east, west, south
% directions
lighting_north_side = wall_area_n / (wall_area_n + wall_area_e + wall_area_s + wall_area_w);
lighting_east_side = wall_area_e / (wall_area_n + wall_area_e + wall_area_s + wall_area_w);
lighting_south_side = wall_area_s / (wall_area_n + wall_area_e + wall_area_s + wall_area_w);
lighting_west_side = wall_area_w / (wall_area_n + wall_area_e + wall_area_s + wall_area_w);

% - surface heat transfer cooeficient for radiative heat exchange
surf_rad_htc = 4.0;

% - radiative exchange coefficents between internal walls and other
% building constructions
surf_rad_htc_int_wall_glazing_n = surf_rad_htc * int_wall_area * glazing_area_n / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_glazing_e = surf_rad_htc * int_wall_area * glazing_area_e / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_glazing_s = surf_rad_htc * int_wall_area * glazing_area_s / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_glazing_w = surf_rad_htc * int_wall_area * glazing_area_w / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_frame_n = surf_rad_htc * int_wall_area * frame_area_n / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_frame_e = surf_rad_htc * int_wall_area * frame_area_e / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_frame_s = surf_rad_htc * int_wall_area * frame_area_s / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_frame_w = surf_rad_htc * int_wall_area * frame_area_w / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_wall_n = surf_rad_htc * int_wall_area * wall_area_n / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_wall_e = surf_rad_htc * int_wall_area * wall_area_e / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_wall_s = surf_rad_htc * int_wall_area * wall_area_s / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_wall_w = surf_rad_htc * int_wall_area * wall_area_w / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_roof = surf_rad_htc * int_wall_area * roof_area / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_floor = surf_rad_htc * int_wall_area * floor_area / (total_area_constructions - int_wall_area);
surf_rad_htc_int_wall_int_ceiling = surf_rad_htc * int_wall_area * int_ceiling_area / (total_area_constructions - int_wall_area);

% - radiative exchange coefficents between internal ceilings and other
% building constructions
surf_rad_htc_int_ceiling_glazing_n = surf_rad_htc * int_ceiling_area * glazing_area_n / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_glazing_e = surf_rad_htc * int_ceiling_area * glazing_area_e / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_glazing_s = surf_rad_htc * int_ceiling_area * glazing_area_s / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_glazing_w = surf_rad_htc * int_ceiling_area * glazing_area_w / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_frame_n = surf_rad_htc * int_ceiling_area * frame_area_n / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_frame_e = surf_rad_htc * int_ceiling_area * frame_area_e / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_frame_s = surf_rad_htc * int_ceiling_area * frame_area_s / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_frame_w = surf_rad_htc * int_ceiling_area * frame_area_w / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_wall_n = surf_rad_htc * int_ceiling_area * wall_area_n / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_wall_e = surf_rad_htc * int_ceiling_area * wall_area_e / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_wall_s = surf_rad_htc * int_ceiling_area * wall_area_s / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_wall_w = surf_rad_htc * int_ceiling_area * wall_area_w / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_roof = surf_rad_htc * int_ceiling_area * roof_area / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_floor = surf_rad_htc * int_ceiling_area * floor_area / (total_area_constructions - int_ceiling_area);
surf_rad_htc_int_ceiling_int_wall = surf_rad_htc_int_wall_int_ceiling;


% 10. Initialization the left matrix of system of 49 linear equations
left_matrix = zeros(49, 49);

% 11. Definition of the lines of system of linear equations
line_air = 1; % air temperature

line_in_glazing_n = 2; % temperature of inside glazing surface in north direction
line_in_glazing_e = 3; % temperature of inside glazing surface in east direction
line_in_glazing_s = 4; % temperature of inside glazing surface in south direction
line_in_glazing_w = 5; % temperature of inside glazing surface in west direction

line_out_glazing_n = 6; % temperature of outside glazing surface in north direction
line_out_glazing_e = 7; % temperature of outside glazing surface in east direction
line_out_glazing_s = 8; % temperature of outside glazing surface in south direction
line_out_glazing_w = 9; % temperature of outside glazing surface in west direction

line_in_frame_n = 10; % temperature of inside window frame surface in north direction
line_in_frame_e = 11; % temperature of inside window frame surface in east direction
line_in_frame_s = 12; % temperature of inside window frame surface in south direction
line_in_frame_w = 13; % temperature of inside window frame surface in west direction

line_out_frame_n = 14; % temperature of outside window frame surface in north direction
line_out_frame_e = 15; % temperature of outside window frame surface in east direction
line_out_frame_s = 16; % temperature of outside window frame surface in south direction
line_out_frame_w = 17; % temperature of outside window frame surface in west direction

line_wall_n_1 = 18; % temperature of the 1. node of the external wall in north direction
line_wall_e_1 = 19; % temperature of the 1. node of the external wall in east direction
line_wall_s_1 = 20; % temperature of the 1. node of the external wall in south direction
line_wall_w_1 = 21; % temperature of the 1. node of the external wall in west direction
line_roof_1 = 22; % temperature of the 1. node of the roof
line_floor_1 = 23; % temperature of the 1. node of the floor
line_int_wall_1 = 24; % temperature of the 1. node of the internal walls
line_int_ceiling_1 = 25; % temperature of the 1. node of the internal ceiling

line_wall_n_2 = 26; % temperature of the 2. node of the external wall in north direction
line_wall_e_2 = 27; % temperature of the 2. node of the external wall in east direction
line_wall_s_2 = 28; % temperature of the 2. node of the external wall in south direction
line_wall_w_2 = 29; % temperature of the 2. node of the external wall in west direction
line_roof_2 = 30; % temperature of the 2. node of the roof
line_floor_2 = 31; % temperature of the 2. node of the floor
line_int_wall_2 = 32; % temperature of the 2. node of the internal walls
line_int_ceiling_2 = 33; % temperature of the 2. node of the internal ceiling

line_wall_n_3 = 34; % temperature of the 3. node of the external wall in north direction
line_wall_e_3 = 35; % temperature of the 3. node of the external wall in east direction
line_wall_s_3 = 36; % temperature of the 3. node of the external wall in south direction
line_wall_w_3 = 37; % temperature of the 3. node of the external wall in west direction
line_roof_3 = 38; % temperature of the 3. node of the roof
line_floor_3 = 39; % temperature of the 3. node of the floor
line_int_wall_3 = 40; % temperature of the 3. node of the internal walls
line_int_ceiling_3 = 41; % temperature of the 3. node of the internal ceiling

line_wall_n_4 = 42; % temperature of the 3. node of the external wall in north direction
line_wall_e_4 = 43; % temperature of the 3. node of the external wall in east direction
line_wall_s_4 = 44; % temperature of the 3. node of the external wall in south direction
line_wall_w_4 = 45; % temperature of the 3. node of the external wall in west direction
line_roof_4 = 46; % temperature of the 3. node of the roof
line_floor_4 = 47; % temperature of the 3. node of the floor
line_int_wall_4 = 48; % temperature of the 4. node of the internal walls
line_int_ceiling_4 = 49; % temperature of the 4. node of the internal ceiling

% 12. Define the values in left matrix

% - air temperature equation
left_matrix(line_air, line_air) = building_height * floor_area * 1006 * 1.185 + ...
    surf_htc_in * total_area_constructions * time_step + (thermal_bridges + wall_against_unheated_u_value * wall_against_unheated_area) * time_step + ...
    (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step;

left_matrix(line_air, line_in_glazing_n) = - surf_htc_in * time_step * glazing_area_n;
left_matrix(line_air, line_in_glazing_e) = - surf_htc_in * time_step * glazing_area_e;
left_matrix(line_air, line_in_glazing_s) = - surf_htc_in * time_step * glazing_area_s;
left_matrix(line_air, line_in_glazing_w) = - surf_htc_in * time_step * glazing_area_w;
left_matrix(line_air, line_in_frame_n) = - surf_htc_in * time_step * frame_area_n;
left_matrix(line_air, line_in_frame_e) = - surf_htc_in * time_step * frame_area_e;
left_matrix(line_air, line_in_frame_s) = - surf_htc_in * time_step * frame_area_s;
left_matrix(line_air, line_in_frame_w) = - surf_htc_in * time_step * frame_area_w;
left_matrix(line_air, line_wall_n_1) = - surf_htc_in * time_step * wall_area_n;
left_matrix(line_air, line_wall_e_1) = - surf_htc_in * time_step * wall_area_e;
left_matrix(line_air, line_wall_s_1) = - surf_htc_in * time_step * wall_area_s;
left_matrix(line_air, line_wall_w_1) = - surf_htc_in * time_step * wall_area_w;
left_matrix(line_air, line_roof_1) = - surf_htc_in * time_step * roof_area;
left_matrix(line_air, line_floor_1) = - surf_htc_in * time_step * floor_area;
left_matrix(line_air, line_int_wall_1) = - surf_htc_in * time_step * int_wall_area;
left_matrix(line_air, line_int_ceiling_1) = - surf_htc_in * time_step * int_ceiling_area;


% - temperature of the inside node of the north glazing
left_matrix(line_in_glazing_n, line_air) = left_matrix(line_air, line_in_glazing_n);
left_matrix(line_in_glazing_n, line_out_glazing_n) = -glazing_area_n * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out);
left_matrix(line_in_glazing_n, line_int_wall_1) = -surf_rad_htc_int_wall_glazing_n * time_step;
left_matrix(line_in_glazing_n, line_int_ceiling_1) = -surf_rad_htc_int_ceiling_glazing_n * time_step;

left_matrix(line_in_glazing_n, line_in_glazing_n) = ...
    - left_matrix(line_in_glazing_n, line_air) ...
    - left_matrix(line_in_glazing_n, line_out_glazing_n) ... 
    - left_matrix(line_in_glazing_n, line_int_wall_1) ...
    - left_matrix(line_in_glazing_n, line_int_ceiling_1);


% - temperature of the inside node of the east glazing
left_matrix(line_in_glazing_e, line_air) = left_matrix(line_air, line_in_glazing_e);
left_matrix(line_in_glazing_e, line_out_glazing_e) = -glazing_area_e * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out);
left_matrix(line_in_glazing_e, line_int_wall_1) = -surf_rad_htc_int_wall_glazing_e * time_step;
left_matrix(line_in_glazing_e, line_int_ceiling_1) = -surf_rad_htc_int_ceiling_glazing_e * time_step;

left_matrix(line_in_glazing_e, line_in_glazing_e) = ...
    - left_matrix(line_in_glazing_e, line_air) ...
    - left_matrix(line_in_glazing_e, line_out_glazing_e) ... 
    - left_matrix(line_in_glazing_e, line_int_wall_1) ...
    - left_matrix(line_in_glazing_e, line_int_ceiling_1);


% - temperature of the inside node of the south glazing
left_matrix(line_in_glazing_s, line_air) = left_matrix(line_air, line_in_glazing_s);
left_matrix(line_in_glazing_s, line_out_glazing_s) = -glazing_area_s * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out);
left_matrix(line_in_glazing_s, line_int_wall_1) = -surf_rad_htc_int_wall_glazing_s * time_step;
left_matrix(line_in_glazing_s, line_int_ceiling_1) = -surf_rad_htc_int_ceiling_glazing_s * time_step;

left_matrix(line_in_glazing_s, line_in_glazing_s) = ...
    - left_matrix(line_in_glazing_s, line_air) ...
    - left_matrix(line_in_glazing_s, line_out_glazing_s) ... 
    - left_matrix(line_in_glazing_s, line_int_wall_1) ...
    - left_matrix(line_in_glazing_s, line_int_ceiling_1);


% - temperature of the inside node of the west glazing
left_matrix(line_in_glazing_w, line_air) = left_matrix(line_air, line_in_glazing_w);
left_matrix(line_in_glazing_w, line_out_glazing_w) = -glazing_area_w * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out);
left_matrix(line_in_glazing_w, line_int_wall_1) = -surf_rad_htc_int_wall_glazing_w * time_step;
left_matrix(line_in_glazing_w, line_int_ceiling_1) = -surf_rad_htc_int_ceiling_glazing_w * time_step;

left_matrix(line_in_glazing_w, line_in_glazing_w) = ...
    - left_matrix(line_in_glazing_w, line_air) ...
    - left_matrix(line_in_glazing_w, line_out_glazing_w) ... 
    - left_matrix(line_in_glazing_w, line_int_wall_1) ...
    - left_matrix(line_in_glazing_w, line_int_ceiling_1);


% - temperature of the outside node of the north glazing
left_matrix(line_out_glazing_n, line_in_glazing_n) = left_matrix(line_in_glazing_n, line_out_glazing_n);
left_matrix(line_out_glazing_n, line_out_glazing_n) = -left_matrix(line_out_glazing_n, line_in_glazing_n) + glazing_area_n * surf_htc_out * time_step;


% - temperature of the outside node of the east glazing
left_matrix(line_out_glazing_e, line_in_glazing_e) = left_matrix(line_in_glazing_e, line_out_glazing_e);
left_matrix(line_out_glazing_e, line_out_glazing_e) = -left_matrix(line_out_glazing_e, line_in_glazing_e) + glazing_area_e * surf_htc_out * time_step;


% - temperature of the outside node of the south glazing
left_matrix(line_out_glazing_s, line_in_glazing_s) = left_matrix(line_in_glazing_s, line_out_glazing_s);
left_matrix(line_out_glazing_s, line_out_glazing_s) = -left_matrix(line_out_glazing_s, line_in_glazing_s) + glazing_area_s * surf_htc_out * time_step;


% - temperature of the outside node of the west glazing
left_matrix(line_out_glazing_w, line_in_glazing_w) = left_matrix(line_in_glazing_w, line_out_glazing_w);
left_matrix(line_out_glazing_w, line_out_glazing_w) = -left_matrix(line_out_glazing_w, line_in_glazing_w) + glazing_area_w * surf_htc_out * time_step;


% - temperature of the inside node of the north window frame
left_matrix(line_in_frame_n, line_air) = left_matrix(line_air, line_in_frame_n);
left_matrix(line_in_frame_n, line_out_frame_n) = -frame_area_n * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out);
left_matrix(line_in_frame_n, line_int_wall_1) = -surf_rad_htc_int_wall_frame_n * time_step;
left_matrix(line_in_frame_n, line_int_ceiling_1) = -surf_rad_htc_int_ceiling_frame_n * time_step;

left_matrix(line_in_frame_n, line_in_frame_n) = ...
    - left_matrix(line_in_frame_n, line_air) ...
    - left_matrix(line_in_frame_n, line_out_frame_n) ... 
    - left_matrix(line_in_frame_n, line_int_wall_1) ...
    - left_matrix(line_in_frame_n, line_int_ceiling_1);


% - temperature of the inside node of the east window frame
left_matrix(line_in_frame_e, line_air) = left_matrix(line_air, line_in_frame_e);
left_matrix(line_in_frame_e, line_out_frame_e) = -frame_area_e * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out);
left_matrix(line_in_frame_e, line_int_wall_1) = -surf_rad_htc_int_wall_frame_e * time_step;
left_matrix(line_in_frame_e, line_int_ceiling_1) = -surf_rad_htc_int_ceiling_frame_e * time_step;

left_matrix(line_in_frame_e, line_in_frame_e) = ...
    - left_matrix(line_in_frame_e, line_air) ...
    - left_matrix(line_in_frame_e, line_out_frame_e) ... 
    - left_matrix(line_in_frame_e, line_int_wall_1) ...
    - left_matrix(line_in_frame_e, line_int_ceiling_1);


% - temperature of the inside node of the south window frame
left_matrix(line_in_frame_s, line_air) = left_matrix(line_air, line_in_frame_s);
left_matrix(line_in_frame_s, line_out_frame_s) = -frame_area_s * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out);
left_matrix(line_in_frame_s, line_int_wall_1) = -surf_rad_htc_int_wall_frame_s * time_step;
left_matrix(line_in_frame_s, line_int_ceiling_1) = -surf_rad_htc_int_ceiling_frame_s * time_step;

left_matrix(line_in_frame_s, line_in_frame_s) = ...
    - left_matrix(line_in_frame_s, line_air) ...
    - left_matrix(line_in_frame_s, line_out_frame_s) ... 
    - left_matrix(line_in_frame_s, line_int_wall_1) ...
    - left_matrix(line_in_frame_s, line_int_ceiling_1);


% - temperature of the inside node of the west window frame
left_matrix(line_in_frame_w, line_air) = left_matrix(line_air, line_in_frame_w);
left_matrix(line_in_frame_w, line_out_frame_w) = -frame_area_w * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out);
left_matrix(line_in_frame_w, line_int_wall_1) = -surf_rad_htc_int_wall_frame_w * time_step;
left_matrix(line_in_frame_w, line_int_ceiling_1) = -surf_rad_htc_int_ceiling_frame_w * time_step;

left_matrix(line_in_frame_w, line_in_frame_w) = ...
    - left_matrix(line_in_frame_w, line_air) ...
    - left_matrix(line_in_frame_w, line_out_frame_w) ... 
    - left_matrix(line_in_frame_w, line_int_wall_1) ...
    - left_matrix(line_in_frame_w, line_int_ceiling_1);


% - temperature of the outside node of the north window frame
left_matrix(line_out_frame_n, line_in_frame_n) = left_matrix(line_in_frame_n, line_out_frame_n);
left_matrix(line_out_frame_n, line_out_frame_n) = -left_matrix(line_out_frame_n, line_in_frame_n) + frame_area_n * surf_htc_out * time_step;


% - temperature of the outside node of the east window frame
left_matrix(line_out_frame_e, line_in_frame_e) = left_matrix(line_in_frame_e, line_out_frame_e);
left_matrix(line_out_frame_e, line_out_frame_e) = -left_matrix(line_out_frame_e, line_in_frame_e) + frame_area_e * surf_htc_out * time_step;


% - temperature of the outside node of the south window frame
left_matrix(line_out_frame_s, line_in_frame_s) = left_matrix(line_in_frame_s, line_out_frame_s);
left_matrix(line_out_frame_s, line_out_frame_s) = -left_matrix(line_out_frame_s, line_in_frame_s) + frame_area_s * surf_htc_out * time_step;


% - temperature of the outside node of the west window frame
left_matrix(line_out_frame_w, line_in_frame_w) = left_matrix(line_in_frame_w, line_out_frame_w);
left_matrix(line_out_frame_w, line_out_frame_w) = -left_matrix(line_out_frame_w, line_in_frame_w) + frame_area_w * surf_htc_out * time_step;


% - temperature of the 1. node of the north wall
left_matrix(line_wall_n_1, line_air) = left_matrix(line_air, line_wall_n_1);
left_matrix(line_wall_n_1, line_wall_n_2) = - wall_area_n * time_step *  wall_inside_lyamda / wall_inside_thickness / 0.75;
left_matrix(line_wall_n_1, line_int_wall_1) = - surf_rad_htc_int_wall_wall_n * time_step;
left_matrix(line_wall_n_1, line_int_ceiling_1) = - surf_rad_htc_int_ceiling_wall_n * time_step;

left_matrix(line_wall_n_1, line_wall_n_1) = wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5 ...
    - left_matrix(line_wall_n_1, line_air) ...
    - left_matrix(line_wall_n_1, line_wall_n_2) ...
    - left_matrix(line_wall_n_1, line_int_wall_1) ...
    - left_matrix(line_wall_n_1, line_int_ceiling_1);


% - temperature of the 1. node of the east wall
left_matrix(line_wall_e_1, line_air) = left_matrix(line_air, line_wall_e_1);
left_matrix(line_wall_e_1, line_wall_e_2) = - wall_area_e * time_step * wall_inside_lyamda / wall_inside_thickness / 0.75;
left_matrix(line_wall_e_1, line_int_wall_1) = - surf_rad_htc_int_wall_wall_e * time_step;
left_matrix(line_wall_e_1, line_int_ceiling_1) = - surf_rad_htc_int_ceiling_wall_e * time_step;

left_matrix(line_wall_e_1, line_wall_e_1) = wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5 ...
    - left_matrix(line_wall_e_1, line_air) ...
    - left_matrix(line_wall_e_1, line_wall_e_2) ...
    - left_matrix(line_wall_e_1, line_int_wall_1) ...
    - left_matrix(line_wall_e_1, line_int_ceiling_1);


% - temperature of the 1. node of the south wall
left_matrix(line_wall_s_1, line_air) = left_matrix(line_air, line_wall_s_1);
left_matrix(line_wall_s_1, line_wall_s_2) = - wall_area_s * time_step * wall_inside_lyamda / wall_inside_thickness / 0.75;
left_matrix(line_wall_s_1, line_int_wall_1) = - surf_rad_htc_int_wall_wall_s * time_step;
left_matrix(line_wall_s_1, line_int_ceiling_1) = - surf_rad_htc_int_ceiling_wall_s * time_step;

left_matrix(line_wall_s_1, line_wall_s_1) = wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5 ...
    - left_matrix(line_wall_s_1, line_air) ...
    - left_matrix(line_wall_s_1, line_wall_s_2) ...
    - left_matrix(line_wall_s_1, line_int_wall_1) ...
    - left_matrix(line_wall_s_1, line_int_ceiling_1);


% - temperature of the 1. node of the west wall
left_matrix(line_wall_w_1, line_air) = left_matrix(line_air, line_wall_w_1);
left_matrix(line_wall_w_1, line_wall_w_2) = - wall_area_w * time_step * wall_inside_lyamda / wall_inside_thickness / 0.75;
left_matrix(line_wall_w_1, line_int_wall_1) = - surf_rad_htc_int_wall_wall_w * time_step;
left_matrix(line_wall_w_1, line_int_ceiling_1) = - surf_rad_htc_int_ceiling_wall_w * time_step;

left_matrix(line_wall_w_1, line_wall_w_1) = wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5 ...
    - left_matrix(line_wall_w_1, line_air) ...
    - left_matrix(line_wall_w_1, line_wall_w_2) ...
    - left_matrix(line_wall_w_1, line_int_wall_1) ...
    - left_matrix(line_wall_w_1, line_int_ceiling_1);


% - temperature of the 1. node of the roof
left_matrix(line_roof_1, line_air) = left_matrix(line_air, line_roof_1);
left_matrix(line_roof_1, line_roof_2) = - roof_area * time_step * roof_inside_lyamda / roof_inside_thickness / 0.75;
left_matrix(line_roof_1, line_int_wall_1) = - surf_rad_htc_int_wall_roof * time_step;
left_matrix(line_roof_1, line_int_ceiling_1) = - surf_rad_htc_int_ceiling_roof * time_step;

left_matrix(line_roof_1, line_roof_1) = roof_area * roof_inside_capacity_density * roof_inside_thickness * 0.5 ...
    - left_matrix(line_roof_1, line_air) ...
    - left_matrix(line_roof_1, line_roof_2) ...
    - left_matrix(line_roof_1, line_int_wall_1) ...
    - left_matrix(line_roof_1, line_int_ceiling_1);


% - temperature of the 1. node of the floor
left_matrix(line_floor_1, line_air) = left_matrix(line_air, line_floor_1);
left_matrix(line_floor_1, line_floor_2) = - floor_area * time_step * floor_inside_lyamda / floor_inside_thickness / 0.75;
left_matrix(line_floor_1, line_int_wall_1) = - surf_rad_htc_int_wall_floor * time_step;
left_matrix(line_floor_1, line_int_ceiling_1) = - surf_rad_htc_int_ceiling_floor * time_step;

left_matrix(line_floor_1, line_floor_1) = floor_area * floor_inside_capacity_density * floor_inside_thickness * 0.5 ... 
    - left_matrix(line_floor_1, line_air) ...
    - left_matrix(line_floor_1, line_floor_2) ...
    - left_matrix(line_floor_1, line_int_wall_1) ...
    - left_matrix(line_floor_1, line_int_ceiling_1);


% - temperature of the 1. node of the internal walls
left_matrix(line_int_wall_1, line_air) = left_matrix(line_air, line_int_wall_1);
left_matrix(line_int_wall_1, line_int_wall_2) = - int_wall_area * time_step * int_wall_lyamda / int_wall_thickness / (0.125 + 0.0625);
left_matrix(line_int_wall_1, line_in_glazing_n) = left_matrix(line_in_glazing_n, line_int_wall_1);
left_matrix(line_int_wall_1, line_in_glazing_e) = left_matrix(line_in_glazing_e, line_int_wall_1);
left_matrix(line_int_wall_1, line_in_glazing_s) = left_matrix(line_in_glazing_s, line_int_wall_1);
left_matrix(line_int_wall_1, line_in_glazing_w) = left_matrix(line_in_glazing_w, line_int_wall_1);
left_matrix(line_int_wall_1, line_in_frame_n) = left_matrix(line_in_frame_n, line_int_wall_1);
left_matrix(line_int_wall_1, line_in_frame_e) = left_matrix(line_in_frame_e, line_int_wall_1);
left_matrix(line_int_wall_1, line_in_frame_s) = left_matrix(line_in_frame_s, line_int_wall_1);
left_matrix(line_int_wall_1, line_in_frame_w) = left_matrix(line_in_frame_w, line_int_wall_1);
left_matrix(line_int_wall_1, line_wall_n_1) = left_matrix(line_wall_n_1, line_int_wall_1);
left_matrix(line_int_wall_1, line_wall_e_1) = left_matrix(line_wall_e_1, line_int_wall_1);
left_matrix(line_int_wall_1, line_wall_s_1) = left_matrix(line_wall_s_1, line_int_wall_1);
left_matrix(line_int_wall_1, line_wall_w_1) = left_matrix(line_wall_w_1, line_int_wall_1);
left_matrix(line_int_wall_1, line_roof_1) = left_matrix(line_roof_1, line_int_wall_1);
left_matrix(line_int_wall_1, line_floor_1) = left_matrix(line_floor_1, line_int_wall_1);
left_matrix(line_int_wall_1, line_int_ceiling_1) = - surf_rad_htc_int_wall_int_ceiling * time_step;

left_matrix(line_int_wall_1, line_int_wall_1) = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 ...
    - left_matrix(line_int_wall_1, line_air) ...
    - left_matrix(line_int_wall_1, line_int_wall_2) ...
    - left_matrix(line_int_wall_1, line_in_glazing_n) ...
    - left_matrix(line_int_wall_1, line_in_glazing_e) ...
    - left_matrix(line_int_wall_1, line_in_glazing_s) ...
    - left_matrix(line_int_wall_1, line_in_glazing_w) ...
    - left_matrix(line_int_wall_1, line_in_frame_n) ...
    - left_matrix(line_int_wall_1, line_in_frame_e) ...
    - left_matrix(line_int_wall_1, line_in_frame_s) ...
    - left_matrix(line_int_wall_1, line_in_frame_w) ...
    - left_matrix(line_int_wall_1, line_wall_n_1) ...
    - left_matrix(line_int_wall_1, line_wall_e_1) ...
    - left_matrix(line_int_wall_1, line_wall_s_1) ...
    - left_matrix(line_int_wall_1, line_wall_w_1) ...
    - left_matrix(line_int_wall_1, line_roof_1) ...
    - left_matrix(line_int_wall_1, line_floor_1) ...
    - left_matrix(line_int_wall_1, line_int_ceiling_1);


% - temperature of the 1. node of the internal ceiling
left_matrix(line_int_ceiling_1, line_air) = left_matrix(line_air, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_int_ceiling_2) = - int_ceiling_area * time_step * int_ceiling_lyamda / int_ceiling_thickness / (0.125 + 0.0625);
left_matrix(line_int_ceiling_1, line_in_glazing_n) = left_matrix(line_in_glazing_n, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_in_glazing_e) = left_matrix(line_in_glazing_e, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_in_glazing_s) = left_matrix(line_in_glazing_s, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_in_glazing_w) = left_matrix(line_in_glazing_w, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_in_frame_n) = left_matrix(line_in_frame_n, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_in_frame_e) = left_matrix(line_in_frame_e, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_in_frame_s) = left_matrix(line_in_frame_s, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_in_frame_w) = left_matrix(line_in_frame_w, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_wall_n_1) = left_matrix(line_wall_n_1, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_wall_e_1) = left_matrix(line_wall_e_1, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_wall_s_1) = left_matrix(line_wall_s_1, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_wall_w_1) = left_matrix(line_wall_w_1, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_roof_1) = left_matrix(line_roof_1, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_floor_1) = left_matrix(line_floor_1, line_int_ceiling_1);
left_matrix(line_int_ceiling_1, line_int_wall_1) = left_matrix(line_int_wall_1, line_int_ceiling_1);

left_matrix(line_int_ceiling_1, line_int_ceiling_1) = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 ...
    - left_matrix(line_int_ceiling_1, line_air) ...
    - left_matrix(line_int_ceiling_1, line_int_ceiling_2) ...
    - left_matrix(line_int_ceiling_1, line_in_glazing_n) ...
    - left_matrix(line_int_ceiling_1, line_in_glazing_e) ...
    - left_matrix(line_int_ceiling_1, line_in_glazing_s) ...
    - left_matrix(line_int_ceiling_1, line_in_glazing_w) ...
    - left_matrix(line_int_ceiling_1, line_in_frame_n) ...
    - left_matrix(line_int_ceiling_1, line_in_frame_e) ...
    - left_matrix(line_int_ceiling_1, line_in_frame_s) ...
    - left_matrix(line_int_ceiling_1, line_in_frame_w) ...    
    - left_matrix(line_int_ceiling_1, line_wall_n_1) ...
    - left_matrix(line_int_ceiling_1, line_wall_e_1) ...
    - left_matrix(line_int_ceiling_1, line_wall_s_1) ...
    - left_matrix(line_int_ceiling_1, line_wall_w_1) ...
    - left_matrix(line_int_ceiling_1, line_roof_1) ...
    - left_matrix(line_int_ceiling_1, line_floor_1) ...
    - left_matrix(line_int_ceiling_1, line_int_wall_1);


% - temperature of the 2. node of the north wall
left_matrix(line_wall_n_2, line_wall_n_1) = left_matrix(line_wall_n_1, line_wall_n_2);
left_matrix(line_wall_n_2, line_wall_n_3) = - wall_area_n * time_step *  1 / (1 / wall_inside_lyamda * wall_inside_thickness * 0.25 + 1 / wall_outside_lyamda * wall_outside_thickness * 0.25);
left_matrix(line_wall_n_2, line_wall_n_2) = wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5...
    - left_matrix(line_wall_n_2, line_wall_n_1) ...
    - left_matrix(line_wall_n_2, line_wall_n_3);

% - temperature of the 2. node of the east wall
left_matrix(line_wall_e_2, line_wall_e_1) = left_matrix(line_wall_e_1, line_wall_e_2);
left_matrix(line_wall_e_2, line_wall_e_3) = - wall_area_e * time_step *  1 / (1 / wall_inside_lyamda * wall_inside_thickness * 0.25 + 1 / wall_outside_lyamda * wall_outside_thickness * 0.25);
left_matrix(line_wall_e_2, line_wall_e_2) = wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5...
    - left_matrix(line_wall_e_2, line_wall_e_1) ...
    - left_matrix(line_wall_e_2, line_wall_e_3);

% - temperature of the 2. node of the south wall
left_matrix(line_wall_s_2, line_wall_s_1) = left_matrix(line_wall_s_1, line_wall_s_2);
left_matrix(line_wall_s_2, line_wall_s_3) = - wall_area_s * time_step *  1 / (1 / wall_inside_lyamda * wall_inside_thickness * 0.25 + 1 / wall_outside_lyamda * wall_outside_thickness * 0.25);
left_matrix(line_wall_s_2, line_wall_s_2) = wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5...
    - left_matrix(line_wall_s_2, line_wall_s_1) ...
    - left_matrix(line_wall_s_2, line_wall_s_3);

% - temperature of the 2. node of the west wall
left_matrix(line_wall_w_2, line_wall_w_1) = left_matrix(line_wall_w_1, line_wall_w_2);
left_matrix(line_wall_w_2, line_wall_w_3) = - wall_area_w * time_step *  1 / (1 / wall_inside_lyamda * wall_inside_thickness * 0.25 + 1 / wall_outside_lyamda * wall_outside_thickness * 0.25);
left_matrix(line_wall_w_2, line_wall_w_2) = wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5...
    - left_matrix(line_wall_w_2, line_wall_w_1) ...
    - left_matrix(line_wall_w_2, line_wall_w_3);

% - temperature of the 2. node of the roof
left_matrix(line_roof_2, line_roof_1) = left_matrix(line_roof_1, line_roof_2);
left_matrix(line_roof_2, line_roof_3) = - roof_area * time_step *  1 / (1 / roof_inside_lyamda * roof_inside_thickness * 0.25 + 1 / roof_outside_lyamda * roof_outside_thickness * 0.25);
left_matrix(line_roof_2, line_roof_2) = roof_area * roof_inside_capacity_density * roof_inside_thickness * 0.5...
    - left_matrix(line_roof_2, line_roof_1) ...
    - left_matrix(line_roof_2, line_roof_3);

% - temperature of the 2. node of the floor
left_matrix(line_floor_2, line_floor_1) = left_matrix(line_floor_1, line_floor_2);
left_matrix(line_floor_2, line_floor_3) = - floor_area * time_step *  1 / (1 / floor_inside_lyamda * floor_inside_thickness * 0.25 + 1 / floor_outside_lyamda * floor_outside_thickness * 0.25);
left_matrix(line_floor_2, line_floor_2) = floor_area * floor_inside_capacity_density * floor_inside_thickness * 0.5...
    - left_matrix(line_floor_2, line_floor_1) ...
    - left_matrix(line_floor_2, line_floor_3);

% - temperature of the 2. node of the internal walls
left_matrix(line_int_wall_2, line_int_wall_1) = left_matrix(line_int_wall_1, line_int_wall_2);
left_matrix(line_int_wall_2, line_int_wall_3) = - int_wall_area * time_step *  1 / (1 / int_wall_lyamda * int_wall_thickness * 0.125);
left_matrix(line_int_wall_2, line_int_wall_2) = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 ...
    - left_matrix(line_int_wall_2, line_int_wall_1) ...
    - left_matrix(line_int_wall_2, line_int_wall_3);

% - temperature of the 2. node of the internal walls
left_matrix(line_int_ceiling_2, line_int_ceiling_1) = left_matrix(line_int_ceiling_1, line_int_ceiling_2);
left_matrix(line_int_ceiling_2, line_int_ceiling_3) = - int_ceiling_area * time_step *  1 / (1 / int_ceiling_lyamda * int_ceiling_thickness * 0.125);
left_matrix(line_int_ceiling_2, line_int_ceiling_2) = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 ...
    - left_matrix(line_int_ceiling_2, line_int_ceiling_1) ...
    - left_matrix(line_int_ceiling_2, line_int_ceiling_3);


% - temperature of the 3. node of the north wall
left_matrix(line_wall_n_3, line_wall_n_2) = left_matrix(line_wall_n_2, line_wall_n_3);
left_matrix(line_wall_n_3, line_wall_n_4) = - wall_area_n * time_step *  wall_outside_lyamda / wall_outside_thickness / 0.75;
left_matrix(line_wall_n_3, line_wall_n_3) = wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5...
    - left_matrix(line_wall_n_3, line_wall_n_2) ...
    - left_matrix(line_wall_n_3, line_wall_n_4);

% - temperature of the 3. node of the east wall
left_matrix(line_wall_e_3, line_wall_e_2) = left_matrix(line_wall_e_2, line_wall_e_3);
left_matrix(line_wall_e_3, line_wall_e_4) = - wall_area_e * time_step *  wall_outside_lyamda / wall_outside_thickness / 0.75;
left_matrix(line_wall_e_3, line_wall_e_3) = wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5...
    - left_matrix(line_wall_e_3, line_wall_e_2) ...
    - left_matrix(line_wall_e_3, line_wall_e_4);

% - temperature of the 3. node of the south wall
left_matrix(line_wall_s_3, line_wall_s_2) = left_matrix(line_wall_s_2, line_wall_s_3);
left_matrix(line_wall_s_3, line_wall_s_4) = - wall_area_s * time_step *  wall_outside_lyamda / wall_outside_thickness / 0.75;
left_matrix(line_wall_s_3, line_wall_s_3) = wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5...
    - left_matrix(line_wall_s_3, line_wall_s_2) ...
    - left_matrix(line_wall_s_3, line_wall_s_4);

% - temperature of the 3. node of the west wall
left_matrix(line_wall_w_3, line_wall_w_2) = left_matrix(line_wall_w_2, line_wall_w_3);
left_matrix(line_wall_w_3, line_wall_w_4) = - wall_area_w * time_step *  wall_outside_lyamda / wall_outside_thickness / 0.75;
left_matrix(line_wall_w_3, line_wall_w_3) = wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5...
    - left_matrix(line_wall_w_3, line_wall_w_2) ...
    - left_matrix(line_wall_w_3, line_wall_w_4);

% - temperature of the 3. node of the roof
left_matrix(line_roof_3, line_roof_2) = left_matrix(line_roof_2, line_roof_3);
left_matrix(line_roof_3, line_roof_4) = - roof_area * time_step * roof_outside_lyamda / roof_outside_thickness / 0.75;
left_matrix(line_roof_3, line_roof_3) = roof_area * roof_outside_capacity_density * roof_outside_thickness * 0.5...
    - left_matrix(line_roof_3, line_roof_2) ...
    - left_matrix(line_roof_3, line_roof_4);

% - temperature of the 3. node of the floor
left_matrix(line_floor_3, line_floor_2) = left_matrix(line_floor_2, line_floor_3);
left_matrix(line_floor_3, line_floor_4) = - floor_area * time_step * floor_outside_lyamda / floor_outside_thickness / 0.75;
left_matrix(line_floor_3, line_floor_3) = floor_area * floor_outside_capacity_density * floor_outside_thickness * 0.5...
    - left_matrix(line_floor_3, line_floor_2) ...
    - left_matrix(line_floor_3, line_floor_4);

% - temperature of the 3. node of the internal walls
left_matrix(line_int_wall_3, line_int_wall_2) = left_matrix(line_int_wall_2, line_int_wall_3);
left_matrix(line_int_wall_3, line_int_wall_4) = - int_wall_area * time_step *  1 / (1 / int_wall_lyamda * int_wall_thickness * 0.125);
left_matrix(line_int_wall_3, line_int_wall_3) = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 ...
    - left_matrix(line_int_wall_3, line_int_wall_2) ...
    - left_matrix(line_int_wall_3, line_int_wall_4);

% - temperature of the 3. node of the internal ceiling
left_matrix(line_int_ceiling_3, line_int_ceiling_2) = left_matrix(line_int_ceiling_2, line_int_ceiling_3);
left_matrix(line_int_ceiling_3, line_int_ceiling_4) = - int_ceiling_area * time_step *  1 / (1 / int_ceiling_lyamda * int_ceiling_thickness * 0.125);
left_matrix(line_int_ceiling_3, line_int_ceiling_3) = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 ...
    - left_matrix(line_int_ceiling_3, line_int_ceiling_2) ...
    - left_matrix(line_int_ceiling_3, line_int_ceiling_4);


% - temperature of the 4. node of the north wall
left_matrix(line_wall_n_4, line_wall_n_3) = left_matrix(line_wall_n_3, line_wall_n_4);
left_matrix(line_wall_n_4, line_wall_n_4) = wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5...
    + wall_area_n * surf_htc_out * time_step - left_matrix(line_wall_n_4, line_wall_n_3);

% - temperature of the 4. node of the east wall
left_matrix(line_wall_e_4, line_wall_e_3) = left_matrix(line_wall_e_3, line_wall_e_4);
left_matrix(line_wall_e_4, line_wall_e_4) = wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5...
    + wall_area_e *surf_htc_out * time_step - left_matrix(line_wall_e_4, line_wall_e_3);

% - temperature of the 4. node of the south wall
left_matrix(line_wall_s_4, line_wall_s_3) = left_matrix(line_wall_s_3, line_wall_s_4);
left_matrix(line_wall_s_4, line_wall_s_4) = wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5...
    + wall_area_s *surf_htc_out * time_step - left_matrix(line_wall_s_4, line_wall_s_3);

% - temperature of the 4. node of the west wall
left_matrix(line_wall_w_4, line_wall_w_3) = left_matrix(line_wall_w_3, line_wall_w_4);
left_matrix(line_wall_w_4, line_wall_w_4) = wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5...
    + wall_area_w * surf_htc_out * time_step - left_matrix(line_wall_w_4, line_wall_w_3);

% - temperature of the 4. node of the roof
left_matrix(line_roof_4, line_roof_3) = left_matrix(line_roof_3, line_roof_4);
left_matrix(line_roof_4, line_roof_4) = roof_area * roof_outside_capacity_density * roof_outside_thickness * 0.5...
    + roof_area * surf_htc_out * time_step - left_matrix(line_roof_4, line_roof_3);


% - temperature of the 4. node of the floor
left_matrix(line_floor_4, line_floor_3) = left_matrix(line_floor_3, line_floor_4);
left_matrix(line_floor_4, line_floor_4) = floor_area * floor_outside_capacity_density * floor_outside_thickness * 0.5...
    + floor_area * surf_htc_out * time_step - left_matrix(line_floor_4, line_floor_3);


% - temperature of the 4. node of the internal walls
left_matrix(line_int_wall_4, line_int_wall_3) = left_matrix(line_int_wall_3, line_int_wall_4);
left_matrix(line_int_wall_4, line_int_wall_4) = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 ...
    - left_matrix(line_int_wall_4, line_int_wall_3);

% - temperature of the 4. node of the internal ceiling
left_matrix(line_int_ceiling_4, line_int_ceiling_3) = left_matrix(line_int_ceiling_3, line_int_ceiling_4);
left_matrix(line_int_ceiling_4, line_int_ceiling_4) = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 ...
    - left_matrix(line_int_ceiling_4, line_int_ceiling_3);

% 13. Calculate inverse matrix
inverse_matrix = inv(left_matrix);

% 14. Get the amount of hours in weather file
weather_file_size = size(ambient_temp);

% 15. Declare initial and resulting temperature variables
initial_temperatures = 20.0 * ones(49,1);
output_temperatures = zeros(8760, 49);
output_heating_power = zeros(8760, 1);
output_cooling_power = zeros(8760, 1);
output_lighting_electricity = zeros(8760, 1);
output_equipment_electricity = zeros(8760, 1);

% 16. Run simulation
hour_counter = 1;
for day=1:weather_file_size(1)/24
    hour = 1;
    if day == 1 && hour == 1
        hour = hour + 1;
        hour_counter = hour_counter + 1;
    end
    while hour <= 24      
        for internal_time_step = 1:3600/time_step
            right_matrix = zeros(49, 1);
            
            % - interpolation of weather data
            interpolated_amb_temp = ambient_temp(hour_counter - 1) + internal_time_step * time_step / 3600 * (ambient_temp(hour_counter) - ambient_temp(hour_counter - 1));
            interpolated_sun_flux_n = sun_flux_north(hour_counter - 1) + internal_time_step * time_step / 3600 * (sun_flux_north(hour_counter) - sun_flux_north(hour_counter - 1));
            interpolated_sun_flux_e = sun_flux_east(hour_counter - 1) + internal_time_step * time_step / 3600 * (sun_flux_east(hour_counter) - sun_flux_east(hour_counter - 1));
            interpolated_sun_flux_s = sun_flux_south(hour_counter - 1) + internal_time_step * time_step / 3600 * (sun_flux_south(hour_counter) - sun_flux_south(hour_counter - 1));
            interpolated_sun_flux_w = sun_flux_west(hour_counter - 1) + internal_time_step * time_step / 3600 * (sun_flux_west(hour_counter) - sun_flux_west(hour_counter - 1));
            interpolated_sun_flux_r = sun_flux_roof(hour_counter - 1) + internal_time_step * time_step / 3600 * (sun_flux_roof(hour_counter) - sun_flux_roof(hour_counter - 1));
            interpolated_diff_rad = diff_radiation(hour_counter - 1) + internal_time_step * time_step / 3600 * (diff_radiation(hour_counter) - diff_radiation(hour_counter - 1));
            interpolated_global_rad = global_radiation(hour_counter - 1) + internal_time_step * time_step / 3600 * (global_radiation(hour_counter) - global_radiation(hour_counter - 1));            
            interpolated_shading_flux = (0.5 * interpolated_diff_rad + 0.2 * 0.5 * interpolated_global_rad);
            interpolated_ground_temp = 15 - 5 * cosd((hour_counter - 31 * 2 * 24) * 360 / 8760);            
            interpolated_unheated_temp = 18 - 3 * cosd((hour_counter - 31 * 2 * 24) * 360 / 8760);    

            % - calculation of shading
            shading_value_shaded_windows_north = 1.0;
            shading_value_shaded_windows_east = 1.0;
            shading_value_shaded_windows_south = 1.0;
            shading_value_shaded_windows_west = 1.0;
            
            if initial_temperatures(line_air) > 23.0
                if interpolated_shading_flux > 200.0
                    shading_value_shaded_windows_north = shading_g_value_reduction_factor;
                    shading_value_shaded_windows_east = shading_g_value_reduction_factor;
                    shading_value_shaded_windows_south = shading_g_value_reduction_factor;
                    shading_value_shaded_windows_west = shading_g_value_reduction_factor;
                end
            end
            
            shading_value_unshaded_windows_north = 1.0;
            shading_value_unshaded_windows_east = 1.0;
            shading_value_unshaded_windows_south = 1.0;
            shading_value_unshaded_windows_west = 1.0;
            
            if initial_temperatures(line_air) > 23.0
                if interpolated_sun_flux_n > 200.0
                    shading_value_unshaded_windows_north = shading_g_value_reduction_factor;
                end
                if interpolated_sun_flux_e > 200.0
                    shading_value_unshaded_windows_east = shading_g_value_reduction_factor;
                end
                if interpolated_sun_flux_s > 200.0
                    shading_value_unshaded_windows_south = shading_g_value_reduction_factor;
                end
                if interpolated_sun_flux_w > 200.0
                    shading_value_unshaded_windows_west = shading_g_value_reduction_factor;
                end
            end
            
            total_sun_heat_gain =   shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n + ...
                                    shading_value_shaded_windows_north * shaded_glazing_area_n * interpolated_shading_flux + ...
                                    shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e + ...
                                    shading_value_shaded_windows_east * shaded_glazing_area_e * interpolated_shading_flux + ...
                                    shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s + ...
                                    shading_value_shaded_windows_south * shaded_glazing_area_s * interpolated_shading_flux + ...
                                    shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w + ...
                                    shading_value_shaded_windows_west * shaded_glazing_area_w * interpolated_shading_flux;

            int_heat_gain = occupancy_schedule(hour) * occupancy_power + equipment_schedule(hour) * equipment_power;
                                            
            if lighting_schedule(hour) > 0.0
               if (shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n + ...
                   shading_value_shaded_windows_north * shaded_glazing_area_n * interpolated_shading_flux) / ...
                   glazing_area_n < 15.0
                   int_heat_gain = int_heat_gain + lighting_schedule(hour) * lighting_power * lighting_north_side;
               end 
               if (shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e + ...
                   shading_value_shaded_windows_east * shaded_glazing_area_e * interpolated_shading_flux) / ...
                   glazing_area_e < 15.0
                   int_heat_gain = int_heat_gain + lighting_schedule(hour) * lighting_power * lighting_east_side;
               end 
               if (shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s + ...
                   shading_value_shaded_windows_south * shaded_glazing_area_s * interpolated_shading_flux) / ...
                   glazing_area_s < 15.0
                   int_heat_gain = int_heat_gain + lighting_schedule(hour) * lighting_power * lighting_south_side;
               end 
               if (shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w + ...
                   shading_value_shaded_windows_west * shaded_glazing_area_w * interpolated_shading_flux) / ...
                   glazing_area_w < 15.0
                   int_heat_gain = int_heat_gain + lighting_schedule(hour) * lighting_power * lighting_west_side;
               end                
            end

            % - air temperature equation
            right_matrix(line_air) = building_height * floor_area * 1006 * 1.185 * initial_temperatures(line_air) + ...
                                    wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp + ...
                                    thermal_bridges * time_step * interpolated_amb_temp + ...
                                    (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp + ...
                                    int_heat_gain_to_air_coef * int_heat_gain * time_step;
                                
            % - temperature of the inside node of the north glazing
            right_matrix(line_in_glazing_n) = int_heat_gain_to_glazing_n_coef * int_heat_gain * time_step + time_step * sun_heat_gain_to_inside_glazing * ...
                  (shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n + ...
                   shading_value_shaded_windows_north * shaded_glazing_area_n * interpolated_shading_flux);

            % - temperature of the inside node of the east glazing
            right_matrix(line_in_glazing_e) = int_heat_gain_to_glazing_e_coef * int_heat_gain * time_step + time_step * sun_heat_gain_to_inside_glazing * ...
                  (shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e + ...
                   shading_value_shaded_windows_east * shaded_glazing_area_e * interpolated_shading_flux);

            % - temperature of the inside node of the south glazing
            right_matrix(line_in_glazing_s) = int_heat_gain_to_glazing_s_coef * int_heat_gain * time_step + time_step * sun_heat_gain_to_inside_glazing * ...
                  (shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s + ...
                   shading_value_shaded_windows_south * shaded_glazing_area_s * interpolated_shading_flux);

            % - temperature of the inside node of the west glazing
            right_matrix(line_in_glazing_w) = int_heat_gain_to_glazing_w_coef * int_heat_gain * time_step + time_step * sun_heat_gain_to_inside_glazing * ...
                  (shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w + ...
                   shading_value_shaded_windows_west * shaded_glazing_area_w * interpolated_shading_flux);

            % - temperature of the outside node of the north glazing
            right_matrix(line_out_glazing_n) = time_step * sun_heat_gain_to_outside_glazing * (shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n + ...
                   shading_value_shaded_windows_north * shaded_glazing_area_n * interpolated_shading_flux) + ...
                   interpolated_amb_temp * glazing_area_n * surf_htc_out * time_step;

            % - temperature of the outside node of the east glazing
            right_matrix(line_out_glazing_e) = time_step * sun_heat_gain_to_outside_glazing * (shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e + ...
                   shading_value_shaded_windows_east * shaded_glazing_area_e * interpolated_shading_flux) + ...
                   interpolated_amb_temp * glazing_area_e * surf_htc_out * time_step;

            % - temperature of the outside node of the south glazing
            right_matrix(line_out_glazing_s) = time_step * sun_heat_gain_to_outside_glazing * (shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s + ...
                   shading_value_shaded_windows_south * shaded_glazing_area_s * interpolated_shading_flux) + ...
                   interpolated_amb_temp * glazing_area_s * surf_htc_out * time_step;

            % - temperature of the outside node of the west glazing
            right_matrix(line_out_glazing_w) = time_step * sun_heat_gain_to_outside_glazing *(shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w + ...
                   shading_value_shaded_windows_west * shaded_glazing_area_w * interpolated_shading_flux) + ...
                   interpolated_amb_temp * glazing_area_w * surf_htc_out * time_step;

            % - temperature of the inside node of the north window frame
            right_matrix(line_in_frame_n) = int_heat_gain_to_frame_n_coef * int_heat_gain * time_step;

            % - temperature of the inside node of the east window frame
            right_matrix(line_in_frame_e) = int_heat_gain_to_frame_e_coef * int_heat_gain * time_step;

            % - temperature of the inside node of the south window frame
            right_matrix(line_in_frame_s) = int_heat_gain_to_frame_s_coef * int_heat_gain * time_step;

            % - temperature of the inside node of the west window frame
            right_matrix(line_in_frame_w) = int_heat_gain_to_frame_w_coef * int_heat_gain * time_step;

            % - temperature of the outside node of the north window frame
            right_matrix(line_out_frame_n) = (unshaded_frame_area_n * interpolated_sun_flux_n + shaded_frame_area_n * interpolated_shading_flux) * 0.8 * time_step + interpolated_amb_temp * frame_area_n * surf_htc_out * time_step;

            % - temperature of the outside node of the east window frame
            right_matrix(line_out_frame_e) = (unshaded_frame_area_e * interpolated_sun_flux_e + shaded_frame_area_e * interpolated_shading_flux) * 0.8 * time_step + interpolated_amb_temp * frame_area_e * surf_htc_out * time_step;

            % - temperature of the outside node of the south window frame
            right_matrix(line_out_frame_s) = (unshaded_frame_area_s * interpolated_sun_flux_s + shaded_frame_area_s * interpolated_shading_flux) * 0.8 * time_step + interpolated_amb_temp * frame_area_s * surf_htc_out * time_step;

            % - temperature of the outside node of the west window frame
            right_matrix(line_out_frame_w) = (unshaded_frame_area_w * interpolated_sun_flux_w + shaded_frame_area_w * interpolated_shading_flux) * 0.8 * time_step + interpolated_amb_temp * frame_area_w * surf_htc_out * time_step;

            % - temperature of the 1. node of the north wall
            right_matrix(line_wall_n_1) = wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures(line_wall_n_1) ...
                + int_heat_gain_to_wall_n_coef * int_heat_gain * time_step;

            % - temperature of the 1. node of the east wall
            right_matrix(line_wall_e_1) = wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures(line_wall_e_1) ...
                + int_heat_gain_to_wall_e_coef * int_heat_gain * time_step;

            % - temperature of the 1. node of the south wall
            right_matrix(line_wall_s_1) = wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures(line_wall_s_1) ...
                + int_heat_gain_to_wall_s_coef * int_heat_gain * time_step;

            % - temperature of the 1. node of the west wall
            right_matrix(line_wall_w_1) = wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures(line_wall_w_1) ...
                + int_heat_gain_to_wall_w_coef * int_heat_gain * time_step;

            % - temperature of the 1. node of the roof
            right_matrix(line_roof_1) = roof_area * roof_inside_capacity_density * roof_inside_thickness * 0.5 * initial_temperatures(line_roof_1) ...
                + int_heat_gain_to_roof_coef * int_heat_gain * time_step;

            % - temperature of the 1. node of the floor
            right_matrix(line_floor_1) = floor_area * floor_inside_capacity_density * floor_inside_thickness * 0.5 * initial_temperatures(line_floor_1) ... 
                + int_heat_gain_to_floor_coef * int_heat_gain * time_step;

            % - temperature of the 1. node of the internal walls
            right_matrix(line_int_wall_1) = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures(line_int_wall_1) ...
                + sun_heat_gain_to_int_wall * total_sun_heat_gain * time_step + ...
                + int_heat_gain_to_int_wall_coef * int_heat_gain * time_step;

            % - temperature of the 1. node of the internal ceiling
            right_matrix(line_int_ceiling_1) = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures(line_int_ceiling_1)  ...
                + sun_heat_gain_to_int_ceiling * total_sun_heat_gain * time_step + ...
                + int_heat_gain_to_int_ceiling_coef * int_heat_gain * time_step;


            % - temperature of the 2. node of the north wall
            right_matrix(line_wall_n_2) = wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures(line_wall_n_2);

            % - temperature of the 2. node of the east wall
            right_matrix(line_wall_e_2) = wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures(line_wall_e_2);

            % - temperature of the 2. node of the south wall
            right_matrix(line_wall_s_2) = wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures(line_wall_s_2);

            % - temperature of the 2. node of the west wall
            right_matrix(line_wall_w_2) = wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures(line_wall_w_2);

            % - temperature of the 2. node of the roof
            right_matrix(line_roof_2) = roof_area * roof_inside_capacity_density * roof_inside_thickness * 0.5 * initial_temperatures(line_roof_2);

            % - temperature of the 2. node of the floor
            right_matrix(line_floor_2) = floor_area * floor_inside_capacity_density * floor_inside_thickness * 0.5 * initial_temperatures(line_floor_2);

            % - temperature of the 2. node of the internal walls
            right_matrix(line_int_wall_2) = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures(line_int_wall_2);

            % - temperature of the 2. node of the internal ceiling
            right_matrix(line_int_ceiling_2) = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures(line_int_ceiling_2);


            % - temperature of the 3. node of the north wall
            right_matrix(line_wall_n_3) = wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures(line_wall_n_3);

            % - temperature of the 3. node of the east wall
            right_matrix(line_wall_e_3) = wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures(line_wall_e_3);

            % - temperature of the 3. node of the south wall
            right_matrix(line_wall_s_3) = wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures(line_wall_s_3);

            % - temperature of the 3. node of the west wall
            right_matrix(line_wall_w_3) = wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures(line_wall_w_3);

            % - temperature of the 3. node of the roof
            right_matrix(line_roof_3) = roof_area * roof_outside_capacity_density * roof_outside_thickness * 0.5 * initial_temperatures(line_roof_3);

            % - temperature of the 3. node of the floor
            right_matrix(line_floor_3) = floor_area * floor_outside_capacity_density * floor_outside_thickness * 0.5 * initial_temperatures(line_floor_3);

            % - temperature of the 3. node of the internal walls
            right_matrix(line_int_wall_3) = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures(line_int_wall_3);

            % - temperature of the 3. node of the internal ceiling
            right_matrix(line_int_ceiling_3) = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures(line_int_ceiling_3);


            % - temperature of the 4. node of the north wall
            right_matrix(line_wall_n_4) = wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures(line_wall_n_4) ...
                + interpolated_amb_temp * surf_htc_out * wall_area_n * time_step + 0.8 * interpolated_sun_flux_n * wall_area_n * time_step;

            % - temperature of the 4. node of the east wall
            right_matrix(line_wall_e_4) = wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures(line_wall_e_4) ...
                + interpolated_amb_temp * surf_htc_out * wall_area_e * time_step + 0.8 * interpolated_sun_flux_e * wall_area_e * time_step;
                
            % - temperature of the 4. node of the south wall
            right_matrix(line_wall_s_4) = wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures(line_wall_s_4) ...
                + interpolated_amb_temp * surf_htc_out * wall_area_s * time_step + 0.8 * interpolated_sun_flux_s * wall_area_s * time_step;
                
            % - temperature of the 4. node of the west wall
            right_matrix(line_wall_w_4) = wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures(line_wall_w_4) ...
                + interpolated_amb_temp * surf_htc_out * wall_area_w * time_step + 0.8 * interpolated_sun_flux_w * wall_area_w * time_step;
                
            % - temperature of the 4. node of the roof
            right_matrix(line_roof_4) = roof_area * roof_outside_capacity_density * roof_outside_thickness * 0.5 * initial_temperatures(line_roof_4) ...
                + interpolated_amb_temp * surf_htc_out * roof_area * time_step + 0.8 * interpolated_sun_flux_r * roof_area * time_step;
                
            % - temperature of the 4. node of the floor
            right_matrix(line_floor_4) = floor_area * floor_outside_capacity_density * floor_outside_thickness * 0.5 * initial_temperatures(line_floor_4) ...
                + interpolated_ground_temp * surf_htc_out * floor_area * time_step;
                
            % - temperature of the 4. node of the internal walls
            right_matrix(line_int_wall_4) = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures(line_int_wall_4);

            % - temperature of the 4. node of the internal ceiling
            right_matrix(line_int_ceiling_4) = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures(line_int_ceiling_4);
            
            initial_temperatures = inverse_matrix * right_matrix;
            
            heating_power = 0.0;
            cooling_power = 0.0;
            if initial_temperatures(line_air) < heating_setpoint
                for i=1:5
                    heating_power = heating_power + left_matrix(line_air, line_air) * (heating_setpoint - initial_temperatures(line_air)) / time_step;
                    right_matrix(line_air) = building_height * floor_area * 1006 * 1.185 * initial_temperatures(line_air) + ...
                                            wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp + ...
                                            thermal_bridges * time_step * interpolated_amb_temp + ...
                                            (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp + ...
                                            int_heat_gain_to_air_coef * int_heat_gain * time_step + ...
                                            heating_power * time_step;
                    initial_temperatures = inverse_matrix * right_matrix;                    
                end                
            elseif initial_temperatures(line_air) > cooling_setpoint
                for i=1:5
                    cooling_power = cooling_power + left_matrix(line_air, line_air) * (cooling_setpoint - initial_temperatures(line_air)) / time_step;
                    right_matrix(line_air) = building_height * floor_area * 1006 * 1.185 * initial_temperatures(line_air) + ...
                                            wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp + ...
                                            thermal_bridges * time_step * interpolated_amb_temp + ...
                                            (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp + ...
                                            int_heat_gain_to_air_coef * int_heat_gain * time_step + ...
                                            cooling_power * time_step;
                    initial_temperatures = inverse_matrix * right_matrix;                    
                end                
            end    
            if hour_counter > weather_file_size(1) - 8760
                output_heating_power(hour_counter - weather_file_size(1) + 8760) = output_heating_power(hour_counter - weather_file_size(1) + 8760) + heating_power * time_step / 3600;
                output_cooling_power(hour_counter - weather_file_size(1) + 8760) = output_cooling_power(hour_counter - weather_file_size(1) + 8760) + cooling_power * time_step / 3600;
                output_lighting_electricity(hour_counter - weather_file_size(1) + 8760) = output_lighting_electricity(hour_counter - weather_file_size(1) + 8760) + ...
                    (int_heat_gain - occupancy_schedule(hour) * occupancy_power - equipment_schedule(hour) * equipment_power) * time_step / 3600;
                output_equipment_electricity(hour_counter - weather_file_size(1) + 8760) = output_equipment_electricity(hour_counter - weather_file_size(1) + 8760) + ...
                    equipment_schedule(hour) * equipment_power * time_step / 3600;                
            end
        end
        if hour_counter > weather_file_size(1) - 8760
            output_temperatures(hour_counter - weather_file_size(1) + 8760, :) = initial_temperatures(:);
%             total_sun_heat_gain_temp(hour_counter - weather_file_size(1) + 8760, 1) = (sun_heat_gain_to_int_wall + sun_heat_gain_to_int_ceiling) *  total_sun_heat_gain;
%             total_sun_heat_gain_temp(hour_counter - weather_file_size(1) + 8760, 2) = diff_radiation(hour_counter);
%             total_sun_heat_gain_temp(hour_counter - weather_file_size(1) + 8760, 3) = beam_radiation(hour_counter);
%             total_sun_heat_gain_temp(hour_counter - weather_file_size(1) + 8760, 4) = ambient_temp(hour_counter);
        end
        hour = hour + 1;
        hour_counter = hour_counter + 1;
    end 
end
output_total_heating_power = sum(output_heating_power) / 10^6
output_total_cooling_power = sum(output_cooling_power) / 10^6
output_total_lighting_power = sum(output_lighting_electricity) / 10^6
output_total_equipment_power = sum(output_equipment_electricity) / 10^6

%%
% load("ida_results_ver2.mat");
% st_dev_tair = 0.0;
% st_dev_q_heating = 0.0;
% st_dev_q_cooling = 0.0;
% counter_heating = 0;
% counter_cooling = 0;
% for i = 1:8760
%     st_dev_tair = st_dev_tair + (output_temperatures(i, 1) - ida_air_temp(i)) ^ 2;
%     if output_heating_power(i) > 0.0 || ida_heating_power(i) > 0.0
%         st_dev_q_heating = st_dev_q_heating + (output_heating_power(i) - ida_heating_power(i)) ^ 2;
%         counter_heating = counter_heating + 1;
%     end
%     if -output_cooling_power(i) > 0.0 || ida_cooling_power(i) > 0.0
%         st_dev_q_cooling = st_dev_q_cooling + (-output_cooling_power(i) - ida_cooling_power(i)) ^ 2;
%         counter_cooling = counter_cooling + 1;
%     end
% end
% st_dev_tair = (st_dev_tair / 8760) ^ 0.5
% st_dev_q_heating = (st_dev_q_heating / counter_heating) ^ 0.5 / 1000.0 
% st_dev_q_cooling = (st_dev_q_cooling / counter_cooling) ^ 0.5 / 1000.0

%%
% figure(1)
% plot(1:8760,output_temperatures(:,1));
% hold on
% plot(1:8760,ida_air_temp);
% legend(["matlab" "ida-ice"]);
% title("Room air temperatures");
% 
% figure(2)
% plot(1:8760,output_heating_power);
% hold on
% plot(1:8760,ida_heating_power);
% legend(["matlab" "ida-ice"]);
% title("Heating power");
% 
% figure(3)
% plot(1:8760,-output_cooling_power);
% hold on
% plot(1:8760,ida_cooling_power);
% legend(["matlab" "ida-ice"]);
% title("Cooling power");
%%
% for i=1:49
%     for j=1:49
%         if left_matrix(i, j) ~= left_matrix(j, i)
%             i
%             j
%         end
%     end
% end
% roof_area / (1 / surf_htc_in + 1 / surf_htc_out + roof_inside_thickness / roof_inside_lyamda + roof_outside_thickness / roof_outside_lyamda)
% (wall_area_n + wall_area_e + wall_area_w + wall_area_s) / (1 / surf_htc_in + 1 / surf_htc_out + wall_inside_thickness / wall_inside_lyamda + wall_outside_thickness / wall_outside_lyamda)
%  (glazing_area_n + glazing_area_e + glazing_area_w + glazing_area_s) * glazing_u_value + ...
%      (frame_area_n + frame_area_e + frame_area_w + frame_area_s) * frame_u_value

% save output for validation
save('matlab_ref_results.mat', ...
    'output_temperatures', ...
    'output_heating_power', ...
    'output_cooling_power', ...
    'output_lighting_electricity', ...
    'output_equipment_electricity', ...
    'left_matrix', ...
    '-v7')