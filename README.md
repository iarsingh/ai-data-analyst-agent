# AI Data Analyst Agent

<!-- project-guide:start -->
## Project guide

[Project architecture](PROJECT_ARCHITECTURE.md) · [Interview questions and answers](INTERVIEW_QA.md)

Use the architecture document for the component diagram, implementation boundaries, and verification entry points. The interview guide includes source-backed answers and project walkthroughs.

### Implementation map

| Component | Responsibility |
| --- | --- |
| [`src/analyst/main.py`](src/analyst/main.py) | HTTP handlers: `POST /agent/run` |
| [`src/analyst/agent.py`](src/analyst/agent.py) | Functions: `run` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/analyst/__init__.py`](src/analyst/__init__.py) | Implementation or supporting configuration |
| [`tests/test_analyst.py`](tests/test_analyst.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

### Local setup and verification

From the repository root (the commands follow the checked-in manifests):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

To serve the FastAPI application locally, install the server separately if it is not already available:

```bash
python -m pip install uvicorn
PYTHONPATH=src python -m uvicorn analyst.main:app --reload
```

<!-- project-guide:end -->

Level: 8 — Beginner agentic AI

Skills: Python, tool order, read-only tables

An analysis goal runs profile, filter, and aggregate in that order and returns revenue by region. A goal that says delete, drop, update, or insert is refused. The agent does not write the table.

```bash
pip install -r requirements.txt
pytest -q
```

## Ops plane

Workspaces, tenant isolation, job approval, and audit live under `/v1`. Production apply is refused. See `docs/ARCHITECTURE.md`.
