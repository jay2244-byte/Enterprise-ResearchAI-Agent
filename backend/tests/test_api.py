import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_api():
    response = client.get("/api/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data


def test_system_stats_api():
    response = client.get("/api/system/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_projects" in data
    assert "total_sources" in data
    assert "total_findings" in data


def test_create_and_list_research_project():
    # Create project
    payload = {
        "question": "What is the economic impact of autonomous supply chain agents?",
        "industry": "Logistics & Supply Chain",
        "scope": "Comprehensive",
        "max_sources": 4
    }
    response = client.post("/api/research", json=payload)
    assert response.status_code == 200
    project = response.json()
    assert project["id"] > 0
    assert project["question"] == payload["question"]

    # Get details
    get_res = client.get(f"/api/research/{project['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == project["id"]

    # List projects
    list_res = client.get("/api/research")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(p["id"] == project["id"] for p in items)


def test_knowledge_search_api():
    response = client.get("/api/knowledge/search?q=supply")
    assert response.status_code == 200
    data = response.json()
    assert "total_results" in data
    assert "results" in data
