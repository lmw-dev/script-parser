import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from pydantic import BaseModel
from werkzeug.utils import secure_filename

# Default temporary directory
TEMP_DIR = Path("/tmp/scriptparser")


class TempFileInfo(BaseModel):
    """Information about a temporarily saved file"""
    file_path: Path
    original_filename: str
    size: int


class FileHandlerError(Exception):
    """Custom exception for file handling errors"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class FileHandler:
    """Service for handling temporary file operations"""

    def __init__(self, temp_dir: Path = TEMP_DIR):
        """
        Initialize FileHandler with configurable temporary directory

        Args:
            temp_dir: Directory for temporary file storage
        """
        self.temp_dir = temp_dir
        # Create directory if it doesn't exist
        self.temp_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    async def save_upload_file(self, file: UploadFile) -> TempFileInfo:
        """
        Save uploaded file to temporary storage with security measures

        Args:
            file: FastAPI UploadFile object

        Returns:
            TempFileInfo: Information about the saved file

        Raises:
            FileHandlerError: When file operations fail
        """
        try:
            # Get original filename and sanitize it
            original_filename = file.filename or "unknown"
            safe_filename = secure_filename(original_filename)

            # Generate unique filename to prevent conflicts
            unique_id = str(uuid.uuid4())
            unique_filename = f"{unique_id}-{safe_filename}"

            # Create full file path
            file_path = self.temp_dir / unique_filename

            # Read file content
            content = await file.read()

            # Write file asynchronously
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            # Get file size from saved file
            file_size = file_path.stat().st_size

            return TempFileInfo(
                file_path=file_path,
                original_filename=safe_filename,
                size=file_size
            )

        except Exception as e:
            raise FileHandlerError(f"Failed to save uploaded file: {str(e)}") from e

    @staticmethod
    async def cleanup(file_path: Path) -> None:
        """
        Remove temporary file with graceful error handling

        Args:
            file_path: Path to file to remove

        Note:
            This method handles errors gracefully and does not raise exceptions
            to ensure cleanup doesn't break the main application flow
        """
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            # Log error in production, but don't raise to avoid breaking cleanup
            # In a production environment, you might want to log this error
            pass
