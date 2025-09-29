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
A_ref = np.asarray(ref['left_matrix'])  # left matrix A

gpt_path = here / "python_ref_results.mat"  # Path to the Python .mat file
gpt_py = loadmat(gpt_path, simplify_cells=True)  # Load the Python .mat file

T_gpt_py = gpt_py['output_temperatures']  # temperature python [°C], shape (8760, 49)
Qh_gpt_py = gpt_py['output_heating_power'].ravel()  # heating power python [MWh], shape (1, )
Qc_gpt_py = gpt_py['output_cooling_power'].ravel()  # cooling power
El_gpt_py = gpt_py['output_lighting_electricity'].ravel()  # lighting electricity python [MWh], shape (1, )
Eq_gpt_py = gpt_py['output_equipment_electricity'].ravel()  # equipment electricity python [MWh], shape (1, )
A_gpt_py = gpt_py['left_matrix']  # left matrix A


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

def MWh(x): return float(np.sum(x)/1e6)  # sum in MWh


print("=== comparison matlab vs python ===")
print(f"Temperature shape: py={T_py.shape}, ref={T_ref.shape}")
print(f"Matrix-shape     : py={A_py.shape}, ref={A_ref.shape}")

Qc_py_comp = -Qc_py if np.mean(Qc_ref) < 0 else Qc_py  # ensure same sign convention for cooling power

# compare temperatures
t_rmse = rmse(T_py[:, 0], T_ref[:, 0]) # compare only first column (air temperature)

# compare heating and cooling power hourly
qh_rmse = rmse(Qh_py, Qh_ref)
qc_rmse = rmse(Qc_py, Qc_ref)

print(f"RMSE T_air [K]             : {t_rmse:.6f} K")
print(f"RMSE Q_h [Wh]              : {qh_rmse:.6f} Wh")
print(f"RMSE Q_c [Wh]              : {qc_rmse:.6f} Wh")
print(f"Σheating [MWh] py vs ref   : {MWh(Qh_py):.6f}  vs  {MWh(Qh_ref):.6f}")
print(f"Σcooling [MWh] py vs ref   : {MWh(Qc_py_comp):.6f}  vs  {MWh(Qc_ref):.6f}")
print(f"Σlight [MWh] py vs ref     : {MWh(El_py):.6f}   vs  {MWh(El_ref):.6f}")
print(f"Σequipment [MWh] py vs ref : {MWh(Eq_py):.6f}   vs  {MWh(Eq_ref):.6f}")

# compare left matrix A
mat_equal = np.allclose(A_py, A_ref, atol=1e-12, rtol=1e-12)
print(f"left_matrix allclose       : {mat_equal}")

print("=== comparison python vs python_GPT vs matlab ===")
print(f"Temperature shape: gpt py={T_gpt_py.shape}, py={T_py.shape}, ref={T_ref.shape}")
print(f"Matrix-shape     : gpt py={A_gpt_py.shape}, py={A_py.shape}, ref={A_ref.shape}")

Qc_gpt_py_comp = -Qc_gpt_py if np.mean(Qc_ref) < 0 else Qc_gpt_py  # ensure same sign convention for cooling power

# compare temperatures
t_gpt_rmse = rmse(T_gpt_py[:, 0], T_ref[:, 0]) # compare only first column (air temperature)

# compare heating and cooling power hourly
qh_gpt_rmse = rmse(Qh_gpt_py, Qh_ref)
qc_gpt_rmse = rmse(Qc_gpt_py, Qc_ref)

print(f"RMSE gpt T_air [K]             : {t_gpt_rmse:.6f} K")
print(f"RMSE gpt Q_h [Wh]              : {qh_gpt_rmse:.6f} Wh")
print(f"RMSE gpt Q_c [Wh]              : {qc_gpt_rmse:.6f} Wh")
print(f"Σgpt heating [MWh] gpt_py vs ref   : {MWh(Qh_gpt_py):.6f}     vs  {MWh(Qh_ref):.6f} ")
print(f"Σgpt cooling [MWh] gpt_py vs ref   : {MWh(Qc_gpt_py_comp):.6f}      vs  {MWh(Qc_ref):.6f}")
print(f"Σgpt light [MWh] gpt_py vs ref     : {MWh(El_gpt_py):.6f}      vs  {MWh(El_ref):.6f}")
print(f"Σgpt equipment [MWh] gpt_py vs ref : {MWh(Eq_gpt_py):.6f}     vs  {MWh(Eq_ref):.6f}")

# compare left matrix A
mat_gpt_equal = np.allclose(A_gpt_py, A_ref, atol=1e-12, rtol=1e-12)
print(f"gpt left_matrix allclose       : {mat_gpt_equal}")



# strong asserts
assert t_rmse < 1e-3, f"T_air RMSE to high: {t_rmse:.3e}"
assert qh_rmse < 1e-2, f"Q_h RMSE to high: {qh_rmse:.3e}"
assert qc_rmse < 1e-2, f"Q_c RMSE to high: {qc_rmse:.3e}"
assert np.isclose(MWh(El_py), MWh(El_ref), atol=1e-6, rtol=1e-5), "Σlight differs"
assert np.isclose(MWh(Eq_py), MWh(Eq_ref), atol=1e-6, rtol=1e-5), "Σequipment differs"
assert mat_equal, "left_matrix differs"
print("all tests passed")