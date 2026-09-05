# Wound Care 3D Photogrammetry Agent

> **Domain:** Clinical Decision Support & Wound Care AI
> **Standards:** CAP / CLSI / ISO / NPUAP / EPUAP Pressure Injury Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

Wound Care 3D Photogrammetry Agent is a multi-agent analytical platform for clinical wound assessment. It evaluates tissue measurements, detects anomalies, and generates structured dossiers with cryptographic audit trails. The system operates under strict zero-PHI outbound policies to prevent accidental exposure of patient identifiers.

---

## Key Capabilities

- **Multi-Agent Evaluation Pipeline**: Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) analyze each task
- **Zero-PHI Outbound Interceptor**: AST and regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation
- **Input Validation**: Bounds checking on all metrics with configurable safety limits
- **FastAPI REST API**: OpenAPI 3.1 endpoints for integration with clinical systems
- **Batch Processing**: CSV-based high-throughput evaluation with error recovery
- **Prometheus Telemetry**: Operational metrics export (`/metrics`)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/wound-care-3d-photogrammetry-agent.git
cd wound-care-3d-photogrammetry-agent

# Install dependencies
pip install -e .

# Or install directly
pip install pydantic fastapi uvicorn pytest
```

### Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env to set your production values
# AUDIT_SECRET_KEY=your-strong-random-key-here
```

---

## Usage

### CLI Commands

```bash
# Run single task evaluation
python cli.py audit --task-id TASK-001 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT

# Interactive chat with supervisor
python cli.py chat "What is the system status?"

# Batch process CSV records
python cli.py batch -i sample.csv -o results.csv

# Verify audit trail integrity
python cli.py verify-audit

# Launch REST API server
python cli.py serve --host 127.0.0.1 --port 8000
```

### REST API

```bash
# Health check
curl http://localhost:8000/health

# Submit evaluation task
curl -X POST http://localhost:8000/api/audit \
  -H "Content-Type: application/json" \
  -d @sample_payload.json

# Query audit trail
curl http://localhost:8000/api/audit/logs

# Prometheus metrics
curl http://localhost:8000/metrics
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or manually
docker build -t wound-care-3d-photogrammetry-agent .
docker run -p 8000:8000 --env-file .env wound-care-3d-photogrammetry-agent
```

---

## Input Data Schema

| Field | Type | Description | Bounds |
|:------|:-----|:------------|:-------|
| `task_id` | string | Unique task identifier | Required, non-empty |
| `target_identifier` | string | Entity or specimen key | Required, non-empty |
| `primary_metric` float | Primary measurement | 0.0 - 1000.0 |
| `secondary_metric` | float | Secondary measurement | 0.0 - 1000.0 |
| `status_descriptor` | string | Status code (NOMINAL, DISCORDANT, etc.) | Required |
| `is_critical_flag` | boolean | Emergency escalation trigger | Default: false |

---

## Testing

```bash
# Run full test suite
pytest -v

# Run with coverage
pytest -v --cov=agents --cov=wound_vision_ai

# Run simulation benchmark
python simulator.py 1000
```

---

## Security

- **Zero-PHI Guard**: All outbound data is inspected for patient identifiers before logging or transmission
- **Audit Trail**: HMAC-SHA256 chained signatures prevent tampering
- **Input Validation**: All metrics are bounds-checked; control characters are rejected
- **Secrets Management**: Production secrets via environment variables (never hardcoded)

---

## Project Structure

```
wound-care-3d-photogrammetry-agent/
├── agents/                  # Enterprise multi-agent framework
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic schemas with validation
│   ├── supervisor.py       # Master orchestrator
│   ├── workers.py          # Specialized evaluation workers
│   ├── llm_factory.py      # LLM provider abstraction
│   ├── learning.py         # Bayesian calibration engine
│   ├── metrics.py          # Prometheus metrics collector
│   └── streamer.py         # WebSocket telemetry broadcaster
├── wound_vision_ai/         # Domain-specific wound care module
│   ├── agents.py           # Tissue segmentation, PUSH scoring
│   ├── engine.py           # Core algorithmic engine
│   ├── models.py           # Frontier data models
│   ├── cli.py              # Domain CLI
│   └── server.py           # Domain FastAPI server
├── tests/                   # Pytest test suite
├── cli.py                   # Main CLI entry point
├── simulator.py             # High-throughput simulation
├── enrichment.py            # Feature enrichment suite
├── pyproject.toml           # Project configuration
├── Dockerfile               # Container build
├── docker-compose.yml       # Container orchestration
└── .env.example             # Environment template
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
