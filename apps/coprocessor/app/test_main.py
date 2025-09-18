from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_successful_url_request():
    """Test successful JSON request with URL"""
    # Test with xiaohongshu URL - should now work with mock data
    response = client.post(
        "/api/parse", json={"url": "https://www.xiaohongshu.com/discovery/item/68c94ab0000000001202ca84"}
    )
    assert response.status_code == 200  # Should now succeed
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "transcript" in data["data"]


def test_successful_file_upload_request():
    """Test successful multipart form data request with file"""
    response = client.post(
        "/api/parse", files={"file": ("test.mp4", b"file_content", "video/mp4")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "transcript" in data["data"]
    assert "test.mp4" in data["data"]["transcript"]


def test_missing_inputs_request():
    """Test request with neither URL nor file"""
    response = client.post("/api/parse")
    assert response.status_code == 400


def test_content_type_mismatch_url_request():
    """Test URL sent as form data instead of JSON"""
    response = client.post("/api/parse", data={"url": "http://test.com"})
    assert response.status_code == 422


def test_unsupported_platform_url_request():
    """Test unsupported platform URL returns 400"""
    response = client.post("/api/parse", json={"url": "http://test.com"})
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported platform" in data["detail"]
