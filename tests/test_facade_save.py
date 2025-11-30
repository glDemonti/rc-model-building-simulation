import copy
import pytest

from core.facade import ConfigFacade


class FakeRepo:
    def __init__(self):
        self.writes = []

    def write_raw(self, cfg: dict):
        self.writes.append(copy.deepcopy(cfg))


class FakeEvaluatorOK:
    def evaluate_cfg(self, cfg: dict):
        # no error -> returns cfg (ev. with 'value')
        return cfg, []

   
class FakeEvaluatorWithError:
    def evaluate_cfg(self, cfg: dict):
        return cfg, ["dummy error"]


class FakeValidatorOK:
    def validate(self, cfg: dict):
        return True, "ok"
    
def test_save_happy_path(sample_cfg):
    repo = FakeRepo()
    facade = ConfigFacade(
        config_repo=repo,
        engine=None,
        evaluator=FakeEvaluatorOK(),
        validator=FakeValidatorOK(),
        result=None,
        mapper=None,
    )
    ok , msg = facade.save("demo", sample_cfg)
    assert ok is True
    assert repo.writes, "Repo sollte geschrieben haben"
    written = repo.writes[-1]
    assert "some" in written

def test_safe_evaluator_error_blocks_write(sample_cfg):
    repo = FakeRepo()
    facade = ConfigFacade(
        config_repo=repo,
        engine=None,
        evaluator=FakeEvaluatorWithError(),
        validator=FakeValidatorOK(),
        result=None,
        mapper=None,
    )
    ok , msg = facade.save("demo", sample_cfg)
    assert ok is False
    assert not repo.writes, "Bei Evaluator-Fehler darf nichts geschrieben werden"
    assert "error" in msg.lower()

@pytest.fixture
def sample_cfg():
    return {
        "some": {"expression": "2*3"},
        }