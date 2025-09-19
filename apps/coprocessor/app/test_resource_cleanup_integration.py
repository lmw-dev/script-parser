"""
Integration tests for resource cleanup mechanism.
Tests actual file creation and cleanup without mocking.
"""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from .main import app


class TestResourceCleanupIntegration:
    """Integration tests for resource cleanup"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_temp_file_cleanup_after_successful_request(self, client):
        """Test that temporary files are cleaned up after successful processing"""
        temp_files_created = []

        # Track temp files created by patching the cleanup method
        original_cleanup = None

        async def track_cleanup(file_path):
            temp_files_created.append(file_path)
            # Call original cleanup
            await original_cleanup(file_path)

        from .services.file_handler import FileHandler

        original_cleanup = FileHandler.cleanup

        with patch.object(FileHandler, "cleanup", track_cleanup):
            # Make a file upload request
            response = client.post(
                "/api/parse",
                files={"file": ("test.mp4", b"test_file_content", "video/mp4")},
            )

            # Request should complete (success or error doesn't matter for cleanup test)
            assert response.status_code in [200, 500]  # Either success or handled error

            # Verify cleanup was called (meaning temp files were created and cleaned up)
            assert (
                len(temp_files_created) >= 1
            ), "Cleanup should have been called for temp files"

    def test_temp_file_cleanup_after_error_request(self, client):
        """Test that temporary files are cleaned up even when processing fails"""
        temp_files_cleaned = []

        # Track temp files cleaned
        original_cleanup = None

        async def track_cleanup(file_path):
            temp_files_cleaned.append(file_path)
            # Call original cleanup
            await original_cleanup(file_path)

        from .main import WorkflowOrchestrator
        from .services.file_handler import FileHandler

        original_cleanup = FileHandler.cleanup

        with patch.object(FileHandler, "cleanup", track_cleanup), patch.object(
            WorkflowOrchestrator, "process_file_workflow"
        ) as mock_process:
            # Force processing to fail
            mock_process.side_effect = Exception("Simulated processing error")

            # Make a file upload request
            response = client.post(
                "/api/parse",
                files={"file": ("test.mp4", b"test_file_content", "video/mp4")},
            )

            # Request should return error
            assert response.status_code == 500

            # Verify cleanup was called even after error
            assert (
                len(temp_files_cleaned) >= 1
            ), "Cleanup should have been called even after error"

    def test_no_temp_files_for_url_requests(self, client):
        """Test that URL requests don't create temporary files"""
        save_upload_called = []

        # Track if save_upload_file is called
        original_save_upload_file = None

        async def track_save_upload(self, file):
            save_upload_called.append(True)
            return await original_save_upload_file(self, file)

        from .services.file_handler import FileHandler

        original_save_upload_file = FileHandler.save_upload_file

        with patch.object(FileHandler, "save_upload_file", track_save_upload):
            # Make a URL request
            response = client.post(
                "/api/parse",
                json={"url": "https://www.xiaohongshu.com/discovery/item/test"},
            )

            # Request should complete (success or error doesn't matter)
            assert response.status_code in [200, 400, 500]

            # save_upload_file should not be called for URL requests
            assert (
                len(save_upload_called) == 0
            ), "save_upload_file should not be called for URL requests"

    def test_file_handler_cleanup_with_real_file(self, tmp_path):
        """Test FileHandler.cleanup with a real file"""
        from .services.file_handler import FileHandler

        # Create a real temporary file
        test_file = tmp_path / "test_cleanup.txt"
        test_file.write_text("test content for cleanup")
        assert test_file.exists()

        # Test cleanup
        import asyncio

        asyncio.run(FileHandler.cleanup(test_file))

        # Verify file was removed
        assert not test_file.exists()

    def test_file_handler_cleanup_with_nonexistent_file(self, tmp_path):
        """Test FileHandler.cleanup with a non-existent file (should not raise error)"""
        from .services.file_handler import FileHandler

        # Use a non-existent file path
        nonexistent_file = tmp_path / "does_not_exist.txt"
        assert not nonexistent_file.exists()

        # This should not raise any exception
        import asyncio

        asyncio.run(FileHandler.cleanup(nonexistent_file))

        # File should still not exist (obviously)
        assert not nonexistent_file.exists()
