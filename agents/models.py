"""
Pydantic v2 schemas and data definitions for Wound Care 3D Photogrammetry Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


# Safety bounds for input metrics
PRIMARY_METRIC_MIN = 0.0
PRIMARY_METRIC_MAX = 1000.0
SECONDARY_METRIC_MIN = 0.0
SECONDARY_METRIC_MAX = 1000.0


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier")
    target_identifier: str = Field(..., description="Entity, patient key, or genomic/cryptographic target")
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor")
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("primary_metric")
    @classmethod
    def validate_primary_metric(cls, v):
        if not (PRIMARY_METRIC_MIN <= v <= PRIMARY_METRIC_MAX):
            raise ValueError(f"primary_metric must be between {PRIMARY_METRIC_MIN} and {PRIMARY_METRIC_MAX}")
        return v

    @field_validator("secondary_metric")
    @classmethod
    def validate_secondary_metric(cls, v):
        if not (SECONDARY_METRIC_MIN <= v <= SECONDARY_METRIC_MAX):
            raise ValueError(f"secondary_metric must be between {SECONDARY_METRIC_MIN} and {SECONDARY_METRIC_MAX}")
        return v

    @field_validator("task_id", "target_identifier", "status_descriptor")
    @classmethod
    def validate_no_control_chars(cls, v):
        if not v.strip() or len(v) > 128:
            raise ValueError("Identifier/descriptor must contain 1-128 non-whitespace characters")
        if any(ord(c) < 32 or ord(c) == 127 for c in v):
            raise ValueError("Field must not contain control characters")
        return v


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "CAP / CLSI / ISO Standards"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "wound-care-3d-photogrammetry-agent"
    domain: str = "Clinical & Biomedical AI"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "CAP / CLSI / ISO Standards"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
