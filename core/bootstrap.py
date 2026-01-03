from pathlib import Path
from core.facade import ConfigFacade
from core.storage.config_repo import ConfigRepository
from core.validator import ConfigValidator
from core.evaluator import ExpressionEvaluator
from core.mapper import ModelMapper
from r_c_model.r_c_modell import RCEngine
from core.storage.result_repo import ResultRepository
from core.analytics.service import AnalyticsService
from core.analytics.adapters.heating_cooling_summary import HeatingCoolingSummaryAdapter
from core.analytics.adapters.temperature_summary import TemperatureSummaryAdapter
from core.analytics.adapters.temperature_timeseries import TemperatureTimeseriesAdapter
from core.analytics.adapters.heating_cooling_timeseries import HeatingCoolingTimeseriesAdapter
from core.analytics.adapters.heating_cooling_month_timeseries import HeatingCoolingMonthTimeseriesAdapter
from core.analytics.adapters.Co2_summary import Co2SummaryAdapter
from core.weather_service import WeatherService
from core.storage.weather_repo import WeatherRepository
from core.storage.measurements_repo import MeasurementsRepository
from core.measure_service import MeasureService



"""
Bootstrap module to create and configure the ConfigFacade with all necessary components.
This allows to import a fully set up facade instance directly for use in the application.

add this to the ui:
    from core.bootstrap import create_facade
    facade = create_facade("demo-haus-a")

"""

def create_facade(project_id: str, variant_id) -> ConfigFacade:
    Root = Path(__file__).resolve().parents[1]
    
    cfg_file = Root / "projects" / project_id / "config" / f"config_{variant_id}.json"
    schema = Root / "projects" / "schema" / "config" / f"config_{variant_id}.schema.json"
    res_file = Root / "projects" / project_id / "results" / f"raw_results_{variant_id}.parquet"
    weath_file_raw = Root / "projects" / project_id / "weather" / "raw" / f"weather_{variant_id}_raw.mat"
    weath_file_proc = Root / "projects" / project_id / "weather" / "processed" / f"weather_{variant_id}.parquet"
    measr_file_raw = Root / "projects" / "measurements" / "raw" / "measurement_raw.csv"
    measr_file_proc = Root / "projects" / "measurements" / "processed" / f"measurements.parquet"
    config_repo = ConfigRepository(str(cfg_file))
    result_repo = ResultRepository(res_file)
    weather_repo = WeatherRepository(weath_file_raw, weath_file_proc)
    measure_repo = MeasurementsRepository(measr_file_raw, measr_file_proc)

    engine = RCEngine()
    evaluator = ExpressionEvaluator()
    validator = ConfigValidator(schema_path=str(schema))
    mapper = ModelMapper()
    weather_service = WeatherService(weather_repo)
    measure_service = MeasureService(measure_repo)

    adapters = [
        HeatingCoolingSummaryAdapter(),
        TemperatureSummaryAdapter(),
        TemperatureTimeseriesAdapter(),
        HeatingCoolingTimeseriesAdapter(),
        HeatingCoolingMonthTimeseriesAdapter(),
        Co2SummaryAdapter(),
        ]
    analytics = AnalyticsService(
        config_repo=config_repo,
        result_repo=result_repo,
        adapters=adapters
        )
    
    return ConfigFacade(
        config_repo=config_repo,
        engine=engine,
        evaluator=evaluator,
        validator=validator,
        mapper=mapper,
        result=result_repo,
        analytics=analytics,
        weather_service=weather_service,
        measure_service=measure_service,
        weather_repo=weather_repo,
        measure_repo=measure_repo
    )

