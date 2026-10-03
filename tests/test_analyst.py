from fastapi.testclient import TestClient
from analyst.main import app

def test_aggregate_and_refuse_a_write():
    client = TestClient(app)
    rows = [{"region": "north", "revenue": 10}, {"region": "south", "revenue": 30}]
    payload = client.post("/agent/run", json={"goal": "average revenue by region", "rows": rows}).json()
    assert payload["tools"] == ["profile_table", "filter_rows", "aggregate"]
    assert payload["revenue_by_region"]["south"] == 30
    assert payload["wrote"] is False
    refused = client.post("/agent/run", json={"goal": "delete old rows", "rows": rows}).json()
    assert refused["refused"] is True
