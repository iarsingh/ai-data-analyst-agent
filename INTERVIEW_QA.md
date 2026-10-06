# ai-data-analyst-agent — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does ai-data-analyst-agent address, and what can you demonstrate?

An analysis goal runs profile, filter, and aggregate in that order and returns revenue by region. A goal that says delete, drop, update, or insert is refused. The agent does not write the table.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/analyst/main.py`](src/analyst/main.py): Implementation or supporting configuration.
- [`src/analyst/ops.py`](src/analyst/ops.py): Implementation or supporting configuration.
- [`src/analyst/agent.py`](src/analyst/agent.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/analyst/__init__.py`](src/analyst/__init__.py): Implementation or supporting configuration.
- [`Dockerfile`](Dockerfile): Container build/service configuration.
- [`Makefile`](Makefile): Implementation or supporting configuration.
- [`docker-compose.yml`](docker-compose.yml): Container build/service configuration.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `run` and explain the decision it makes?

The main walkthrough here is `run(goal, rows)` in [`src/analyst/agent.py`](src/analyst/agent.py#L4).

```python
def run(goal, rows):
    if any(word in goal.lower() for word in WRITES):
        return {"refused": True, "reason": "This agent only reads the table.", "tools": [], "wrote": False}
    profile = {"rows": len(rows), "columns": list(rows[0]) if rows else []}
    totals = {}
    for row in rows:
        totals[row["region"]] = totals.get(row["region"], 0) + row["revenue"]
    return {"refused": False, "tools": TOOLS, "profile": profile, "revenue_by_region": totals, "wrote": False}
```

The implementation calls `any`, `goal.lower`, `len`, `list`, `totals.get`. In an interview, trace those calls in execution order using a fixture input.

## 4. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=404, detail='workspace not found')` in [`src/analyst/ops.py`](src/analyst/ops.py#L77).
- `HTTPException(status_code=404, detail='job not found')` in [`src/analyst/ops.py`](src/analyst/ops.py#L100).
- `HTTPException(status_code=404, detail='job not found')` in [`src/analyst/ops.py`](src/analyst/ops.py#L109).
- `HTTPException(status_code=403, detail='production apply is disabled in this lab')` in [`src/analyst/ops.py`](src/analyst/ops.py#L113).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_analyst.py`](tests/test_analyst.py#L4) contains `test_aggregate_and_refuse_a_write`:

```python
def test_aggregate_and_refuse_a_write():
    client = TestClient(app)
    rows = [{"region": "north", "revenue": 10}, {"region": "south", "revenue": 30}]
    payload = client.post("/agent/run", json={"goal": "average revenue by region", "rows": rows}).json()
    assert payload["tools"] == ["profile_table", "filter_rows", "aggregate"]
    assert payload["revenue_by_region"]["south"] == 30
    assert payload["wrote"] is False
    refused = client.post("/agent/run", json={"goal": "delete old rows", "rows": rows}).json()
    assert refused["refused"] is True
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `POST /agent/run` → `post_run` in [`src/analyst/main.py`](src/analyst/main.py#L9).
- `GET /readyz` → `readyz` in [`src/analyst/ops.py`](src/analyst/ops.py#L74).
- `POST /workspaces` → `create_workspace` in [`src/analyst/ops.py`](src/analyst/ops.py#L80).
- `GET /workspaces` → `list_workspaces` in [`src/analyst/ops.py`](src/analyst/ops.py#L98).
- `POST /workspaces/{workspace_id}/jobs` → `create_job` in [`src/analyst/ops.py`](src/analyst/ops.py#L106).
- `GET /jobs/{job_id}` → `get_job` in [`src/analyst/ops.py`](src/analyst/ops.py#L130).
- `POST /jobs/{job_id}/approve` → `approve_job` in [`src/analyst/ops.py`](src/analyst/ops.py#L140).
- `GET /audit` → `audit` in [`src/analyst/ops.py`](src/analyst/ops.py#L160).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. Where does state live, and what happens with multiple workers?

Module-level containers include `TOOLS` in [`src/analyst/agent.py`](src/analyst/agent.py); `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS` in [`src/analyst/ops.py`](src/analyst/ops.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `run`?

In [`src/analyst/agent.py`](src/analyst/agent.py#L4), `run(goal, rows)` receives the inputs. The function computes these intermediate values:

- `profile = {'rows': len(rows), 'columns': list(rows[0]) if rows else []}`
- `totals = {}`

Its result is defined by:

- `{'refused': False, 'tools': TOOLS, 'profile': profile, 'revenue_by_region': totals, 'wrote': False}`
- `{'refused': True, 'reason': 'This agent only reads the table.', 'tools': [], 'wrote': False}`

## 12. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/analyst/agent.py`](src/analyst/agent.py#L4) branches on:

- `any((word in goal.lower() for word in WRITES))`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## 13. What does the operations plane add, and where is its limit?

[`src/analyst/ops.py`](src/analyst/ops.py) declares `GET /readyz`, `POST /workspaces`, `GET /workspaces`, `POST /workspaces/{workspace_id}/jobs`, `GET /jobs/{job_id}`, `POST /jobs/{job_id}/approve`, `GET /audit`, `GET /metrics`. Inspect the application’s `include_router` call for its URL prefix.

Its state containers are `_WORKSPACES`, `_JOBS`, `_AUDIT`, `_METRICS`. The job-approval handler defines whether a target is accepted or refused; check that branch and the associated tests instead of treating a recorded job as a successful infrastructure apply.
