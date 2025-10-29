from core.facade import ConfigFacade
from core.repository import ConfigRepository
from core.validator import ConfigValidator
from core.evaluator import ExpressionEvaluator
from core.mapper import ModelMapper
from adapters.rc_engine_mock import RcEngineMock

"""
Bootstrap module to create and configure the ConfigFacade with all necessary components.
This allows to import a fully set up facade instance directly for use in the application.

add this to the ui:
    from core.bootstrap import create_facade
    facade = create_facade("demo-haus-a")

"""

def create_facade(project_id: str) ->ConfigFacade:
    repo = ConfigRepository(f"config/projects/{project_id}/config.1.0.0.json")
    return ConfigFacade(
        repo=repo,
        engine=RcEngineMock(),
        evaluator=ExpressionEvaluator(),
        validator=ConfigValidator(schema_path="config/schema/config.1.0.0.schema.json"),
        mapper=ModelMapper(),
    )
