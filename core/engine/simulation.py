from pathlib import Path

"""
Orchestrates a simulation run. Takes parameter values from JSON file and weatherdata and gives it to the R-C-modell.
Runs Engine and returns simulationsresults as an objekt back to the ui. 
"""

class StartSimulation:

    def __init__(self) -> None:
        pass

    def start(self, project_id, cfg_eval, weather_df):
        pass
    
    def status(self, project_id, run_id):
        pass
        
    def results(self, project_id, run_id):
        pass

    