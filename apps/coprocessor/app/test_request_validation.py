"""
Comprehensive tests for request validation and input processing improvements
Tests all validation scenarios required by task 6
"""

import pytest
from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


class TestRequestValidation:
    """Test comprehensive request validation scenarios"""

    def test_valid_json_url_request(self):
        """Test valid JSON request with URL - should succeed"""
        response = client.post(
            "/api/parse",
            json={
                "url": "https://www.xiaohongshu.com/discovery/item/68c94ab0000000001202ca84"
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["success"] is True
        assert "processing_time" in data

    def test_valid_file_upload_request(self):
        """Test valid multipart file upload - should succeed"""
        response = client.post(
            "/api/parse", files={"file": ("test.mp4", b"file_content", "video/mp4")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["success"] is True
        assert "processing_time" in data

    def test_invalid_json_format(self):
        """Test invalid JSON format - should return HTTP 422 with business code 4002"""
        # Send malformed JSON
        response = client.post(
            "/api/parse",
            data='{"url": "http://test.com"',  # Missing closing brace
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Invalid JSON format in request body" in data["message"]
        assert "processing_time" in data

    def test_empty_json_request(self):
        """Test empty JSON request - should return HTTP 400 with business code 4002"""
        response = client.post("/api/parse", json={})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data

    def test_json_without_url_field(self):
        """Test JSON without URL field - should return HTTP 400 with business code 4002"""
        response = client.post("/api/parse", json={"other_field": "value"})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data

    def test_form_data_url_submission(self):
        """Test URL sent as form data - should return HTTP 422 with clear message"""
        response = client.post("/api/parse", data={"url": "http://test.com"})
        assert response.status_code == 422
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "URL should be sent as JSON, not form data" in data["message"]
        assert "processing_time" in data

    def test_multipart_form_url_submission(self):
        """Test URL sent as multipart form data - should return HTTP 422 with clear message"""
        response = client.post(
            "/api/parse",
            data={"url": "http://test.com"},
            files={},  # This makes it multipart/form-data
        )
        assert response.status_code == 422
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "URL should be sent as JSON, not form data" in data["message"]
        assert "processing_time" in data

    def test_multipart_without_file_or_url(self):
        """Test multipart request without file or URL - should return HTTP 400"""
        response = client.post(
            "/api/parse",
            files={},  # Empty multipart form
        )
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data

    def test_empty_request_no_content_type(self):
        """Test completely empty request - should return HTTP 400"""
        response = client.post("/api/parse")
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data

    def test_unsupported_content_type(self):
        """Test unsupported content type - should return HTTP 400"""
        response = client.post(
            "/api/parse", data="some text data", headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data

    def test_invalid_url_format(self):
        """Test invalid URL format - should return HTTP 400 with business code 4001"""
        response = client.post("/api/parse", json={"url": "not-a-valid-url"})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4001
        assert data["success"] is False
        assert "Failed to parse video URL" in data["message"]
        assert "processing_time" in data

    def test_unsupported_platform_url(self):
        """Test unsupported platform URL - should return HTTP 400 with business code 4001"""
        response = client.post(
            "/api/parse", json={"url": "http://unsupported-platform.com/video"}
        )
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4001
        assert data["success"] is False
        assert "Failed to parse video URL" in data["message"]
        assert "processing_time" in data

    def test_null_url_in_json(self):
        """Test null URL in JSON - should return HTTP 400"""
        response = client.post("/api/parse", json={"url": None})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data

    def test_empty_string_url_in_json(self):
        """Test empty string URL in JSON - should return HTTP 400"""
        response = client.post("/api/parse", json={"url": ""})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data

    def test_whitespace_only_url_in_json(self):
        """Test whitespace-only URL in JSON - should return HTTP 400"""
        response = client.post("/api/parse", json={"url": "   \t\n  "})
        assert response.status_code == 400
        data = response.json()["detail"]
        assert data["code"] == 4002
        assert data["success"] is False
        assert "Either URL or file must be provided" in data["message"]
        assert "processing_time" in data


class TestErrorResponseFormat:
    """Test that all error responses follow the standardized format"""

    def test_error_response_structure(self):
        """Test that error responses have the correct structure"""
        response = client.post("/api/parse", json={})
        assert response.status_code == 400

        data = response.json()["detail"]

        # Check all required fields are present
        assert "code" in data
        assert "success" in data
        assert "data" in data
        assert "message" in data
        assert "processing_time" in data

        # Check field types and values
        assert isinstance(data["code"], int)
        assert data["success"] is False
        assert data["data"] is None
        assert isinstance(data["message"], str)
        assert isinstance(data["processing_time"], int | float)
        assert data["processing_time"] >= 0

    def test_processing_time_in_all_errors(self):
        """Test that processing_time is included in all error responses"""
        test_cases = [
            # Invalid JSON
            {
                "method": "post",
                "url": "/api/parse",
                "data": '{"invalid": json}',
                "headers": {"Content-Type": "application/json"},
            },
            # Missing input
            {"method": "post", "url": "/api/parse", "json": {}},
            # Form URL
            {"method": "post", "url": "/api/parse", "data": {"url": "http://test.com"}},
        ]

        for case in test_cases:
            if "json" in case:
                response = client.post(case["url"], json=case["json"])
            elif "data" in case and "headers" in case:
                response = client.post(
                    case["url"], data=case["data"], headers=case["headers"]
                )
            elif "data" in case:
                response = client.post(case["url"], data=case["data"])
            else:
                response = client.post(case["url"])

            assert response.status_code in [400, 422]
            data = response.json()["detail"]
            assert "processing_time" in data
            assert isinstance(data["processing_time"], int | float)
            assert data["processing_time"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
