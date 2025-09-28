import numpy as np
from scipy.io import loadmat
from pathlib import Path
import os

# Determine the path to the directory containing this script
try:
    here = Path(__file__).resolve().parent  # Path to the folder where this script is located
except NameError:
    here = Path.cwd()  # If __file__ is not defined, use the current working directory

# load matlab refernce results
ref_path = here / "matlab_ref_results.mat"    # Path to the MATLAB .mat file
ref = loadmat(ref_path, simplify_cells=True)  # Load the MATLAB .mat file

T_ref = np.asarray(ref['output_temperatures'])  # temperature reference [°C], shape (8760, 49)
Qh_ref = np.asarray(ref['output_heating_power']).ravel()  # heating power reference [MWh], shape (1, )
Qc_ref = np.asarray(ref['output_cooling_power']).ravel()  # cooling power reference [MWh], shape (1, )
El_ref = np.asarray(ref['output_lighting_electricity']).ravel()  # lighting electricity reference [MWh], shape (1, )
Eq_ref = np.asarray(ref['output_equipment_electricity']).ravel()  # equipment electricity reference [MWh], shape (1, )
A = np.asarray(ref['left_matrix'])  # left matrix A

py = np.load("py_out.npz")
T_py = py['output_temperatures']  # temperature python [°C], shape (8760, 49)
Qh_py = py['output_heating_power'].ravel()  # heating power python [MWh], shape (1, )
Qc_py = py['output_cooling_power'].ravel()  # cooling power python [MWh], shape (1, )
El_py = py['output_lighting_electricity'].ravel()  # lighting electricity python [MWh], shape (1, )
Eq_py = py['output_equipment_electricity'].ravel()  # equipment electricity python [MWh], shape (1, )
A_py = py['left_matrix']  # left matrix A

# tolerance for comparison
ATOL_T = 1e-3  # absolute tolerance for temperature comparison [K]
RTOL_T = 5e-5  # relative tolerance for temperature comparison [%]
ATOL_Wh = 1e-2  # absolute tolerance for power comparison [MWh]
RTOL_Wh = 1e-5  # relative tolerance for power comparison [%]

def rmse(a,b):
    d = np.asarray(a) - np.asarray(b)
    return float(np.sqrt(np.mean(d*d)))

# compare temperatures
t_rmse = rmse(T_py[:,0], T_ref[:,0])
print(f"RMSE T_air = {t_rmse:.6f} K")

# compare heating and cooling power hourly
qh_rmse = rmse(Qh_py, Qh_ref)
qc_rmse = rmse(Qc_py, Qc_ref)
print(f"RMSE Q_h (Wh) = {qh_rmse:.6f}")
print(f"RMSE Q_c (Wh) = {qc_rmse:.6f}")

def MWh(x): return float(np.sum(x)/1e6)  # sum in MWh