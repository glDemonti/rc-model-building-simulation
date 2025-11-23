from pathlib import Path
from core.facade import ConfigFacade
from core.repository import ConfigRepository
from core.validator import ConfigValidator
from core.evaluator import ExpressionEvaluator
from core.mapper import ModelMapper
from r_c_model.r_c_modell import RCEngine
from core.storage.result_store import ResultRepository
from core.analytics.service import AnalyticsService
from core.analytics.adapters.heating_cooling_summary import HeatingCoolingSummaryAdapter
from core.analytics.adapters.temperature_summary import TemperatureSummaryAdapter
from core.analytics.adapters.temperature_timeseries import TemperatureTimeseriesAdapter
from core.analytics.adapters.heating_cooling_timeseries import HeatingCoolingTimeseriesAdapter


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
    repo = ConfigRepository(str(cfg_file))
    result_repo = ResultRepository()

    adapters = [
        HeatingCoolingSummaryAdapter(),
        TemperatureSummaryAdapter(),
        TemperatureTimeseriesAdapter(),
        HeatingCoolingTimeseriesAdapter(),

    ]
    analytics = AnalyticsService(
        config_repo=repo,
        result_repo=result_repo,
        adapters=adapters
        )
    
    return ConfigFacade(
        repo=repo,
        engine=RCEngine(),
        evaluator=ExpressionEvaluator(),
        validator=ConfigValidator(schema_path=str(schema)),
        mapper=ModelMapper(),
        result=result_repo,
        analytics=analytics
    )

