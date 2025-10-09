import numpy as np

# Load reusults from the .npz file
results = np.load("adapters/py_out.npz")
res_temp = results['output_temperatures']
# res_output_heating_power = results['output_heating_power']
# res_output_cooling_power = results['output_cooling_power']
# res_output_lighting_power = results['output_lighting_power']
# res_output_equipment_power = results['output_equipment_power']
# print(f"temp: {temp}")