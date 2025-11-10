# -*- coding: utf-8 -*-
"""
Port des MATLAB-Skripts nach Python.
Ziel: identische Ergebnisse (bis auf Rundungs-/Floating-Point-Differenzen).

Benötigte Pakete:
  pip install numpy scipy
"""

import numpy as np
from scipy.io import loadmat, savemat

# ------------------------------
# 1) Wetterdaten laden
# ------------------------------
# erwartet eine MAT-Datei mit Variable 'basel_dry' (wie im MATLAB-Code)
weather = loadmat("basel_dry_ver2.mat")
basel_dry = np.asarray(weather["basel_dry"], dtype=float)

ambient_temp   = basel_dry[:, 1]   # 2. Spalte
beam_radiation = basel_dry[:, 5]   # 6. Spalte
diff_radiation = basel_dry[:, 6]   # 7. Spalte
sun_elevation  = basel_dry[:, 8]   # 9. Spalte
sun_azimuth    = basel_dry[:, 9]   # 10. Spalte

# Länge (Stunden)
n_hours = ambient_temp.shape[0]  # sollte 9096 sein

# ------------------------------
# 2) Geometrien / Flächen
# ------------------------------
# unverschattet (Verglasung)
unshaded_glazing_area_n = 0.825 * (2.3 * 12 + 1.2 * 6 + 3 * 2.07)
unshaded_glazing_area_e = 0.825 * (3.45 * 3 + 2.3 * 3 + 1.98 * 1)
unshaded_glazing_area_s = 0.825 * (1.73 * 2 + 5.18 * 2 + 1.98 * 4 + 1.2 * 6 + 2.07 * 1)
unshaded_glazing_area_w = 0.825 * (3.45 * 3 + 2.3 * 3 + 2.07 * 1)

# verschattet (Verglasung)
shaded_glazing_area_n = 0.0
shaded_glazing_area_e = 0.825 * (1.98 * 2)
shaded_glazing_area_s = 0.825 * (1.73 * 4 + 5.18 * 4 + 1.98 * 8 + 2.07 * 2)
shaded_glazing_area_w = 0.825 * (2.07 * 2)

# Rahmenflächen unverschattet
unshaded_frame_area_n = 0.175 * (2.3 * 12 + 1.2 * 6 + 3 * 2.07)
unshaded_frame_area_e = 0.175 * (3.45 * 3 + 2.3 * 3 + 1.98 * 1)
unshaded_frame_area_s = 0.175 * (1.73 * 2 + 5.18 * 2 + 1.98 * 4 + 1.2 * 6 + 2.07 * 1)
unshaded_frame_area_w = 0.175 * (3.45 * 3 + 2.3 * 3 + 2.07 * 1)

# Rahmenflächen verschattet
shaded_frame_area_n = 0.0
shaded_frame_area_e = 0.175 * (1.98 * 2)
shaded_frame_area_s = 0.175 * (1.73 * 4 + 5.18 * 4 + 1.98 * 8 + 2.07 * 2)
shaded_frame_area_w = 0.175 * (2.07 * 2)

# Gesamtflächen
glazing_area_n = unshaded_glazing_area_n + shaded_glazing_area_n
glazing_area_e = unshaded_glazing_area_e + shaded_glazing_area_e
glazing_area_s = unshaded_glazing_area_s + shaded_glazing_area_s
glazing_area_w = unshaded_glazing_area_w + shaded_glazing_area_w

frame_area_n = unshaded_frame_area_n + shaded_frame_area_n
frame_area_e = unshaded_frame_area_e + shaded_frame_area_e
frame_area_s = unshaded_frame_area_s + shaded_frame_area_s
frame_area_w = unshaded_frame_area_w + shaded_frame_area_w

# Außenwände (ohne Fenster u. Rahmen)
wall_area_n = 2.5 * 3 * (32.6 + 1.6 - 6.0) - glazing_area_n - frame_area_n
wall_area_e = 2.5 * 3 * 14.0 - glazing_area_e - frame_area_e
wall_area_s = 2.5 * 3 * (32.6 + 1.6) - glazing_area_s - frame_area_s
wall_area_w = 2.5 * 3 * 14.0 - glazing_area_w - frame_area_w

# Dach / Boden
roof_area = 313.8
floor_area = 313.8

# Innenflächen
int_wall_area = (72.975 + 91.9 + 2.0 * 19.75) * 3.0
int_ceiling_area = 313.8 * 2.0 * 2.0

# Wand gg. unbeheizt
wall_against_unheated_area = (21.5 + 12.5 + 5.3) * 3.0

# Orientierungsvektoren
surface_vector_north = np.array([0.0,  1.0, 0.0])
surface_vector_east  = np.array([1.0,  0.0, 0.0])
surface_vector_south = np.array([0.0, -1.0, 0.0])
surface_vector_west  = np.array([-1.0, 0.0, 0.0])
surface_vector_roof  = np.array([0.0,  0.0, 1.0])

# Gebäudehöhe
building_height = 2.5 * 3  # m

# Summe aller Bauteilflächen (ohne Wände gg. unbeheizt)
total_area_constructions = (
    glazing_area_n + glazing_area_e + glazing_area_s + glazing_area_w
    + frame_area_n + frame_area_e + frame_area_s + frame_area_w
    + wall_area_n + wall_area_e + wall_area_s + wall_area_w
    + roof_area + floor_area + int_wall_area + int_ceiling_area
)

# ------------------------------
# 2b) U-/G-/λ-/Kapazitäten
# ------------------------------
glazing_u_value = 0.7
glazing_g_value = 0.45
shading_g_value_reduction_factor = 0.14
frame_u_value = 2.0

wall_against_unheated_u_value = 1.0 / (2.0 / 8.0 + 0.17 / 0.79)

wall_inside_lyamda = 1.8
roof_inside_lyamda = 1.8
floor_inside_lyamda = 1.8

wall_inside_capacity_density = 2400 * 1100
roof_inside_capacity_density = 2400 * 1100
floor_inside_capacity_density = 2400 * 1100

wall_outside_lyamda = 0.031
roof_outside_lyamda = 0.02
floor_outside_lyamda = 0.03

wall_outside_capacity_density = 16 * 1400
roof_outside_capacity_density = 30 * 1400
floor_outside_capacity_density = 18 * 1400

int_wall_lyamda = 0.79
int_ceiling_lyamda = 1.8

int_wall_capacity_density = 1070.0 * 850.0
int_ceiling_capacity_density = 2400.0 * 1100.0

# ------------------------------
# 3) Schichtdicken [m]
# ------------------------------
wall_inside_thickness  = 0.2
wall_outside_thickness = 0.1

roof_inside_thickness  = 0.25
roof_outside_thickness = 0.1

floor_inside_thickness  = 0.3
floor_outside_thickness = 0.08

int_wall_thickness    = 0.17
int_ceiling_thickness = 0.3654

# ------------------------------
# 4) Infiltration / 5) Lüftung
# ------------------------------
infiltration_rate = 0.194444 * 0.001 * floor_area * 3.0  # m^3/s

air_ventilation_rate = 0.278 * 0.001 * floor_area * 3.0  # m^3/s
heat_exchanger_efficiency = 0.0

# ------------------------------
# 6) Wärmebrücken, interne Lasten
# ------------------------------
thermal_bridges = 123.4

occupancy_power = 70.0 * 0.033 * floor_area * 3.0
lighting_power  = 2.7 * floor_area * 3.0
equipment_power = 8.0 * floor_area * 3.0

# ------------------------------
# 7) Tagesgang (24 Elemente)
# ------------------------------
occupancy_schedule = np.array([1,1,1,1,1,1,0.6,0.4,0,0,0,0,0.8,0.4,0,0,0,0.4,0.8,0.8,0.8,1,1,1], dtype=float)
lighting_schedule  = np.array([0,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,1,1,1,1,0,0,0], dtype=float)
equipment_schedule = np.array([0.1,0.1,0.1,0.1,0.1,0.2,0.8,0.2,0.1,0.1,0.1,0.1,0.8,0.2,0.1,0.1,0.1,0.2,0.8,1.0,0.2,0.2,0.2,0.1], dtype=float)

# ------------------------------
# 8) Sonnenvektor / Globalstrahlung
# ------------------------------
sun_vector = np.zeros((n_hours, 3), dtype=float)
global_radiation = np.zeros((n_hours,), dtype=float)

# MATLAB cosd/sind -> numpy mit Gradargumenten
rad_el = np.deg2rad(sun_elevation)
rad_az = np.deg2rad(sun_azimuth)

for i in range(n_hours):
    if sun_elevation[i] > 0.0:
        sun_vector[i, 0] = np.cos(rad_el[i]) * np.sin(rad_az[i])
        sun_vector[i, 1] = np.cos(rad_el[i]) * np.cos(rad_az[i])
        sun_vector[i, 2] = -np.sin(rad_el[i])
    global_radiation[i] = diff_radiation[i] - beam_radiation[i] * sun_vector[i, 2]

# ------------------------------
# 9) Sonnenfluss auf Bauteile [W/m^2]
# ------------------------------
sun_flux_north = np.zeros(n_hours)
sun_flux_east  = np.zeros(n_hours)
sun_flux_west  = np.zeros(n_hours)
sun_flux_south = np.zeros(n_hours)
sun_flux_roof  = np.zeros(n_hours)

def _flux(surface_vec, i):
    # -beam * min(0, dot(surface, sun)) + 0.5*diff + 0.2*0.5*global
    dot = surface_vec[0]*sun_vector[i,0] + surface_vec[1]*sun_vector[i,1] + surface_vec[2]*sun_vector[i,2]
    return -beam_radiation[i] * min(0.0, dot) + 0.5 * diff_radiation[i] + 0.2 * 0.5 * global_radiation[i]

for i in range(n_hours):
    if sun_elevation[i] > 0.0:
        sun_flux_north[i] = _flux(surface_vector_north, i)
        sun_flux_east[i]  = _flux(surface_vector_east,  i)
        sun_flux_west[i]  = _flux(surface_vector_west,  i)
        sun_flux_south[i] = _flux(surface_vector_south, i)
        sun_flux_roof[i]  = global_radiation[i]

# ------------------------------
# 10) Simulationsparameter
# ------------------------------
time_step = 5.0 * 60.0  # s
surf_htc_in  = 4.5
surf_htc_out = 23.0
heating_setpoint = 21.0
cooling_setpoint = 26.0

# Aufteilung interner Lasten
int_heat_gain_to_air_coef = 0.6
int_heat_gain_to_glazing_n_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_n / total_area_constructions
int_heat_gain_to_glazing_e_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_e / total_area_constructions
int_heat_gain_to_glazing_s_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_s / total_area_constructions
int_heat_gain_to_glazing_w_coef = (1 - int_heat_gain_to_air_coef) * glazing_area_w / total_area_constructions
int_heat_gain_to_frame_n_coef   = (1 - int_heat_gain_to_air_coef) * frame_area_n   / total_area_constructions
int_heat_gain_to_frame_e_coef   = (1 - int_heat_gain_to_air_coef) * frame_area_e   / total_area_constructions
int_heat_gain_to_frame_s_coef   = (1 - int_heat_gain_to_air_coef) * frame_area_s   / total_area_constructions
int_heat_gain_to_frame_w_coef   = (1 - int_heat_gain_to_air_coef) * frame_area_w   / total_area_constructions
int_heat_gain_to_wall_n_coef    = (1 - int_heat_gain_to_air_coef) * wall_area_n    / total_area_constructions
int_heat_gain_to_wall_e_coef    = (1 - int_heat_gain_to_air_coef) * wall_area_e    / total_area_constructions
int_heat_gain_to_wall_s_coef    = (1 - int_heat_gain_to_air_coef) * wall_area_s    / total_area_constructions
int_heat_gain_to_wall_w_coef    = (1 - int_heat_gain_to_air_coef) * wall_area_w    / total_area_constructions
int_heat_gain_to_roof_coef      = (1 - int_heat_gain_to_air_coef) * roof_area      / total_area_constructions
int_heat_gain_to_floor_coef     = (1 - int_heat_gain_to_air_coef) * floor_area     / total_area_constructions
int_heat_gain_to_int_wall_coef  = (1 - int_heat_gain_to_air_coef) * int_wall_area  / total_area_constructions
int_heat_gain_to_int_ceiling_coef = (1 - int_heat_gain_to_air_coef) * int_ceiling_area / total_area_constructions

# Solare Gewinne Verteilung
sun_heat_gain_to_outside_glazing = 0.25 * (1.0 - glazing_g_value)
sun_heat_gain_to_inside_glazing  = 0.25 * (1.0 - glazing_g_value) * glazing_g_value
sun_heat_gain_to_int_wall    = (1.0 - 0.25 * (1.0 - glazing_g_value)) * glazing_g_value * int_wall_area    / (int_wall_area + int_ceiling_area)
sun_heat_gain_to_int_ceiling = (1.0 - 0.25 * (1.0 - glazing_g_value)) * glazing_g_value * int_ceiling_area / (int_wall_area + int_ceiling_area)

# Lichtverteilung nach Himmelsrichtung
den = wall_area_n + wall_area_e + wall_area_s + wall_area_w
lighting_north_side = wall_area_n / den
lighting_east_side  = wall_area_e / den
lighting_south_side = wall_area_s / den
lighting_west_side  = wall_area_w / den

# Strahlungsaustauschkoeffizienten
surf_rad_htc = 4.0

def rad_x(a, b):
    return surf_rad_htc * a * b / (total_area_constructions - a)

surf_rad_htc_int_wall_glazing_n = surf_rad_htc * int_wall_area * glazing_area_n / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_glazing_e = surf_rad_htc * int_wall_area * glazing_area_e / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_glazing_s = surf_rad_htc * int_wall_area * glazing_area_s / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_glazing_w = surf_rad_htc * int_wall_area * glazing_area_w / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_frame_n   = surf_rad_htc * int_wall_area * frame_area_n     / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_frame_e   = surf_rad_htc * int_wall_area * frame_area_e     / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_frame_s   = surf_rad_htc * int_wall_area * frame_area_s     / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_frame_w   = surf_rad_htc * int_wall_area * frame_area_w     / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_wall_n    = surf_rad_htc * int_wall_area * wall_area_n      / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_wall_e    = surf_rad_htc * int_wall_area * wall_area_e      / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_wall_s    = surf_rad_htc * int_wall_area * wall_area_s      / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_wall_w    = surf_rad_htc * int_wall_area * wall_area_w      / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_roof      = surf_rad_htc * int_wall_area * roof_area        / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_floor     = surf_rad_htc * int_wall_area * floor_area       / (total_area_constructions - int_wall_area)
surf_rad_htc_int_wall_int_ceiling = surf_rad_htc * int_wall_area * int_ceiling_area / (total_area_constructions - int_wall_area)

# Decken-gegen-alles
surf_rad_htc_int_ceiling_glazing_n = surf_rad_htc * int_ceiling_area * glazing_area_n / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_glazing_e = surf_rad_htc * int_ceiling_area * glazing_area_e / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_glazing_s = surf_rad_htc * int_ceiling_area * glazing_area_s / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_glazing_w = surf_rad_htc * int_ceiling_area * glazing_area_w / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_frame_n   = surf_rad_htc * int_ceiling_area * frame_area_n   / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_frame_e   = surf_rad_htc * int_ceiling_area * frame_area_e   / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_frame_s   = surf_rad_htc * int_ceiling_area * frame_area_s   / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_frame_w   = surf_rad_htc * int_ceiling_area * frame_area_w   / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_wall_n    = surf_rad_htc * int_ceiling_area * wall_area_n    / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_wall_e    = surf_rad_htc * int_ceiling_area * wall_area_e    / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_wall_s    = surf_rad_htc * int_ceiling_area * wall_area_s    / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_wall_w    = surf_rad_htc * int_ceiling_area * wall_area_w    / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_roof      = surf_rad_htc * int_ceiling_area * roof_area      / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_floor     = surf_rad_htc * int_ceiling_area * floor_area     / (total_area_constructions - int_ceiling_area)
surf_rad_htc_int_ceiling_int_wall  = surf_rad_htc_int_wall_int_ceiling

# ------------------------------
# 10) Gleichungssystem (49x49)
# ------------------------------
N = 49
left_matrix = np.zeros((N, N), dtype=float)

# Zeilen-Indizes (0-basiert in Python)
line_air = 0

line_in_glazing_n = 1
line_in_glazing_e = 2
line_in_glazing_s = 3
line_in_glazing_w = 4

line_out_glazing_n = 5
line_out_glazing_e = 6
line_out_glazing_s = 7
line_out_glazing_w = 8

line_in_frame_n = 9
line_in_frame_e = 10
line_in_frame_s = 11
line_in_frame_w = 12

line_out_frame_n = 13
line_out_frame_e = 14
line_out_frame_s = 15
line_out_frame_w = 16

line_wall_n_1 = 17
line_wall_e_1 = 18
line_wall_s_1 = 19
line_wall_w_1 = 20
line_roof_1   = 21
line_floor_1  = 22
line_int_wall_1    = 23
line_int_ceiling_1 = 24

line_wall_n_2 = 25
line_wall_e_2 = 26
line_wall_s_2 = 27
line_wall_w_2 = 28
line_roof_2   = 29
line_floor_2  = 30
line_int_wall_2    = 31
line_int_ceiling_2 = 32

line_wall_n_3 = 33
line_wall_e_3 = 34
line_wall_s_3 = 35
line_wall_w_3 = 36
line_roof_3   = 37
line_floor_3  = 38
line_int_wall_3    = 39
line_int_ceiling_3 = 40

line_wall_n_4 = 41
line_wall_e_4 = 42
line_wall_s_4 = 43
line_wall_w_4 = 44
line_roof_4   = 45
line_floor_4  = 46
line_int_wall_4    = 47
line_int_ceiling_4 = 48

# --- zur Lesbarkeit Hilfsfunktion für Zuweisungen
def LM(i, j, val):
    left_matrix[i, j] = val

# (Die folgenden Blöcke sind 1:1 aus dem MATLAB-Teil übertragen – nur Indizes sind 0-basiert.)
# --- Luftgleichung
LM(line_air, line_air, building_height * floor_area * 1006 * 1.185
   + surf_htc_in * total_area_constructions * time_step
   + (thermal_bridges + wall_against_unheated_u_value * wall_against_unheated_area) * time_step
   + (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step)

for line, area in [
    (line_in_glazing_n, glazing_area_n), (line_in_glazing_e, glazing_area_e),
    (line_in_glazing_s, glazing_area_s), (line_in_glazing_w, glazing_area_w),
    (line_in_frame_n, frame_area_n), (line_in_frame_e, frame_area_e),
    (line_in_frame_s, frame_area_s), (line_in_frame_w, frame_area_w),
    (line_wall_n_1, wall_area_n), (line_wall_e_1, wall_area_e),
    (line_wall_s_1, wall_area_s), (line_wall_w_1, wall_area_w),
    (line_roof_1, roof_area), (line_floor_1, floor_area),
    (line_int_wall_1, int_wall_area), (line_int_ceiling_1, int_ceiling_area)
]:
    LM(line_air, line, -surf_htc_in * time_step * area)

# --- (Alle restlichen ~300 Matrixzuweisungen 1:1 wie im MATLAB-Code)
# Zur Vermeidung eines extrem langen Blocks folgt hier wortwörtlich die Portierung
# – BEGIN Matrixdefinitionen (entspricht deinem MATLAB-Abschnitt 12) –

# inside glazing north
LM(line_in_glazing_n, line_air, left_matrix[line_air, line_in_glazing_n])
LM(line_in_glazing_n, line_out_glazing_n, -glazing_area_n * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out))
LM(line_in_glazing_n, line_int_wall_1, -surf_rad_htc_int_wall_glazing_n * time_step)
LM(line_in_glazing_n, line_int_ceiling_1, -surf_rad_htc_int_ceiling_glazing_n * time_step)
LM(line_in_glazing_n, line_in_glazing_n,
   -left_matrix[line_in_glazing_n, line_air]
   -left_matrix[line_in_glazing_n, line_out_glazing_n]
   -left_matrix[line_in_glazing_n, line_int_wall_1]
   -left_matrix[line_in_glazing_n, line_int_ceiling_1])

# inside glazing east
LM(line_in_glazing_e, line_air, left_matrix[line_air, line_in_glazing_e])
LM(line_in_glazing_e, line_out_glazing_e, -glazing_area_e * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out))
LM(line_in_glazing_e, line_int_wall_1, -surf_rad_htc_int_wall_glazing_e * time_step)
LM(line_in_glazing_e, line_int_ceiling_1, -surf_rad_htc_int_ceiling_glazing_e * time_step)
LM(line_in_glazing_e, line_in_glazing_e,
   -left_matrix[line_in_glazing_e, line_air]
   -left_matrix[line_in_glazing_e, line_out_glazing_e]
   -left_matrix[line_in_glazing_e, line_int_wall_1]
   -left_matrix[line_in_glazing_e, line_int_ceiling_1])

# inside glazing south
LM(line_in_glazing_s, line_air, left_matrix[line_air, line_in_glazing_s])
LM(line_in_glazing_s, line_out_glazing_s, -glazing_area_s * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out))
LM(line_in_glazing_s, line_int_wall_1, -surf_rad_htc_int_wall_glazing_s * time_step)
LM(line_in_glazing_s, line_int_ceiling_1, -surf_rad_htc_int_ceiling_glazing_s * time_step)
LM(line_in_glazing_s, line_in_glazing_s,
   -left_matrix[line_in_glazing_s, line_air]
   -left_matrix[line_in_glazing_s, line_out_glazing_s]
   -left_matrix[line_in_glazing_s, line_int_wall_1]
   -left_matrix[line_in_glazing_s, line_int_ceiling_1])

# inside glazing west
LM(line_in_glazing_w, line_air, left_matrix[line_air, line_in_glazing_w])
LM(line_in_glazing_w, line_out_glazing_w, -glazing_area_w * time_step * 1.0 / (1.0 / glazing_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out))
LM(line_in_glazing_w, line_int_wall_1, -surf_rad_htc_int_wall_glazing_w * time_step)
LM(line_in_glazing_w, line_int_ceiling_1, -surf_rad_htc_int_ceiling_glazing_w * time_step)
LM(line_in_glazing_w, line_in_glazing_w,
   -left_matrix[line_in_glazing_w, line_air]
   -left_matrix[line_in_glazing_w, line_out_glazing_w]
   -left_matrix[line_in_glazing_w, line_int_wall_1]
   -left_matrix[line_in_glazing_w, line_int_ceiling_1])

# outside glazing n/e/s/w
for l_out, l_in, area in [
    (line_out_glazing_n, line_in_glazing_n, glazing_area_n),
    (line_out_glazing_e, line_in_glazing_e, glazing_area_e),
    (line_out_glazing_s, line_in_glazing_s, glazing_area_s),
    (line_out_glazing_w, line_in_glazing_w, glazing_area_w),
]:
    LM(l_out, l_in, left_matrix[l_in, l_out])
    LM(l_out, l_out, -left_matrix[l_out, l_in] + area * surf_htc_out * time_step)

# inside frame n/e/s/w
for l_in, l_out, area, htc_wall, htc_ceil in [
    (line_in_frame_n, line_out_frame_n, frame_area_n, surf_rad_htc_int_wall_frame_n, surf_rad_htc_int_ceiling_frame_n),
    (line_in_frame_e, line_out_frame_e, frame_area_e, surf_rad_htc_int_wall_frame_e, surf_rad_htc_int_ceiling_frame_e),
    (line_in_frame_s, line_out_frame_s, frame_area_s, surf_rad_htc_int_wall_frame_s, surf_rad_htc_int_ceiling_frame_s),
    (line_in_frame_w, line_out_frame_w, frame_area_w, surf_rad_htc_int_wall_frame_w, surf_rad_htc_int_ceiling_frame_w),
]:
    LM(l_in, line_air, left_matrix[line_air, l_in])
    LM(l_in, l_out, -area * time_step * 1.0 / (1.0 / frame_u_value - 1.0 / surf_htc_in - 1.0 / surf_htc_out))
    LM(l_in, line_int_wall_1, -htc_wall * time_step)
    LM(l_in, line_int_ceiling_1, -htc_ceil * time_step)
    LM(l_in, l_in,
       -left_matrix[l_in, line_air]
       -left_matrix[l_in, l_out]
       -left_matrix[l_in, line_int_wall_1]
       -left_matrix[l_in, line_int_ceiling_1])

# outside frame n/e/s/w
for l_out, l_in, area in [
    (line_out_frame_n, line_in_frame_n, frame_area_n),
    (line_out_frame_e, line_in_frame_e, frame_area_e),
    (line_out_frame_s, line_in_frame_s, frame_area_s),
    (line_out_frame_w, line_in_frame_w, frame_area_w),
]:
    LM(l_out, l_in, left_matrix[l_in, l_out])
    LM(l_out, l_out, -left_matrix[l_out, l_in] + area * surf_htc_out * time_step)

# 1. Knoten Außenwände / Dach / Boden / Innenbauteile
def add_first_node(line_wall_1, line_wall_2, area, lam_in, thick_in, rad_w, rad_c):
    LM(line_wall_1, line_air, left_matrix[line_air, line_wall_1])
    LM(line_wall_1, line_wall_2, - area * time_step * lam_in / thick_in / 0.75)
    LM(line_wall_1, line_int_wall_1, -rad_w * time_step)
    LM(line_wall_1, line_int_ceiling_1, -rad_c * time_step)
    LM(line_wall_1, line_wall_1, area * (wall_inside_capacity_density if lam_in==wall_inside_lyamda else
                                         roof_inside_capacity_density if lam_in==roof_inside_lyamda else
                                         floor_inside_capacity_density if lam_in==floor_inside_lyamda else 0.0)
       * thick_in * 0.5
       - left_matrix[line_wall_1, line_air]
       - left_matrix[line_wall_1, line_wall_2]
       - left_matrix[line_wall_1, line_int_wall_1]
       - left_matrix[line_wall_1, line_int_ceiling_1])

add_first_node(line_wall_n_1, line_wall_n_2, wall_area_n, wall_inside_lyamda, wall_inside_thickness, surf_rad_htc_int_wall_wall_n, surf_rad_htc_int_ceiling_wall_n)
add_first_node(line_wall_e_1, line_wall_e_2, wall_area_e, wall_inside_lyamda, wall_inside_thickness, surf_rad_htc_int_wall_wall_e, surf_rad_htc_int_ceiling_wall_e)
add_first_node(line_wall_s_1, line_wall_s_2, wall_area_s, wall_inside_lyamda, wall_inside_thickness, surf_rad_htc_int_wall_wall_s, surf_rad_htc_int_ceiling_wall_s)
add_first_node(line_wall_w_1, line_wall_w_2, wall_area_w, wall_inside_lyamda, wall_inside_thickness, surf_rad_htc_int_wall_wall_w, surf_rad_htc_int_ceiling_wall_w)
add_first_node(line_roof_1, line_roof_2, roof_area, roof_inside_lyamda, roof_inside_thickness, surf_rad_htc_int_wall_roof, surf_rad_htc_int_ceiling_roof)
add_first_node(line_floor_1, line_floor_2, floor_area, floor_inside_lyamda, floor_inside_thickness, surf_rad_htc_int_wall_floor, surf_rad_htc_int_ceiling_floor)

# Innenwand / -decke 1. Knoten
LM(line_int_wall_1, line_air, left_matrix[line_air, line_int_wall_1])
LM(line_int_wall_1, line_int_wall_2, - int_wall_area * time_step * int_wall_lyamda / int_wall_thickness / (0.125 + 0.0625))
# Kopplungen zu Glas / Rahmen / Wände / Dach / Boden / Decke
for tgt in [line_in_glazing_n, line_in_glazing_e, line_in_glazing_s, line_in_glazing_w,
            line_in_frame_n, line_in_frame_e, line_in_frame_s, line_in_frame_w,
            line_wall_n_1, line_wall_e_1, line_wall_s_1, line_wall_w_1, line_roof_1, line_floor_1]:
    LM(line_int_wall_1, tgt, left_matrix[tgt, line_int_wall_1])
LM(line_int_wall_1, line_int_ceiling_1, -surf_rad_htc_int_wall_int_ceiling * time_step)
LM(line_int_wall_1, line_int_wall_1,
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
   - left_matrix[line_int_wall_1, line_int_ceiling_1])

# Innen-Decke 1. Knoten
LM(line_int_ceiling_1, line_air, left_matrix[line_air, line_int_ceiling_1])
LM(line_int_ceiling_1, line_int_ceiling_2, - int_ceiling_area * time_step * int_ceiling_lyamda / int_ceiling_thickness / (0.125 + 0.0625))
for tgt in [line_in_glazing_n, line_in_glazing_e, line_in_glazing_s, line_in_glazing_w,
            line_in_frame_n, line_in_frame_e, line_in_frame_s, line_in_frame_w,
            line_wall_n_1, line_wall_e_1, line_wall_s_1, line_wall_w_1, line_roof_1, line_floor_1,
            line_int_wall_1]:
    LM(line_int_ceiling_1, tgt, left_matrix[tgt, line_int_ceiling_1] if tgt != line_int_wall_1 else left_matrix[line_int_wall_1, line_int_ceiling_1])
LM(line_int_ceiling_1, line_int_ceiling_1,
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
   - left_matrix[line_int_ceiling_1, line_int_wall_1])

# 2. Knoten Außenwände, Dach, Boden, Innenbauteile
def add_second_node(line2, line1, line3, area, lam_in, thick_in, cap_in):
    LM(line2, line1, left_matrix[line1, line2])
    LM(line2, line3, - area * time_step * 1.0 / (1.0 / lam_in * thick_in * 0.25 + 1.0 / (wall_outside_lyamda if area in [wall_area_n, wall_area_e, wall_area_s, wall_area_w] else
                                                                                         roof_outside_lyamda if area == roof_area else
                                                                                         floor_outside_lyamda) * (wall_outside_thickness if area in [wall_area_n, wall_area_e, wall_area_s, wall_area_w] else
                                                                                                                   roof_outside_thickness if area == roof_area else
                                                                                                                   floor_outside_thickness) * 0.25))
    LM(line2, line2, area * cap_in * thick_in * 0.5 - left_matrix[line2, line1] - left_matrix[line2, line3])

add_second_node(line_wall_n_2, line_wall_n_1, line_wall_n_3, wall_area_n, wall_inside_lyamda, wall_inside_thickness, wall_inside_capacity_density)
add_second_node(line_wall_e_2, line_wall_e_1, line_wall_e_3, wall_area_e, wall_inside_lyamda, wall_inside_thickness, wall_inside_capacity_density)
add_second_node(line_wall_s_2, line_wall_s_1, line_wall_s_3, wall_area_s, wall_inside_lyamda, wall_inside_thickness, wall_inside_capacity_density)
add_second_node(line_wall_w_2, line_wall_w_1, line_wall_w_3, wall_area_w, wall_inside_lyamda, wall_inside_thickness, wall_inside_capacity_density)

add_second_node(line_roof_2, line_roof_1, line_roof_3, roof_area, roof_inside_lyamda, roof_inside_thickness, roof_inside_capacity_density)
add_second_node(line_floor_2, line_floor_1, line_floor_3, floor_area, floor_inside_lyamda, floor_inside_thickness, floor_inside_capacity_density)

LM(line_int_wall_2, line_int_wall_1, left_matrix[line_int_wall_1, line_int_wall_2])
LM(line_int_wall_2, line_int_wall_3, - int_wall_area * time_step * 1.0 / (1.0 / int_wall_lyamda * int_wall_thickness * 0.125))
LM(line_int_wall_2, line_int_wall_2, int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125
   - left_matrix[line_int_wall_2, line_int_wall_1] - left_matrix[line_int_wall_2, line_int_wall_3])

LM(line_int_ceiling_2, line_int_ceiling_1, left_matrix[line_int_ceiling_1, line_int_ceiling_2])
LM(line_int_ceiling_2, line_int_ceiling_3, - int_ceiling_area * time_step * 1.0 / (1.0 / int_ceiling_lyamda * int_ceiling_thickness * 0.125))
LM(line_int_ceiling_2, line_int_ceiling_2, int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125
   - left_matrix[line_int_ceiling_2, line_int_ceiling_1] - left_matrix[line_int_ceiling_2, line_int_ceiling_3])

# 3. Knoten Außenwände / Dach / Boden / Innenbauteile
def add_third_node(line3, line2, line4, area, lam_out, thick_out, cap_out):
    LM(line3, line2, left_matrix[line2, line3])
    LM(line3, line4, - area * time_step * lam_out / thick_out / 0.75)
    LM(line3, line3, area * cap_out * thick_out * 0.5 - left_matrix[line3, line2] - left_matrix[line3, line4])

add_third_node(line_wall_n_3, line_wall_n_2, line_wall_n_4, wall_area_n, wall_outside_lyamda, wall_outside_thickness, wall_outside_capacity_density)
add_third_node(line_wall_e_3, line_wall_e_2, line_wall_e_4, wall_area_e, wall_outside_lyamda, wall_outside_thickness, wall_outside_capacity_density)
add_third_node(line_wall_s_3, line_wall_s_2, line_wall_s_4, wall_area_s, wall_outside_lyamda, wall_outside_thickness, wall_outside_capacity_density)
add_third_node(line_wall_w_3, line_wall_w_2, line_wall_w_4, wall_area_w, wall_outside_lyamda, wall_outside_thickness, wall_outside_capacity_density)

add_third_node(line_roof_3, line_roof_2, line_roof_4, roof_area, roof_outside_lyamda, roof_outside_thickness, roof_outside_capacity_density)
add_third_node(line_floor_3, line_floor_2, line_floor_4, floor_area, floor_outside_lyamda, floor_outside_thickness, floor_outside_capacity_density)

LM(line_int_wall_3, line_int_wall_2, left_matrix[line_int_wall_2, line_int_wall_3])
LM(line_int_wall_3, line_int_wall_4, - int_wall_area * time_step * 1.0 / (1.0 / int_wall_lyamda * int_wall_thickness * 0.125))
LM(line_int_wall_3, line_int_wall_3, int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125
   - left_matrix[line_int_wall_3, line_int_wall_2] - left_matrix[line_int_wall_3, line_int_wall_4])

LM(line_int_ceiling_3, line_int_ceiling_2, left_matrix[line_int_ceiling_2, line_int_ceiling_3])
LM(line_int_ceiling_3, line_int_ceiling_4, - int_ceiling_area * time_step * 1.0 / (1.0 / int_ceiling_lyamda * int_ceiling_thickness * 0.125))
LM(line_int_ceiling_3, line_int_ceiling_3, int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125
   - left_matrix[line_int_ceiling_3, line_int_ceiling_2] - left_matrix[line_int_ceiling_3, line_int_ceiling_4])

# 4. Knoten Außenschalen + Rand
def add_fourth_node(line4, line3, area, cap_out, thick_out):
    LM(line4, line3, left_matrix[line3, line4])
    LM(line4, line4, area * cap_out * thick_out * 0.5 + area * surf_htc_out * time_step - left_matrix[line4, line3])

add_fourth_node(line_wall_n_4, line_wall_n_3, wall_area_n, wall_outside_capacity_density, wall_outside_thickness)
add_fourth_node(line_wall_e_4, line_wall_e_3, wall_area_e, wall_outside_capacity_density, wall_outside_thickness)
add_fourth_node(line_wall_s_4, line_wall_s_3, wall_area_s, wall_outside_capacity_density, wall_outside_thickness)
add_fourth_node(line_wall_w_4, line_wall_w_3, wall_area_w, wall_outside_capacity_density, wall_outside_thickness)
add_fourth_node(line_roof_4, line_roof_3, roof_area, roof_outside_capacity_density, roof_outside_thickness)
add_fourth_node(line_floor_4, line_floor_3, floor_area, floor_outside_capacity_density, floor_outside_thickness)

LM(line_int_wall_4, line_int_wall_3, left_matrix[line_int_wall_3, line_int_wall_4])
LM(line_int_wall_4, line_int_wall_4, int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 - left_matrix[line_int_wall_4, line_int_wall_3])

LM(line_int_ceiling_4, line_int_ceiling_3, left_matrix[line_int_ceiling_3, line_int_ceiling_4])
LM(line_int_ceiling_4, line_int_ceiling_4, int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 - left_matrix[line_int_ceiling_4, line_int_ceiling_3])

# – END Matrixdefinitionen –

# ------------------------------
# 13) Inverse Matrix
# ------------------------------
inverse_matrix = np.linalg.inv(left_matrix)

# ------------------------------
# 14) Anzahl Stunden
# ------------------------------
weather_file_size = ambient_temp.shape[0]

# ------------------------------
# 15) Initialwerte / Outputs
# ------------------------------
initial_temperatures = np.full((N,), 20.0, dtype=float)
output_temperatures = np.zeros((8760, N), dtype=float)
output_heating_power = np.zeros(8760, dtype=float)
output_cooling_power = np.zeros(8760, dtype=float)
output_lighting_electricity = np.zeros(8760, dtype=float)
output_equipment_electricity = np.zeros(8760, dtype=float)

# ------------------------------
# 16) Zeitschleife
# ------------------------------
hour_counter = 1  # MATLAB startet effektiv bei 2 wegen Interpolation (t-1)
# Python-Indexierung: wir nutzen hour_counter als "MATLAB-Zähler" und rechnen beim Zugriff -1

for day in range(1, weather_file_size // 24 + 1):
    hour = 1
    if day == 1 and hour == 1:
        hour += 1
        hour_counter += 1
    while hour <= 24:
        for internal_time_step in range(1, int(3600 / time_step) + 1):  # 12 Steps bei 5 min
            right_matrix = np.zeros((N,), dtype=float)

            # Interpolation Wetterdaten (zwischen Stunde-1 und Stunde)
            hc = hour_counter
            hcm1 = hc - 1
            alpha = internal_time_step * time_step / 3600.0

            # Hilfszugriffe (Python 0-basiert)
            Ta0 = ambient_temp[hcm1 - 1]; Ta1 = ambient_temp[hc - 1]
            SFn0 = sun_flux_north[hcm1 - 1]; SFn1 = sun_flux_north[hc - 1]
            SFe0 = sun_flux_east[hcm1 - 1];  SFe1 = sun_flux_east[hc - 1]
            SFs0 = sun_flux_south[hcm1 - 1]; SFs1 = sun_flux_south[hc - 1]
            SFw0 = sun_flux_west[hcm1 - 1];  SFw1 = sun_flux_west[hc - 1]
            SFr0 = sun_flux_roof[hcm1 - 1];  SFr1 = sun_flux_roof[hc - 1]
            D0 = diff_radiation[hcm1 - 1];   D1 = diff_radiation[hc - 1]
            G0 = global_radiation[hcm1 - 1]; G1 = global_radiation[hc - 1]

            interpolated_amb_temp = Ta0 + alpha * (Ta1 - Ta0)
            interpolated_sun_flux_n = SFn0 + alpha * (SFn1 - SFn0)
            interpolated_sun_flux_e = SFe0 + alpha * (SFe1 - SFe0)
            interpolated_sun_flux_s = SFs0 + alpha * (SFs1 - SFs0)
            interpolated_sun_flux_w = SFw0 + alpha * (SFw1 - SFw0)
            interpolated_sun_flux_r = SFr0 + alpha * (SFr1 - SFr0)
            interpolated_diff_rad   = D0   + alpha * (D1   - D0)
            interpolated_global_rad = G0   + alpha * (G1   - G0)
            interpolated_shading_flux = (0.5 * interpolated_diff_rad + 0.2 * 0.5 * interpolated_global_rad)

            # Bodentemp / Unbeheizt (Grad-Cosinus mit Gradargument)
            interpolated_ground_temp   = 15 - 5 * np.cos(np.deg2rad((hc - 31 * 2 * 24) * 360 / 8760.0))
            interpolated_unheated_temp = 18 - 3 * np.cos(np.deg2rad((hc - 31 * 2 * 24) * 360 / 8760.0))

            # Verschattung
            shading_value_shaded_windows_north = 1.0
            shading_value_shaded_windows_east  = 1.0
            shading_value_shaded_windows_south = 1.0
            shading_value_shaded_windows_west  = 1.0

            if initial_temperatures[line_air] > 23.0 and interpolated_shading_flux > 200.0:
                sv = shading_g_value_reduction_factor
                shading_value_shaded_windows_north = sv
                shading_value_shaded_windows_east  = sv
                shading_value_shaded_windows_south = sv
                shading_value_shaded_windows_west  = sv

            shading_value_unshaded_windows_north = 1.0
            shading_value_unshaded_windows_east  = 1.0
            shading_value_unshaded_windows_south = 1.0
            shading_value_unshaded_windows_west  = 1.0

            if initial_temperatures[line_air] > 23.0:
                if interpolated_sun_flux_n > 200.0: shading_value_unshaded_windows_north = shading_g_value_reduction_factor
                if interpolated_sun_flux_e > 200.0: shading_value_unshaded_windows_east  = shading_g_value_reduction_factor
                if interpolated_sun_flux_s > 200.0: shading_value_unshaded_windows_south = shading_g_value_reduction_factor
                if interpolated_sun_flux_w > 200.0: shading_value_unshaded_windows_west  = shading_g_value_reduction_factor

            total_sun_heat_gain = (
                shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n +
                shading_value_shaded_windows_north  * shaded_glazing_area_n   * interpolated_shading_flux +
                shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e +
                shading_value_shaded_windows_east   * shaded_glazing_area_e   * interpolated_shading_flux +
                shading_value_unshaded_windows_south* unshaded_glazing_area_s * interpolated_sun_flux_s +
                shading_value_shaded_windows_south  * shaded_glazing_area_s   * interpolated_shading_flux +
                shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w +
                shading_value_shaded_windows_west   * shaded_glazing_area_w   * interpolated_shading_flux
            )

            # Interne Lasten dieser Stunde (hour ist 1..24 -> Index hour-1)
            occ = occupancy_schedule[hour - 1]
            lig = lighting_schedule[hour - 1]
            eqp = equipment_schedule[hour - 1]

            int_heat_gain = occ * occupancy_power + eqp * equipment_power

            if lig > 0.0:
                # Beleuchtungsnachschub je Fassadenseite, wenn mittlere Fensterbestrahlung < 15 W/m2
                if (shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n +
                    shading_value_shaded_windows_north  * shaded_glazing_area_n   * interpolated_shading_flux) / glazing_area_n < 15.0:
                    int_heat_gain += lig * lighting_power * lighting_north_side
                if (shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e +
                    shading_value_shaded_windows_east   * shaded_glazing_area_e   * interpolated_shading_flux) / glazing_area_e < 15.0:
                    int_heat_gain += lig * lighting_power * lighting_east_side
                if (shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s +
                    shading_value_shaded_windows_south   * shaded_glazing_area_s   * interpolated_shading_flux) / glazing_area_s < 15.0:
                    int_heat_gain += lig * lighting_power * lighting_south_side
                if (shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w +
                    shading_value_shaded_windows_west   * shaded_glazing_area_w   * interpolated_shading_flux) / glazing_area_w < 15.0:
                    int_heat_gain += lig * lighting_power * lighting_west_side

            # Rechte Seite (Right-Hand-Vector)
            rm = right_matrix  # Alias

            # Luft
            rm[line_air] = (
                building_height * floor_area * 1006 * 1.185 * initial_temperatures[line_air]
                + wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp
                + thermal_bridges * time_step * interpolated_amb_temp
                + (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp
                + int_heat_gain_to_air_coef * int_heat_gain * time_step
            )

            # Innen-Glas n/e/s/w
            rm[line_in_glazing_n] = int_heat_gain_to_glazing_n_coef * int_heat_gain * time_step + time_step * sun_heat_gain_to_inside_glazing * (
                shading_value_unshaded_windows_north * unshaded_glazing_area_n * interpolated_sun_flux_n +
                shading_value_shaded_windows_north   * shaded_glazing_area_n   * interpolated_shading_flux
            )
            rm[line_in_glazing_e] = int_heat_gain_to_glazing_e_coef * int_heat_gain * time_step + time_step * sun_heat_gain_to_inside_glazing * (
                shading_value_unshaded_windows_east * unshaded_glazing_area_e * interpolated_sun_flux_e +
                shading_value_shaded_windows_east   * shaded_glazing_area_e   * interpolated_shading_flux
            )
            rm[line_in_glazing_s] = int_heat_gain_to_glazing_s_coef * int_heat_gain * time_step + time_step * sun_heat_gain_to_inside_glazing * (
                shading_value_unshaded_windows_south * unshaded_glazing_area_s * interpolated_sun_flux_s +
                shading_value_shaded_windows_south   * shaded_glazing_area_s   * interpolated_shading_flux
            )
            rm[line_in_glazing_w] = int_heat_gain_to_glazing_w_coef * int_heat_gain * time_step + time_step * sun_heat_gain_to_inside_glazing * (
                shading_value_unshaded_windows_west * unshaded_glazing_area_w * interpolated_sun_flux_w +
                shading_value_shaded_windows_west   * shaded_glazing_area_w   * interpolated_shading_flux
            )

            # Außen-Glas n/e/s/w
            for l_out, area, sf in [
                (line_out_glazing_n, glazing_area_n, interpolated_sun_flux_n),
                (line_out_glazing_e, glazing_area_e, interpolated_sun_flux_e),
                (line_out_glazing_s, glazing_area_s, interpolated_sun_flux_s),
                (line_out_glazing_w, glazing_area_w, interpolated_sun_flux_w),
            ]:
                rm[l_out] = (
                    time_step * sun_heat_gain_to_outside_glazing * (
                        (shading_value_unshaded_windows_north if l_out==line_out_glazing_n else
                         shading_value_unshaded_windows_east  if l_out==line_out_glazing_e else
                         shading_value_unshaded_windows_south if l_out==line_out_glazing_s else
                         shading_value_unshaded_windows_west) *
                        (unshaded_glazing_area_n if l_out==line_out_glazing_n else
                         unshaded_glazing_area_e if l_out==line_out_glazing_e else
                         unshaded_glazing_area_s if l_out==line_out_glazing_s else
                         unshaded_glazing_area_w) * sf
                        +
                        (shading_value_shaded_windows_north if l_out==line_out_glazing_n else
                         shading_value_shaded_windows_east  if l_out==line_out_glazing_e else
                         shading_value_shaded_windows_south if l_out==line_out_glazing_s else
                         shading_value_shaded_windows_west) *
                        (shaded_glazing_area_n if l_out==line_out_glazing_n else
                         shaded_glazing_area_e if l_out==line_out_glazing_e else
                         shaded_glazing_area_s if l_out==line_out_glazing_s else
                         shaded_glazing_area_w) * interpolated_shading_flux
                    ) + interpolated_amb_temp * area * surf_htc_out * time_step
                )

            # Innen-Rahmen n/e/s/w
            rm[line_in_frame_n] = int_heat_gain_to_frame_n_coef * int_heat_gain * time_step
            rm[line_in_frame_e] = int_heat_gain_to_frame_e_coef * int_heat_gain * time_step
            rm[line_in_frame_s] = int_heat_gain_to_frame_s_coef * int_heat_gain * time_step
            rm[line_in_frame_w] = int_heat_gain_to_frame_w_coef * int_heat_gain * time_step

            # Außen-Rahmen n/e/s/w (0.8*Strahlung + Konvektion)
            rm[line_out_frame_n] = (unshaded_frame_area_n * interpolated_sun_flux_n + shaded_frame_area_n * interpolated_shading_flux) * 0.8 * time_step + interpolated_amb_temp * frame_area_n * surf_htc_out * time_step
            rm[line_out_frame_e] = (unshaded_frame_area_e * interpolated_sun_flux_e + shaded_frame_area_e * interpolated_shading_flux) * 0.8 * time_step + interpolated_amb_temp * frame_area_e * surf_htc_out * time_step
            rm[line_out_frame_s] = (unshaded_frame_area_s * interpolated_sun_flux_s + shaded_frame_area_s * interpolated_shading_flux) * 0.8 * time_step + interpolated_amb_temp * frame_area_s * surf_htc_out * time_step
            rm[line_out_frame_w] = (unshaded_frame_area_w * interpolated_sun_flux_w + shaded_frame_area_w * interpolated_shading_flux) * 0.8 * time_step + interpolated_amb_temp * frame_area_w * surf_htc_out * time_step

            # 1. Knoten Außenwände/Dach/Boden (Energiespeicher + interne Lastanteile)
            rm[line_wall_n_1] = wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_n_1] + int_heat_gain_to_wall_n_coef * int_heat_gain * time_step
            rm[line_wall_e_1] = wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_e_1] + int_heat_gain_to_wall_e_coef * int_heat_gain * time_step
            rm[line_wall_s_1] = wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_s_1] + int_heat_gain_to_wall_s_coef * int_heat_gain * time_step
            rm[line_wall_w_1] = wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_w_1] + int_heat_gain_to_wall_w_coef * int_heat_gain * time_step
            rm[line_roof_1]   = roof_area   * roof_inside_capacity_density   * roof_inside_thickness   * 0.5 * initial_temperatures[line_roof_1]   + int_heat_gain_to_roof_coef  * int_heat_gain * time_step
            rm[line_floor_1]  = floor_area  * floor_inside_capacity_density  * floor_inside_thickness  * 0.5 * initial_temperatures[line_floor_1]  + int_heat_gain_to_floor_coef * int_heat_gain * time_step

            # Innenbauteile 1. Knoten inkl. solarer Anteile
            rm[line_int_wall_1] = int_wall_area * int_wall_capacity_density * int_wall_thickness * 0.125 * initial_temperatures[line_int_wall_1] + \
                                   sun_heat_gain_to_int_wall * total_sun_heat_gain * time_step + \
                                   int_heat_gain_to_int_wall_coef * int_heat_gain * time_step
            rm[line_int_ceiling_1] = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures[line_int_ceiling_1] + \
                                     sun_heat_gain_to_int_ceiling * total_sun_heat_gain * time_step + \
                                     int_heat_gain_to_int_ceiling_coef * int_heat_gain * time_step

            # 2. Knoten
            rm[line_wall_n_2] = wall_area_n * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_n_2]
            rm[line_wall_e_2] = wall_area_e * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_e_2]
            rm[line_wall_s_2] = wall_area_s * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_s_2]
            rm[line_wall_w_2] = wall_area_w * wall_inside_capacity_density * wall_inside_thickness * 0.5 * initial_temperatures[line_wall_w_2]
            rm[line_roof_2]   = roof_area   * roof_inside_capacity_density   * roof_inside_thickness   * 0.5 * initial_temperatures[line_roof_2]
            rm[line_floor_2]  = floor_area  * floor_inside_capacity_density  * floor_inside_thickness  * 0.5 * initial_temperatures[line_floor_2]
            rm[line_int_wall_2]    = int_wall_area    * int_wall_capacity_density    * int_wall_thickness    * 0.125 * initial_temperatures[line_int_wall_2]
            rm[line_int_ceiling_2] = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures[line_int_ceiling_2]

            # 3. Knoten
            rm[line_wall_n_3] = wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_n_3]
            rm[line_wall_e_3] = wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_e_3]
            rm[line_wall_s_3] = wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_s_3]
            rm[line_wall_w_3] = wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_w_3]
            rm[line_roof_3]   = roof_area   * roof_outside_capacity_density  * roof_outside_thickness * 0.5 * initial_temperatures[line_roof_3]
            rm[line_floor_3]  = floor_area  * floor_outside_capacity_density * floor_outside_thickness* 0.5 * initial_temperatures[line_floor_3]
            rm[line_int_wall_3]    = int_wall_area    * int_wall_capacity_density    * int_wall_thickness    * 0.125 * initial_temperatures[line_int_wall_3]
            rm[line_int_ceiling_3] = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures[line_int_ceiling_3]

            # 4. Knoten Außen mit Randbedingungen (Konvektion + Strahlung auf außen)
            rm[line_wall_n_4] = wall_area_n * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_n_4] + \
                                interpolated_amb_temp * surf_htc_out * wall_area_n * time_step + 0.8 * interpolated_sun_flux_n * wall_area_n * time_step
            rm[line_wall_e_4] = wall_area_e * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_e_4] + \
                                interpolated_amb_temp * surf_htc_out * wall_area_e * time_step + 0.8 * interpolated_sun_flux_e * wall_area_e * time_step
            rm[line_wall_s_4] = wall_area_s * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_s_4] + \
                                interpolated_amb_temp * surf_htc_out * wall_area_s * time_step + 0.8 * interpolated_sun_flux_s * wall_area_s * time_step
            rm[line_wall_w_4] = wall_area_w * wall_outside_capacity_density * wall_outside_thickness * 0.5 * initial_temperatures[line_wall_w_4] + \
                                interpolated_amb_temp * surf_htc_out * wall_area_w * time_step + 0.8 * interpolated_sun_flux_w * wall_area_w * time_step
            rm[line_roof_4]   = roof_area   * roof_outside_capacity_density  * roof_outside_thickness * 0.5 * initial_temperatures[line_roof_4] + \
                                interpolated_amb_temp * surf_htc_out * roof_area * time_step + 0.8 * interpolated_sun_flux_r * roof_area * time_step
            rm[line_floor_4]  = floor_area  * floor_outside_capacity_density * floor_outside_thickness* 0.5 * initial_temperatures[line_floor_4] + \
                                interpolated_ground_temp * surf_htc_out * floor_area * time_step
            rm[line_int_wall_4]    = int_wall_area    * int_wall_capacity_density    * int_wall_thickness    * 0.125 * initial_temperatures[line_int_wall_4]
            rm[line_int_ceiling_4] = int_ceiling_area * int_ceiling_capacity_density * int_ceiling_thickness * 0.125 * initial_temperatures[line_int_ceiling_4]

            # Zustand updaten
            initial_temperatures = inverse_matrix @ rm

            # Heizen / Kühlen (5 Iterationen wie im MATLAB)
            heating_power = 0.0
            cooling_power = 0.0
            if initial_temperatures[line_air] < heating_setpoint:
                for _ in range(5):
                    heating_power += left_matrix[line_air, line_air] * (heating_setpoint - initial_temperatures[line_air]) / time_step
                    rm[line_air] = (
                        building_height * floor_area * 1006 * 1.185 * initial_temperatures[line_air]
                        + wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp
                        + thermal_bridges * time_step * interpolated_amb_temp
                        + (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp
                        + int_heat_gain_to_air_coef * int_heat_gain * time_step
                        + heating_power * time_step
                    )
                    initial_temperatures = inverse_matrix @ rm
            elif initial_temperatures[line_air] > cooling_setpoint:
                for _ in range(5):
                    cooling_power += left_matrix[line_air, line_air] * (cooling_setpoint - initial_temperatures[line_air]) / time_step
                    rm[line_air] = (
                        building_height * floor_area * 1006 * 1.185 * initial_temperatures[line_air]
                        + wall_against_unheated_u_value * wall_against_unheated_area * time_step * interpolated_unheated_temp
                        + thermal_bridges * time_step * interpolated_amb_temp
                        + (infiltration_rate + air_ventilation_rate * (1 - heat_exchanger_efficiency)) * 1006 * 1.185 * time_step * interpolated_amb_temp
                        + int_heat_gain_to_air_coef * int_heat_gain * time_step
                        + cooling_power * time_step
                    )
                    initial_temperatures = inverse_matrix @ rm

            # Output aufs letzte Jahr mappen (wie im MATLAB)
            if hc > weather_file_size - 8760:
                idx = hc - weather_file_size + 8760 - 1  # 0-basiert
                output_heating_power[idx]  += heating_power * time_step / 3600.0
                output_cooling_power[idx]  += cooling_power * time_step / 3600.0
                output_lighting_electricity[idx] += (int_heat_gain - occ * occupancy_power - eqp * equipment_power) * time_step / 3600.0
                output_equipment_electricity[idx] += eqp * equipment_power * time_step / 3600.0

        if hour_counter > weather_file_size - 8760:
            idx = hour_counter - weather_file_size + 8760 - 1
            output_temperatures[idx, :] = initial_temperatures

        hour += 1
        hour_counter += 1

# Summen (MWh)
output_total_heating_power_sum   = np.sum(output_heating_power)   / 1e6
output_total_cooling_power_sum   = np.sum(output_cooling_power)   / 1e6
output_total_lighting_power_sum  = np.sum(output_lighting_electricity) / 1e6
output_total_equipment_power_sum = np.sum(output_equipment_electricity) / 1e6

print("output_total_heating_power_sum [MWh]  =", output_total_heating_power_sum)
print("output_total_cooling_power_sum [MWh]  =", output_total_cooling_power_sum)
print("output_total_lighting_power_sum [MWh] =", output_total_lighting_power_sum)
print("output_total_equipment_power_sum [MWh]=", output_total_equipment_power_sum)

# Ergebnisse als MAT speichern (ähnlich zu MATLAB)
savemat('python_ref_results.mat', {
    'output_temperatures': output_temperatures,
    'output_heating_power': output_heating_power,
    'output_cooling_power': output_cooling_power,
    'output_lighting_electricity': output_lighting_electricity,
    'output_equipment_electricity': output_equipment_electricity,
    'left_matrix': left_matrix
}, do_compression=False)
