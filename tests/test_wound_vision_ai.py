import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from wound_vision_ai.models import FrontierPayload, ExecutionStatus
from wound_vision_ai.engine import FrontierDomainEngine
from wound_vision_ai.agents import TissueSegmentationBedAgent, SurfaceAreaVolumeEstimatorAgent, PUSHHealingScoreAgent, WoundVisionCoordinator
from wound_vision_ai.cli import main


def test_sub_agents():
    a1 = TissueSegmentationBedAgent()
    p1 = FrontierPayload("T1", "KEY-01", primary_metric=35.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    alerts1 = a1.audit(p1)
    assert len(alerts1) == 1
    assert alerts1[0].status == ExecutionStatus.ELEVATED_RISK

    a2 = SurfaceAreaVolumeEstimatorAgent()
    p2 = FrontierPayload("T2", "KEY-02", primary_metric=10.0, secondary_metric=15.0, status_descriptor="NOMINAL", is_critical_flag=True)
    alerts2 = a2.audit(p2)
    assert len(alerts2) == 1
    assert alerts2[0].status == ExecutionStatus.CRITICAL_INTERVENTION

    a3 = PUSHHealingScoreAgent()
    p3 = FrontierPayload("T3", "KEY-03", primary_metric=10.0, secondary_metric=4.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = a3.audit(p3)
    assert len(alerts3) == 1


def test_coordinator():
    coord = WoundVisionCoordinator()
    p_nominal = FrontierPayload("T4", "KEY-04", primary_metric=12.0, secondary_metric=4.0, status_descriptor="NOMINAL")
    dossier = coord.process(p_nominal)
    assert dossier["overall_status"] == ExecutionStatus.NOMINAL.value
    assert dossier["total_alerts"] == 0

    ans = coord.query_supervisory_chat("What standard is applied?")
    assert "NPUAP / EPUAP Pressure Injury Standards" in ans or "specifications" in ans


def test_cli():
    assert main(["audit", "--task-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_frontier_payload_validation():
    """Test that FrontierPayload validates input bounds."""
    # Valid payload should work
    p = FrontierPayload("T1", "KEY-01", primary_metric=50.0, secondary_metric=5.0, status_descriptor="NOMINAL")
    assert p.task_id == "T1"

    # Out-of-range primary metric
    with pytest.raises(ValueError):
        FrontierPayload("T2", "KEY-02", primary_metric=5000.0, secondary_metric=5.0, status_descriptor="NOMINAL")

    # Negative metric
    with pytest.raises(ValueError):
        FrontierPayload("T3", "KEY-03", primary_metric=-1.0, secondary_metric=5.0, status_descriptor="NOMINAL")

    # Empty task_id
    with pytest.raises(ValueError):
        FrontierPayload("", "KEY-04", primary_metric=10.0, secondary_metric=5.0, status_descriptor="NOMINAL")


def test_batch_error_handling():
    """Test that batch processing handles missing files gracefully."""
    result = main(["batch", "-i", "nonexistent_file.csv"])
    assert result == 1
