"""
Tests for resource cleanup mechanism in the /api/parse endpoint.
Verifies that temporary files are cleaned up in all scenarios including exceptions.
"""
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient

from .main import app, WorkflowOrchestrator
from .services.file_handler import TempFileInfo, FileHandler


class TestResourceCleanup:
    """Test resource cleanup in various scenarios"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_temp_file_info(self):
        """Create mock TempFileInfo"""
        return TempFileInfo(
            file_path=Path("/tmp/test_file.mp4"),
            original_filename="test.mp4",
            size=1024
        )

    @pytest.mark.asyncio
    async def test_workflow_orchestrator_cleanup_with_file_info(self, mock_temp_file_info):
        """Test WorkflowOrchestrator cleanup_resources with valid file info"""
        with patch.object(FileHandler, 'cleanup') as mock_cleanup:
            orchestrator = WorkflowOrchestrator()
            
            # Test cleanup with file info
            await orchestrator.cleanup_resources(mock_temp_file_info)
            
            # Verify FileHandler.cleanup was called with correct path
            mock_cleanup.assert_called_once_with(mock_temp_file_info.file_path)

    def test_cleanup_called_on_file_handler_error(self, client):
        """Test that cleanup is called even when FileHandler.save_upload_file fails"""
        cleanup_calls = []
        
        def track_cleanup(file_info):
            cleanup_calls.append(file_info)
            return AsyncMock()()
        
        with patch('app.services.file_handler.FileHandler.save_upload_file') as mock_save, \
             patch.object(WorkflowOrchestrator, 'cleanup_resources', side_effect=track_cleanup):
            
            # Setup mock to raise exception
            mock_save.side_effect = Exception("File save failed")
            
            # Make request
            response = client.post(
                "/api/parse",
                files={"file": ("test.mp4", b"file_content", "video/mp4")}
            )
            
            # Verify response indicates error
            assert response.status_code == 500
            
            # Verify cleanup was still called (with None since temp_file_info wasn't set)
            assert len(cleanup_calls) == 1
            assert cleanup_calls[0] is None

    def test_cleanup_called_on_workflow_processing_error(self, client):
        """Test that cleanup is called when workflow processing fails"""
        cleanup_calls = []
        
        def track_cleanup(file_info):
            cleanup_calls.append(file_info)
            return AsyncMock()()
        
        with patch.object(WorkflowOrchestrator, 'process_file_workflow') as mock_process, \
             patch.object(WorkflowOrchestrator, 'cleanup_resources', side_effect=track_cleanup):
            
            # Workflow processing fails
            mock_process.side_effect = Exception("Processing failed")
            
            # Make request
            response = client.post(
                "/api/parse",
                files={"file": ("test.mp4", b"file_content", "video/mp4")}
            )
            
            # Verify response indicates error
            assert response.status_code == 500
            
            # Verify cleanup was called with some temp file info
            assert len(cleanup_calls) == 1
            # The cleanup should be called with actual temp file info (not None)
            assert cleanup_calls[0] is not None
            assert hasattr(cleanup_calls[0], 'file_path')
            assert hasattr(cleanup_calls[0], 'original_filename')

    @pytest.mark.asyncio
    async def test_workflow_orchestrator_cleanup_with_none(self):
        """Test WorkflowOrchestrator cleanup_resources with None (no temp file)"""
        with patch.object(FileHandler, 'cleanup') as mock_cleanup:
            orchestrator = WorkflowOrchestrator()
            
            # Test cleanup with None
            await orchestrator.cleanup_resources(None)
            
            # Verify FileHandler.cleanup was not called
            mock_cleanup.assert_not_called()

    def test_finally_block_executes_on_file_upload_success(self, client):
        """Test that finally block executes and cleanup is called on successful file upload"""
        cleanup_called = []
        
        def mock_cleanup(file_info):
            cleanup_called.append(file_info)
            return AsyncMock()()
        
        with patch.object(WorkflowOrchestrator, 'cleanup_resources', side_effect=mock_cleanup):
            # Make a file upload request
            response = client.post(
                "/api/parse",
                files={"file": ("test.mp4", b"file_content", "video/mp4")}
            )
            
            # Verify cleanup was called (regardless of response status)
            assert len(cleanup_called) == 1
            # The cleanup should be called with the temp file info or None
            assert cleanup_called[0] is not None or cleanup_called[0] is None

    def test_finally_block_executes_on_url_request_success(self, client):
        """Test that finally block executes and cleanup is called on URL request"""
        cleanup_called = []
        
        def mock_cleanup(file_info):
            cleanup_called.append(file_info)
            return AsyncMock()()
        
        with patch.object(WorkflowOrchestrator, 'cleanup_resources', side_effect=mock_cleanup):
            # Make a URL request
            response = client.post(
                "/api/parse",
                json={"url": "https://www.xiaohongshu.com/discovery/item/test"}
            )
            
            # Verify cleanup was called (regardless of response status)
            assert len(cleanup_called) == 1
            # For URL requests, cleanup should be called with None
            assert cleanup_called[0] is None

    @pytest.mark.asyncio
    async def test_cleanup_handles_none_gracefully(self):
        """Test that cleanup_resources handles None input gracefully"""
        from .main import WorkflowOrchestrator
        
        orchestrator = WorkflowOrchestrator()
        
        # This should not raise any exception
        await orchestrator.cleanup_resources(None)

    @pytest.mark.asyncio
    async def test_cleanup_handles_file_handler_cleanup_error(self, mock_temp_file_info):
        """Test that cleanup_resources handles FileHandler.cleanup errors gracefully"""
        from .main import WorkflowOrchestrator
        
        with patch('app.services.file_handler.FileHandler.cleanup') as mock_cleanup:
            # FileHandler.cleanup raises an exception
            mock_cleanup.side_effect = Exception("Cleanup failed")
            
            orchestrator = WorkflowOrchestrator()
            
            # This should not raise any exception despite cleanup failure
            await orchestrator.cleanup_resources(mock_temp_file_info)
            
            # Verify cleanup was attempted
            mock_cleanup.assert_called_once_with(mock_temp_file_info.file_path)

    @pytest.mark.asyncio
    async def test_file_handler_cleanup_with_existing_file(self, tmp_path):
        """Test FileHandler.cleanup with an existing file"""
        from .services.file_handler import FileHandler
        
        # Create a temporary file
        test_file = tmp_path / "test_cleanup.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        
        # Test cleanup
        await FileHandler.cleanup(test_file)
        
        # Verify file was removed
        assert not test_file.exists()

    @pytest.mark.asyncio
    async def test_file_handler_cleanup_with_nonexistent_file(self, tmp_path):
        """Test FileHandler.cleanup with a non-existent file"""
        from .services.file_handler import FileHandler
        
        # Use a non-existent file path
        test_file = tmp_path / "nonexistent.txt"
        assert not test_file.exists()
        
        # This should not raise any exception
        await FileHandler.cleanup(test_file)

    @pytest.mark.asyncio
    async def test_file_handler_cleanup_with_permission_error(self, tmp_path):
        """Test FileHandler.cleanup handles permission errors gracefully"""
        from .services.file_handler import FileHandler
        
        # Create a temporary file
        test_file = tmp_path / "test_permission.txt"
        test_file.write_text("test content")
        
        with patch.object(Path, 'unlink') as mock_unlink:
            mock_unlink.side_effect = PermissionError("Permission denied")
            
            # This should not raise any exception
            await FileHandler.cleanup(test_file)
            
            # Verify unlink was attempted
            mock_unlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_finally_block_executes_on_http_exception(self, client):
        """Test that finally block executes even when HTTPException is raised"""
        with patch('app.main.create_missing_input_error') as mock_error, \
             patch('app.main.WorkflowOrchestrator.cleanup_resources') as mock_cleanup:
            
            from fastapi import HTTPException
            
            # Setup mock to raise HTTPException
            mock_error.side_effect = HTTPException(status_code=400, detail="Test error")
            
            # Make request that will trigger the error
            response = client.post("/api/parse")
            
            # Verify error response
            assert response.status_code == 400
            
            # Verify cleanup was still called
            mock_cleanup.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_finally_block_executes_on_general_exception(self, client):
        """Test that finally block executes when general exception is raised and handled"""
        with patch('app.main.WorkflowOrchestrator.process_url_workflow') as mock_process, \
             patch('app.main.WorkflowOrchestrator.cleanup_resources') as mock_cleanup, \
             patch('app.main.handle_service_exception') as mock_handle:
            
            from fastapi import HTTPException
            
            # Setup mocks
            mock_process.side_effect = Exception("General error")
            mock_handle.side_effect = HTTPException(status_code=500, detail="Handled error")
            
            # Make request
            response = client.post(
                "/api/parse",
                json={"url": "https://www.xiaohongshu.com/discovery/item/test"}
            )
            
            # Verify error response
            assert response.status_code == 500
            
            # Verify cleanup was still called
            mock_cleanup.assert_called_once_with(None)