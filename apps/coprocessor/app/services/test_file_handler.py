from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import UploadFile

from .file_handler import FileHandler, FileHandlerError, TempFileInfo


class TestFileHandler:
    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing"""
        return tmp_path / "test_scriptparser"

    @pytest.fixture
    def file_handler(self, temp_dir):
        """Create FileHandler instance with test directory"""
        return FileHandler(temp_dir=temp_dir)

    @pytest.fixture
    def mock_upload_file(self):
        """Create mock UploadFile object"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test_video.mp4"
        mock_file.size = 1024
        mock_file.read = AsyncMock(return_value=b"mock_video_content")
        return mock_file

    @pytest.fixture
    def mock_unsafe_upload_file(self):
        """Create mock UploadFile with unsafe filename"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "../../../etc/passwd"
        mock_file.size = 512
        mock_file.read = AsyncMock(return_value=b"malicious_content")
        return mock_file

    @pytest.fixture
    def mock_aiofiles_open(self, mocker):
        """Mock aiofiles.open for testing"""
        mock_file = AsyncMock()
        mock_open = mocker.patch("aiofiles.open")
        mock_open.return_value.__aenter__.return_value = mock_file
        return mock_open, mock_file

    @pytest.mark.asyncio
    async def test_save_upload_file_success(
        self, file_handler, mock_upload_file, mock_aiofiles_open, mocker
    ):
        """Test successful file saving"""
        mock_open, mock_file = mock_aiofiles_open

        # Mock Path.stat() for file size
        mock_stat = mocker.patch("pathlib.Path.stat")
        mock_stat.return_value.st_size = 1024

        # Mock uuid generation for predictable testing
        test_uuid = "12345678-1234-5678-9012-123456789abc"
        mocker.patch("uuid.uuid4", return_value=Mock(__str__=lambda x: test_uuid))

        # Test file saving
        result = await file_handler.save_upload_file(mock_upload_file)

        # Assertions
        assert isinstance(result, TempFileInfo)
        assert result.original_filename == "test_video.mp4"
        assert result.size == 1024
        assert str(result.file_path).endswith(f"{test_uuid}-test_video.mp4")

        # Verify file operations
        mock_upload_file.read.assert_called_once()
        mock_open.assert_called_once()
        mock_file.write.assert_called_once_with(b"mock_video_content")

    @pytest.mark.asyncio
    async def test_save_upload_file_unsafe_filename(
        self, file_handler, mock_unsafe_upload_file, mock_aiofiles_open, mocker
    ):
        """Test filename sanitization for unsafe filenames"""
        mock_open, mock_file = mock_aiofiles_open

        # Mock Path.stat() for file size
        mock_stat = mocker.patch("pathlib.Path.stat")
        mock_stat.return_value.st_size = 512

        # Mock uuid generation
        test_uuid = "87654321-4321-8765-2109-876543210fed"
        mocker.patch("uuid.uuid4", return_value=Mock(__str__=lambda x: test_uuid))

        # Test file saving with unsafe filename
        result = await file_handler.save_upload_file(mock_unsafe_upload_file)

        # Assertions - filename should be sanitized
        assert isinstance(result, TempFileInfo)
        assert result.original_filename == "etc_passwd"  # Sanitized by secure_filename
        assert result.size == 512
        assert "etc_passwd" in str(result.file_path)
        assert "../" not in str(result.file_path)

        # Verify file operations
        mock_unsafe_upload_file.read.assert_called_once()
        mock_open.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_success(self, mocker):
        """Test successful file cleanup"""
        # Mock Path.unlink()
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.unlink = Mock()

        # Test cleanup
        await FileHandler.cleanup(mock_path)

        # Verify file was removed
        mock_path.unlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_file_not_exists(self, mocker):
        """Test cleanup when file doesn't exist (should not raise error)"""
        # Mock Path that doesn't exist
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = False
        mock_path.unlink = Mock()

        # Test cleanup - should not raise error
        await FileHandler.cleanup(mock_path)

        # Verify unlink was not called
        mock_path.unlink.assert_not_called()

    @pytest.mark.asyncio
    async def test_cleanup_permission_error(self, mocker):
        """Test cleanup with permission error (should not raise error)"""
        # Mock Path.unlink() to raise PermissionError
        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.unlink.side_effect = PermissionError("Permission denied")

        # Test cleanup - should not raise error
        await FileHandler.cleanup(mock_path)

        # Verify unlink was called but error was handled
        mock_path.unlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_upload_file_io_error(
        self, file_handler, mock_upload_file, mocker
    ):
        """Test file saving with I/O error"""
        # Mock aiofiles.open to raise IOError
        mock_open = mocker.patch("aiofiles.open")
        mock_open.side_effect = OSError("Disk full")

        # Test file saving - should raise FileHandlerError
        with pytest.raises(FileHandlerError, match="Failed to save uploaded file"):
            await file_handler.save_upload_file(mock_upload_file)

    @pytest.mark.asyncio
    async def test_save_upload_file_permission_error(
        self, file_handler, mock_upload_file, mocker
    ):
        """Test file saving with permission error"""
        # Mock aiofiles.open to raise PermissionError
        mock_open = mocker.patch("aiofiles.open")
        mock_open.side_effect = PermissionError("Permission denied")

        # Test file saving - should raise FileHandlerError
        with pytest.raises(FileHandlerError, match="Failed to save uploaded file"):
            await file_handler.save_upload_file(mock_upload_file)

    @pytest.mark.asyncio
    async def test_save_upload_file_no_filename(
        self, file_handler, mock_aiofiles_open, mocker
    ):
        """Test file saving when upload file has no filename"""
        mock_open, mock_file = mock_aiofiles_open

        # Create upload file without filename
        mock_file_no_name = Mock(spec=UploadFile)
        mock_file_no_name.filename = None
        mock_file_no_name.size = 256
        mock_file_no_name.read = AsyncMock(return_value=b"content")

        # Mock Path.stat() for file size
        mock_stat = mocker.patch("pathlib.Path.stat")
        mock_stat.return_value.st_size = 256

        # Mock uuid generation
        test_uuid = "11111111-2222-3333-4444-555555555555"
        mocker.patch("uuid.uuid4", return_value=Mock(__str__=lambda x: test_uuid))

        # Test file saving
        result = await file_handler.save_upload_file(mock_file_no_name)

        # Assertions
        assert isinstance(result, TempFileInfo)
        assert result.original_filename == "unknown"  # Default filename
        assert result.size == 256

    def test_file_handler_init_creates_directory(self, temp_dir):
        """Test that FileHandler creates temporary directory on init"""
        # Ensure directory doesn't exist initially
        assert not temp_dir.exists()

        # Create FileHandler
        FileHandler(temp_dir=temp_dir)

        # Verify directory was created
        assert temp_dir.exists()
        assert temp_dir.is_dir()

    def test_temp_file_info_model(self):
        """Test TempFileInfo Pydantic model"""
        file_path = Path("/tmp/test/file.mp4")

        temp_file_info = TempFileInfo(
            file_path=file_path, original_filename="video.mp4", size=2048
        )

        assert temp_file_info.file_path == file_path
        assert temp_file_info.original_filename == "video.mp4"
        assert temp_file_info.size == 2048

    def test_file_handler_error_exception(self):
        """Test FileHandlerError custom exception"""
        error_message = "Test error message"
        error = FileHandlerError(error_message)

        assert error.message == error_message
        assert str(error) == error_message
