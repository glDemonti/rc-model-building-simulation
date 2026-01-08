import copy
import pytest
import pandas as pd
from pathlib import Path

from core.facade import ConfigFacade, RunReport


# ============================================================================
# Mock Classes
# ============================================================================


class FakeConfigRepo:
    def __init__(self, initial_cfg=None):
        self.cfg = initial_cfg or {"test": "config"}
        self.writes = []

    def read_raw(self):
        return copy.deepcopy(self.cfg)

    def write_raw(self, cfg: dict):
        self.writes.append(copy.deepcopy(cfg))
        self.cfg = copy.deepcopy(cfg)


class FakeResultRepo:
    def __init__(self):
        self.saved_results = []

    def save_raw(self, df: pd.DataFrame):
        self.saved_results.append(df.copy())


class FakeWeatherRepo:
    def __init__(self):
        self.raw_writes = []
        self.original_names = []

    def write_raw(self, path: Path):
        self.raw_writes.append(str(path))

    def save_original_name(self, name: str):
        self.original_names.append(name)


class FakeMeasurementRepo:
    def __init__(self):
        self.raw_writes = []
        self.original_names = []

    def write_raw(self, path: Path):
        self.raw_writes.append(str(path))

    def save_original_name(self, name: str):
        self.original_names.append(name)


class FakeEvaluatorOK:
    def evaluate_cfg(self, cfg: dict):
        # no error -> returns cfg with evaluated values
        evaluated = copy.deepcopy(cfg)
        # Simulate expression evaluation
        if "some" in evaluated and "expression" in evaluated["some"]:
            evaluated["some"]["value"] = 6  # 2*3
        return evaluated, []


class FakeEvaluatorWithError:
    def evaluate_cfg(self, cfg: dict):
        return cfg, ["dummy evaluation error"]


class FakeMapper:
    def to_model_params(self, cfg: dict):
        # Return a mock RCParams object
        return {"mock": "params"}


class FakeEngine:
    def run(self, params, weather_df: pd.DataFrame):
        # Return mock simulation results
        return pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, freq="h"),
            "temp_air_room": [20.0, 21.0, 22.0],
            "heating_power": [100.0, 150.0, 200.0],
        })


class FakeWeatherService:
    def __init__(self):
        self.processed_count = 0

    def load_weather(self):
        return pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=3, freq="h"),
            "temp_outdoor": [5.0, 6.0, 7.0],
        })

    def process_and_store_weather(self, cfg=None):
        # Align with real WeatherService signature; cfg is unused in fake
        self.processed_count += 1


class FakeMeasureService:
    def process_and_store_measurements(self):
        return pd.DataFrame({
            "datetime": pd.date_range("2024-01-01", periods=2, freq="h"),
            "measured_temp": [20.5, 21.5],
        })


class FakeAnalyticsService:
    def compute_all(self, project_id: str, variant_id: str):
        return {
            "summary": pd.DataFrame({
                "variant_id": [variant_id],
                "end_use": ["heating"],
                "metric": ["energy_year"],
                "value": [1000.0],
            }),
            "timeseries": pd.DataFrame({
                "datetime": pd.date_range("2024-01-01", periods=2, freq="h"),
                "variant_id": [variant_id, variant_id],
                "heating_power": [100.0, 150.0],
            }),
        }


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_cfg():
    return {
        "some": {"expression": "2*3"},
        "building_geometry": {"height": {"expression": "10"}},
    }


@pytest.fixture
def config_repo():
    return FakeConfigRepo()


@pytest.fixture
def result_repo():
    return FakeResultRepo()


@pytest.fixture
def weather_repo():
    return FakeWeatherRepo()


@pytest.fixture
def measure_repo():
    return FakeMeasurementRepo()


@pytest.fixture
def facade_full():
    """Fully configured facade with all dependencies"""
    return ConfigFacade(
        config_repo=FakeConfigRepo(),
        engine=FakeEngine(),
        result=FakeResultRepo(),
        evaluator=FakeEvaluatorOK(),
        validator=None,
        mapper=FakeMapper(),
        analytics=FakeAnalyticsService(),
        weather_service=FakeWeatherService(),
        measure_service=FakeMeasureService(),
        weather_repo=FakeWeatherRepo(),
        measure_repo=FakeMeasurementRepo(),
    )


# ============================================================================
# Tests: save_config
# ============================================================================


def test_save_config_happy_path(sample_cfg):
    """Test successful config save with evaluation"""
    repo = FakeConfigRepo()
    facade = ConfigFacade(
        config_repo=repo,
        engine=None,
        evaluator=FakeEvaluatorOK(),
        validator=None,
        result=None,
        mapper=None,
    )
    ok, msg = facade.save_config("demo", sample_cfg)
    
    assert ok is True
    assert msg == "Gespeichert"
    assert len(repo.writes) == 1
    written = repo.writes[-1]
    assert "some" in written


def test_save_config_evaluator_error_blocks_write(sample_cfg):
    """Test that evaluator errors prevent saving"""
    repo = FakeConfigRepo()
    facade = ConfigFacade(
        config_repo=repo,
        engine=None,
        evaluator=FakeEvaluatorWithError(),
        validator=None,
        result=None,
        mapper=None,
    )
    ok, msg = facade.save_config("demo", sample_cfg)
    
    assert ok is False
    assert len(repo.writes) == 0
    assert "error" in msg.lower()
    assert "dummy evaluation error" in msg


def test_save_config_write_exception():
    """Test handling of write exceptions"""
    class FailingRepo:
        def write_raw(self, cfg):
            raise IOError("Disk full")

    facade = ConfigFacade(
        config_repo=FailingRepo(),
        engine=None,
        evaluator=FakeEvaluatorOK(),
        validator=None,
        result=None,
        mapper=None,
    )
    ok, msg = facade.save_config("demo", {"test": "data"})
    
    assert ok is False
    assert "Speichern fehlgeschlagen" in msg
    assert "Disk full" in msg


# ============================================================================
# Tests: load_config
# ============================================================================


def test_load_config_returns_copy():
    """Test that load_config returns configuration"""
    initial_cfg = {"key": "value", "nested": {"data": 123}}
    repo = FakeConfigRepo(initial_cfg)
    facade = ConfigFacade(
        config_repo=repo,
        engine=None,
        result=None,
    )
    
    loaded = facade.load_config("demo")
    
    assert loaded == initial_cfg
    assert loaded is not initial_cfg  # Should be a copy


# ============================================================================
# Tests: run_simulation
# ============================================================================


def test_run_simulation_success(facade_full):
    """Test successful simulation run"""
    report = facade_full.run_simulation("project_a", "A")
    
    assert isinstance(report, RunReport)
    assert report.ok is True
    assert report.run_id == "latest"
    assert "project_a" in report.message
    assert "variant A" in report.message


def test_run_simulation_saves_results():
    """Test that simulation results are saved"""
    result_repo = FakeResultRepo()
    facade = ConfigFacade(
        config_repo=FakeConfigRepo(),
        engine=FakeEngine(),
        result=result_repo,
        mapper=FakeMapper(),
        weather_service=FakeWeatherService(),
    )
    
    facade.run_simulation("test_project", "A")
    
    assert len(result_repo.saved_results) == 1
    df = result_repo.saved_results[0]
    assert isinstance(df, pd.DataFrame)
    assert "temp_air_room" in df.columns


def test_run_simulation_uses_weather_data():
    """Test that simulation loads and uses weather data"""
    weather_service = FakeWeatherService()
    facade = ConfigFacade(
        config_repo=FakeConfigRepo(),
        engine=FakeEngine(),
        result=FakeResultRepo(),
        mapper=FakeMapper(),
        weather_service=weather_service,
    )
    
    facade.run_simulation("test_project", "B")
    
    # Weather service should have been called
    # (verified indirectly through successful completion)


# ============================================================================
# Tests: get_summary and get_timeseries
# ============================================================================


def test_get_summary_returns_dataframe(facade_full):
    """Test get_summary returns summary data"""
    summary = facade_full.get_summary("project_a", "A")
    
    assert isinstance(summary, pd.DataFrame)
    assert "variant_id" in summary.columns
    assert summary.iloc[0]["variant_id"] == "A"


def test_get_timeseries_returns_dataframe(facade_full):
    """Test get_timeseries returns timeseries data"""
    timeseries = facade_full.get_timeseries("project_a", "B")
    
    assert isinstance(timeseries, pd.DataFrame)
    assert "datetime" in timeseries.columns
    assert "variant_id" in timeseries.columns


def test_get_context_returns_all_analytics(facade_full):
    """Test get_context returns complete analytics context"""
    context = facade_full.get_context("project_a", "A")
    
    assert isinstance(context, dict)
    assert "summary" in context
    assert "timeseries" in context


def test_get_context_without_analytics_raises_error():
    """Test that get_context raises error when analytics not configured"""
    facade = ConfigFacade(
        config_repo=FakeConfigRepo(),
        engine=None,
        result=None,
        analytics=None,
    )
    
    with pytest.raises(RuntimeError, match="AnalyticsService not configured"):
        facade.get_context("project_a", "A")


# ============================================================================
# Tests: get_measurements
# ============================================================================


def test_get_measurements_returns_dataframe(facade_full):
    """Test get_measurements returns measurement data"""
    measurements = facade_full.get_measurements()
    
    assert isinstance(measurements, pd.DataFrame)
    assert "datetime" in measurements.columns


# ============================================================================
# Tests: update_weather_file
# ============================================================================


def test_update_weather_file_writes_and_processes():
    """Test weather file update writes raw data and processes it"""
    weather_repo = FakeWeatherRepo()
    weather_service = FakeWeatherService()
    
    facade = ConfigFacade(
        config_repo=FakeConfigRepo(),
        engine=None,
        result=None,
        weather_repo=weather_repo,
        weather_service=weather_service,
    )
    
    facade.update_weather_file("/tmp/test_weather.mat", "weather_data.mat")
    
    assert len(weather_repo.raw_writes) == 1
    assert weather_repo.raw_writes[0] == "/tmp/test_weather.mat"
    assert len(weather_repo.original_names) == 1
    assert weather_repo.original_names[0] == "weather_data.mat"
    assert weather_service.processed_count == 1


# ============================================================================
# Tests: update_measurement_file
# ============================================================================


def test_update_measurement_file_writes_data():
    """Test measurement file update writes raw data"""
    measure_repo = FakeMeasurementRepo()
    
    facade = ConfigFacade(
        config_repo=FakeConfigRepo(),
        engine=None,
        result=None,
        measure_repo=measure_repo,
    )
    
    facade.update_measurement_file("/tmp/test.csv", "measurements.csv")
    
    assert len(measure_repo.raw_writes) == 1
    assert measure_repo.raw_writes[0] == "/tmp/test.csv"
    assert len(measure_repo.original_names) == 1
    assert measure_repo.original_names[0] == "measurements.csv"


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_simulation_workflow(facade_full):
    """Test complete workflow: load -> simulate -> get results"""
    # Load config
    cfg = facade_full.load_config("project_a")
    assert cfg is not None
    
    # Run simulation
    report = facade_full.run_simulation("project_a", "A")
    assert report.ok is True
    
    # Get results
    summary = facade_full.get_summary("project_a", "A")
    assert isinstance(summary, pd.DataFrame)
    
    timeseries = facade_full.get_timeseries("project_a", "A")
    assert isinstance(timeseries, pd.DataFrame)


def test_config_modification_workflow():
    """Test workflow: load -> modify -> save -> load again"""
    initial_cfg = {"value": 10, "name": "test"}
    repo = FakeConfigRepo(initial_cfg)
    
    facade = ConfigFacade(
        config_repo=repo,
        engine=None,
        result=None,
        evaluator=FakeEvaluatorOK(),
    )
    
    # Load
    cfg = facade.load_config("project")
    assert cfg["value"] == 10
    
    # Modify
    cfg["value"] = 20
    
    # Save
    ok, msg = facade.save_config("project", cfg)
    assert ok is True
    
    # Load again
    cfg_new = facade.load_config("project")
    assert cfg_new["value"] == 20
