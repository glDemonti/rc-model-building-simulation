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

% - height of a building (needed for air temperature calculation)
building_height = 2.5 * 3; % [m]

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
