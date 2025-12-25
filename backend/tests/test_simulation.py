from backend.sample_data import SAMPLE_MODEL
from backend.simulation import SimulationEngine
from backend.models import SwitchState


def test_parallel_sources_alert():
    engine = SimulationEngine(SAMPLE_MODEL)
    result = engine.run({"e9": SwitchState.CLOSED})
    assert any("Paralelo" in msg for msg in result.alerts)


def test_switch_open_breaks_load():
    engine = SimulationEngine(SAMPLE_MODEL)
    result = engine.run({"e2": SwitchState.OPEN})
    assert "load_1" not in result.energized_nodes
