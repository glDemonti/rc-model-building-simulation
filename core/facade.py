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
        cfg = self._config_repo.read_raw()
        self._weather_service.process_and_store_weather(cfg)


    def update_measurement_file(self, temp_path: str, original_name: str):
        """
        Updates the measurement data file in the repository by copying it from a temporary location.
        Returns a tuple (success, message, has_nan_warning)
        """
        self._measure_repo.write_raw(Path(temp_path))
        self._measure_repo.save_original_name(original_name)
        
        # Check for NaN values in data columns (exclude completely empty columns)
        try:
            df = self._measure_repo.read_raw()
            if df is not None:
                # Only check columns that have at least some data
                data_cols = df.select_dtypes(include=['number'])
                has_nan = False
                for col in data_cols.columns:
                    # If column has some valid data but also has NaN, that's a problem
                    if data_cols[col].notna().any() and data_cols[col].isna().any():
                        has_nan = True
                        break
                if has_nan:
                    return True, "Datei hochgeladen", True
        except Exception:
            pass
        
        return True, "Datei hochgeladen", False

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
    
    def get_measurement_filename(self):
        """
        Returns the original name of the uploaded measurement file.
        Returns None if no file has been uploaded yet.
        """
        return self._measure_repo.get_original_name()
    
    def get_monthly_timeseries(self, project_id: str, variant_id: str):
        result = self._analytics.compute_all(project_id, variant_id)
        return result["monthly_timeseries"]
    
    def get_measurement_summary(self, project_id: str, date_range: tuple = None, time_column: str = None):
        """
        Compute and return measurement statistics in summary format.
        Uses same metrics as simulation adapters for comparison.
        
        Args:
            project_id (str): Project identifier
            date_range (tuple): Optional (start_date, end_date) for filtering
            time_column (str): Optional name of time column
        
        Returns:
            pd.DataFrame: Summary statistics with columns: project_id, column_name, metric, value, unit
        """
        # Load config to get costs and building area
        cfg = self._config_repo.read_raw()
        costs_config = {
            "heating_price": cfg.get("economic_parameters", {}).get("heating_price", {}).get("value", 0),
            "cooling_price": cfg.get("economic_parameters", {}).get("cooling_price", {}).get("value", 0),
        }
        ebf_area = cfg.get("building_geometry", {}).get("enclosure", {}).get("ebf_area", {}).get("value", None)
        
        # Pass config to adapters via analytics service
        result = self._analytics.compute_measurements(
            project_id, 
            date_range=date_range, 
            time_column=time_column,
            costs_config=costs_config,
            ebf_area=ebf_area
        )
        return result["summary"]
    
    def download_raw_results(self) -> bytes:
        data = self._result.load_raw_bites()
        if data is None:
            raise FileNotFoundError("No raw results found to download.")
        return data
    
    def download_all_results_zip(self, variant_id: str, project_id: str = None) -> bytes:
        """
        Creates a ZIP file containing:
        - Parameter JSON file (config_{variant_id}.json)
        - Raw results as parquet (raw_results_{variant_id}.parquet)
        - Raw results as CSV (raw_results_{variant_id}.csv)
        - Processed timeseries CSV (timeseries_{variant_id}.csv)
        - Summary results with key metrics (summary_{variant_id}.csv)
        - Units description file (units_description.txt)
        
        Reads files from the project directory.
        
        Args:
            variant_id: The variant identifier (e.g., "A" or "B")
            project_id: Optional project ID for analytics
            
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
            
            # Add summary results if analytics is available
            if self._analytics and project_id:
                try:
                    context = self._analytics.compute_all(project_id, variant_id)
                    summary_df = context.get("summary")
                    
                    if summary_df is not None and not summary_df.empty:
                        summary_filename = f"summary_{variant_id}.csv"
                        summary_buffer = io.BytesIO()
                        summary_df.to_csv(summary_buffer, index=False)
                        zip_file.writestr(summary_filename, summary_buffer.getvalue())
                    
                    # Add timeseries data
                    timeseries_df = context.get("timeseries")
                    if timeseries_df is not None and not timeseries_df.empty:
                        timeseries_filename = f"timeseries_{variant_id}.csv"
                        timeseries_buffer = io.BytesIO()
                        timeseries_df.to_csv(timeseries_buffer, index=False)
                        zip_file.writestr(timeseries_filename, timeseries_buffer.getvalue())
                except Exception as e:
                    # If summary generation fails, just skip it
                    pass
            
            # Add units description file
            units_text = """Units Description for RC Model Results
=====================================

RAW RESULTS (Timeseries from r_c_modell.py):
- datetime: Timestamp
- temperature_outdoor_air: Outdoor air temperature [°C]
- temperature_air_room: Room air temperature [°C]
- temperature_in_glazing_north/east/south/west: Inside glazing temperatures [°C]
- temperature_out_glazing_north/east/south/west: Outside glazing temperatures [°C]
- temperature_in_frame_north/east/south/west: Inside frame temperatures [°C]
- temperature_out_frame_north/east/south/west: Outside frame temperatures [°C]
- temperature_wall_{n,e,s,w}_1..4: Wall layer node temperatures (north/east/south/west) [°C]
- temperature_roof_1..4: Roof layer node temperatures [°C]
- temperature_floor_1..4: Floor layer node temperatures [°C]
- temperature_int_wall_1..4: Internal wall node temperatures [°C]
- temperature_int_ceiling_1..4: Internal ceiling node temperatures [°C]
- output_heating_power: Heating power [W]
- output_cooling_power: Cooling power [W]
- output_lighting_electricity: Lighting electricity [W]
- output_equipment_electricity: Equipment electricity [W]

PROCESSED TIMESERIES (timeseries_*.csv):
- datetime: Timestamp
- variant_id: Variant identifier (A or B)
- temp_air_room: Room air temperature [°C]
- temp_outdoor_air: Outdoor air temperature [°C]
- heating_power: Heating power [W]
- cooling_power: Cooling power [W]

SUMMARY RESULTS:
Heating:
- energy_year: Annual heating energy demand [kWh]
- energy_specific: Specific heating energy demand [kWh/m²]
- power_max: Maximum heating power [kW]
- load_specific: Specific heating load [W/m²]
- costs_year: Annual heating costs [CHF]
- co2_year: Annual CO2 emissions from heating [kg CO2]

Cooling:
- energy_year: Annual cooling energy demand [kWh]
- energy_specific: Specific cooling energy demand [kWh/m²]
- power_max: Maximum cooling power [kW]
- load_specific: Specific cooling load [W/m²]
- costs_year: Annual cooling costs [CHF]
- co2_year: Annual CO2 emissions from cooling [kg CO2]

Temperature:
- overheating_hours: Hours with temperature above threshold [h]
- temp_outdoor_min: Minimum outdoor temperature [°C]
- temp_outdoor_max: Maximum outdoor temperature [°C]

Total:
- co2_total_year: Total annual CO2 emissions [kg CO2]
"""
            zip_file.writestr("units_description.txt", units_text)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()