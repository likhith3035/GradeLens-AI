import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "sample_memos"

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["app_name"] == "MemoScan AI"
    assert data["database_connected"] is True
    assert "registered_parsers" in data

def test_settings_endpoints():
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "mode" in data

    # Toggle mode to online and back to local
    res = client.post("/api/settings/mode", json={"mode": "online"})
    assert res.status_code == 200
    assert res.json()["mode"] == "online"

    res = client.post("/api/settings/mode", json={"mode": "local"})
    assert res.status_code == 200
    assert res.json()["mode"] == "local"

def test_upload_and_flow():
    pdf_path = SAMPLE_DIR / "memo_1_jntu_passed.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # Upload memo
    res = client.post(
        "/api/upload",
        files=[("files", ("memo_1_jntu_passed.pdf", file_bytes, "application/pdf"))],
        data={"profile": "auto"}
    )
    assert res.status_code == 200
    upload_data = res.json()
    assert upload_data["total_files"] == 1
    assert upload_data["processed_files"] == 1
    assert upload_data["items"][0]["roll_number"] == "20671A0512"

    # Query students
    res = client.get("/api/students")
    assert res.status_code == 200
    students = res.json()
    assert len(students) >= 1
    assert any(s["roll_number"] == "20671A0512" for s in students)

    # Query student profile
    res = client.get("/api/students/20671A0512")
    assert res.status_code == 200
    detail = res.json()
    assert detail["roll_number"] == "20671A0512"
    assert len(detail["semester_results"]) >= 1

    # Query Analytics
    res = client.get("/api/analytics")
    assert res.status_code == 200
    analytics = res.json()
    assert analytics["overview"]["total_students"] >= 1
    assert analytics["overview"]["total_memos_processed"] >= 1

    # Test Excel Export
    res = client.get("/api/export/excel")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(res.content) > 1000

def test_review_queue_and_resolve_all():
    # Fetch review queue
    res = client.get("/api/review/queue")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # Call resolve-all
    res = client.post("/api/review/resolve-all?actor=AutomatedTest")
    assert res.status_code == 200
    data = res.json()
    assert "resolved_count" in data

    # Review queue should now be empty
    res_after = client.get("/api/review/queue")
    assert res_after.status_code == 200
    assert len(res_after.json()) == 0
