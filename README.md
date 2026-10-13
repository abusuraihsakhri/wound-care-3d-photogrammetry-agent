# Wound Care 3D Photogrammetry Agent

A research-stage Python rule-evaluation prototype with a standalone browser demonstration. **Despite the repository name, the current implementation does not reconstruct 3D surfaces, process wound photographs, segment tissue, or calculate validated PUSH scores.** Its thresholds and descriptors are illustrative software rules, **not clinical decision criteria**.

## Browser demonstration

Open `web/index.html` locally, or deploy the `web/` directory through GitHub Pages. The page evaluates three existing backend rules and exports a JSON result. It runs entirely in-browser without Python, external scripts, a backend connection, network uploads, cookies, or browser storage. The Pages workflow is supplied in `.github/workflows/pages.yml`; a public URL should only be published after Pages is enabled and the deployed page is verified.

Use **synthetic identifiers only**. Do not provide identifiable patient data or use outputs to direct patient care.

## What is implemented

- `agents/`: Pydantic-validated audit payloads and three deterministic workers: primary metric above **25**, secondary metric above **12** or critical flag, and anomaly-keyword detection.
- `agents/base.py`: process-local HMAC-SHA256 hash-chain for audit events, including signature verification. Logs exist only in RAM and are lost on restart; this is **not** a durable or externally anchored audit record.
- `agents/api.py`: FastAPI endpoints (`/health`, `/api/audit`, `/api/chat`, `/api/audit/logs`, `/metrics`) and the local browser demonstration at `/`. The `/metrics` endpoint returns JSON counters, not Prometheus exposition text.
- `wound_vision_ai/`: a separate experimental rule engine (primary threshold **25**, secondary threshold **10**) and CLI. Despite legacy class names, it does not calculate a clinical PUSH score or 3D surface metrics.
- `enrichment.py`: placeholder threshold-based modules; no validated prediction or live healthcare integration.

The `mock` model provider returns a deterministic message; it does not call an LLM. The references to clinical standards in legacy output are not evidence of compliance or clinical validation.

## Install and run

Python 3.9+ (CI tests 3.10–3.12):

```bash
git clone https://github.com/abusuraihsakhri/wound-care-3d-photogrammetry-agent.git
cd wound-care-3d-photogrammetry-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python cli.py audit --task-id DEMO-1 --target SAMPLE-1 --primary 29.4 --secondary 14.8 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py serve --host 127.0.0.1 --port 8000
```

With the API running, browse to `http://127.0.0.1:8000/`. Submit synthetic JSON to `POST /api/audit`, or inspect `/docs` for the FastAPI-generated schema.

```bash
curl -X POST http://127.0.0.1:8000/api/audit \
  -H 'Content-Type: application/json' \
  --data-binary @sample_payload.json
```

The separate domain rule CLI can be run with `python -m wound_vision_ai.cli audit`. Docker configuration is provided for running the API; set `AUDIT_SECRET_KEY` in a private `.env` file before a non-development deployment.

## Test and build

```bash
python -m pip install -e . pytest httpx build
python -m pytest -q
python -m compileall -q agents wound_vision_ai cli.py enrichment.py simulator.py
node --check web/app.js
node --test tests/test_browser_demo.cjs
python -m build
```

The GitHub Actions CI workflow runs the Python test suite across Python 3.10, 3.11, and 3.12, including JavaScript rule tests and a package build.

## Privacy and limitations

The backend includes **heuristic regular-expression screening** for common identifier patterns. This is neither complete PHI de-identification nor a HIPAA-compliance guarantee. The API has **no authentication** and should not be exposed on the public internet or used with real patient data. Browser validation restricts the shape of synthetic identifiers, but cannot establish whether a value is personally identifying.

A missing `AUDIT_SECRET_KEY` now generates a temporary random key for development; a stable secret must be configured for process-consistent signatures. Audit records are in memory, without durable storage, external anchoring, or meaningful cross-restart integrity guarantees. The browser demonstration does **not** generate HMAC signatures.

The project is experimental software and requires independent clinical validation, cybersecurity review, and architecture work before any use in clinical workflows.

## Technologies and compatibility

Python, Pydantic, FastAPI, Uvicorn; standard HTML/CSS/JavaScript for the static interface. The browser demonstration requires a modern desktop/mobile browser with JavaScript and Blob download support. No Pyodide is necessary for the implemented rules.

## License

MIT — see [LICENSE](LICENSE).
