import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to ABCC API"}

# More comprehensive tests for agents and langgraph would require mocking 
# the database and LLM calls, which can be done using `unittest.mock.patch`.
