"""
Data Models & Telemetry Definitions for WoundVision-AI: 3D Tissue Surface & PUSH Ulcer Healing Score Agent.
Domain: Wound Care AI
Standard: NPUAP / EPUAP Pressure Injury Standards
"""
import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class ExecutionStatus(str, Enum):
    NOMINAL = "NOMINAL_OPTIMAL"
    ELEVATED_RISK = "ELEVATED_RISK_WARNING"
    CRITICAL_INTERVENTION = "CRITICAL_INTERVENTION_REQUIRED"


# Safety bounds for input metrics
_FRONTIER_PRIMARY_MIN = 0.0
_FRONTIER_PRIMARY_MAX = 1000.0
_FRONTIER_SECONDARY_MIN = 0.0
_FRONTIER_SECONDARY_MAX = 1000.0


def _validate_frontier_payload(
    task_id: str,
    primary_metric: float,
    secondary_metric: float,
    status_descriptor: str,
) -> None:
    """Validate FrontierPayload fields, raising ValueError on invalid input."""
    if not task_id or not isinstance(task_id, str):
        raise ValueError("task_id must be a non-empty string")
    if not (_FRONTIER_PRIMARY_MIN <= primary_metric <= _FRONTIER_PRIMARY_MAX):
        raise ValueError(
            f"primary_metric must be between {_FRONTIER_PRIMARY_MIN} and {_FRONTIER_PRIMARY_MAX}"
        )
    if not (_FRONTIER_SECONDARY_MIN <= secondary_metric <= _FRONTIER_SECONDARY_MAX):
        raise ValueError(
            f"secondary_metric must be between {_FRONTIER_SECONDARY_MIN} and {_FRONTIER_SECONDARY_MAX}"
        )
    if not status_descriptor or not isinstance(status_descriptor, str):
        raise ValueError("status_descriptor must be a non-empty string")
    # Reject control characters in string fields
    for field_val in (task_id, status_descriptor):
        if any(ord(c) < 32 and c not in "\t\n\r" for c in field_val):
            raise ValueError("Fields must not contain control characters")


@dataclass
class FrontierPayload:
    task_id: str
    target_identifier: str
    primary_metric: float
    secondary_metric: float
    status_descriptor: str
    is_critical_flag: bool = False
    attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def __post_init__(self):
        _validate_frontier_payload(
            self.task_id, self.primary_metric, self.secondary_metric, self.status_descriptor
        )


@dataclass
class AgentTelemetryAlert:
    alert_id: str
    origin_agent: str
    status: ExecutionStatus
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "NPUAP / EPUAP Pressure Injury Standards"
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "origin_agent": self.origin_agent,
            "status": self.status.value,
            "summary": self.summary,
            "technical_details": self.technical_details,
            "actionable_remediation": self.actionable_remediation,
            "standard_reference": self.standard_reference,
            "timestamp": self.timestamp,
        }
