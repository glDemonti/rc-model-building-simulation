import copy
from dataclasses import dataclass
import pandas as pd
from pathlib import Path
import json
import io
import zipfile

@dataclass
class RunReport:
    ok: bool
    run_id: str
    message: str
    
class ConfigFacade:
    """
    
    """
    def __init__(
        self, config_repo, engine, result, evaluator=None, validator=None, mapper=None, analytics=None,
        weather_service=None, measure_service=None, weather_repo=None, measure_repo=None,
        config_file_path=None, result_file_path=None
    ):
        self._config_repo = config_repo
        self._engine = engine
        self._evaluator = evaluator
        self._validator = validator
        self._mapper = mapper
        self._result = result
        self._analytics = analytics
        self._weather_service = weather_service
        self._measure_service = measure_service
        self._weather_repo = weather_repo
        self._measure_repo = measure_repo
        self._config_file_path = config_file_path  # Path to config JSON file
        self._result_file_path = result_file_path  # Path to result parquet file

    def load_config(self, project_id) -> dict:
        cfg = self._config_repo.read_raw()
        return cfg

    def save_config(self, project_id, cfg):
        # Evaluate expressions -> values
        cfg_copy = copy.deepcopy(cfg)
        cfg_evaluated, errors = self._evaluator.evaluate_cfg(cfg_copy)
        if errors:
            return False, "Fehler bei der Auswertung: " + "; ".join(errors)
              
       # save
        try:
            self._config_repo.write_raw(cfg_evaluated)
            return True, "Gespeichert"
        except Exception as e:
            return False, f"Speichern fehlgeschlagen: {e}"

    def get_context(self, project_id: str, variant_id: str):
        if self._analytics is None:
            raise RuntimeError("AnalyticsService not configured in ConfigFacade.")
        
        context = self._analytics.compute_all(project_id, variant_id)
        return context


    def update_weather_file(self, temp_path: str, original_name: str) -> None:
        """
        Updates the weather data file in the repository by copying it from a temporary location.
        Also saves the original name of the uploaded file.
        """
        self._weather_repo.write_raw(Path(temp_path))
        self._weather_repo.save_original_name(original_name)
        self._weather_service.process_and_store_weather()


    def update_measurement_file(self, temp_path: str, original_name: str):
        """
        Updates the measurement data file in the repository by copying it from a temporary location.

        """
        self._measure_repo.write_raw(Path(temp_path))
        self._measure_repo.save_original_name(original_name)

    def run_simulation(self, project_id: str, variant_id: str, *, force: bool = False) -> RunReport:
        """quick and dirty implementation of start simulation
        """
        cfg = self._config_repo.read_raw()

        rc_params = self._mapper.to_model_params(cfg)
        weather_df = self._weather_service.load_weather()

        # start simulation
        df_raw = self._engine.run(rc_params, weather_df)
        
        # save result
        self._result.save_raw(df_raw)

        # return f"Simulation for project {project_id} started."
        return RunReport(
            ok=True,
            run_id="latest",
            message=f"Simulation for project {project_id} and variant {variant_id} completed successfully."
        )
   
    def get_summary(self, project_id: str, variant_id: str, ):
        result = self._analytics.compute_all(project_id, variant_id)
        return result["summary"]
    
    def get_timeseries(self, project_id: str, variant_id: str):
        result = self._analytics.compute_all(project_id, variant_id)
        return result["timeseries"]

    def get_measurements(self):
        measurement = self._measure_service.process_and_store_measurements()
        return measurement
    
    def get_monthly_timeseries(self, project_id: str, variant_id: str):
        result = self._analytics.compute_all(project_id, variant_id)
        return result["monthly_timeseries"]
    
    def download_raw_results(self) -> bytes:
        data = self._result.load_raw_bites()
        if data is None:
            raise FileNotFoundError("No raw results found to download.")
        return data
    
    def download_all_results_zip(self, variant_id: str) -> bytes:
        """
        Creates a ZIP file containing:
        - Parameter JSON file (config_{variant_id}.json)
        - Raw results as parquet (raw_results_{variant_id}.parquet)
        - Raw results as CSV (raw_results_{variant_id}.csv)
        
        Reads files from the project directory.
        
        Args:
            variant_id: The variant identifier (e.g., "A" or "B")
            
        Returns:
            bytes: The ZIP file as bytes
        """
        # Create a BytesIO object to hold the zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add config JSON file if it exists
            if self._config_file_path and Path(self._config_file_path).exists():
                config_filename = f"config_{variant_id}.json"
                config_path = Path(self._config_file_path)
                zip_file.write(config_path, arcname=config_filename)
            
            # Add results as parquet if it exists
            if self._result_file_path and Path(self._result_file_path).exists():
                parquet_filename = f"raw_results_{variant_id}.parquet"
                result_path = Path(self._result_file_path)
                zip_file.write(result_path, arcname=parquet_filename)
                
                # Also add results as CSV by reading parquet and converting
                try:
                    df = pd.read_parquet(result_path)
                    csv_filename = f"raw_results_{variant_id}.csv"
                    csv_buffer = io.BytesIO()
                    df.to_csv(csv_buffer, index=False)
                    zip_file.writestr(csv_filename, csv_buffer.getvalue())
                except Exception as e:
                    # If conversion fails, just skip the CSV
                    pass
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()