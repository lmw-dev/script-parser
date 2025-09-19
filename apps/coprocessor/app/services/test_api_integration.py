"""
API端点集成测试
验证/api/parse端点与OSS上传器和ASR服务的集成
"""

from io import BytesIO
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from ..main import app
from .oss_uploader import OSSUploaderError


class TestAPIIntegration:
    """API端点集成测试"""

    def setup_method(self):
        """设置测试客户端"""
        self.client = TestClient(app)

    @patch("app.main.create_oss_uploader_from_env")
    @patch("app.main.ASRService")
    def test_parse_file_with_oss_integration_success(
        self, mock_asr_service_class, mock_create_oss_uploader
    ):
        """测试文件上传端点的OSS集成成功场景"""
        # 1. Mock OSS上传器
        mock_oss_uploader = Mock()
        mock_create_oss_uploader.return_value = mock_oss_uploader

        # 2. Mock ASR服务实例和转录结果
        from unittest.mock import AsyncMock

        mock_asr_service = Mock()
        mock_asr_service.transcribe_from_file = AsyncMock(
            return_value="这是通过OSS集成转录的文本"
        )
        mock_asr_service_class.return_value = mock_asr_service

        # 3. 创建测试文件
        test_file_content = b"fake video content"
        test_file = BytesIO(test_file_content)

        # 4. 发送文件上传请求
        response = self.client.post(
            "/api/parse", files={"file": ("test_video.mp4", test_file, "video/mp4")}
        )

        # 5. 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["transcript"] == "这是通过OSS集成转录的文本"
        assert "file_info" in data["data"]["analysis"]

        # 6. 验证OSS上传器被创建和ASR服务被正确初始化
        mock_create_oss_uploader.assert_called_once()
        mock_asr_service_class.assert_called_once_with(oss_uploader=mock_oss_uploader)

    @patch("app.main.create_oss_uploader_from_env")
    def test_parse_file_with_oss_upload_error(self, mock_create_oss_uploader):
        """测试文件上传端点的OSS上传错误场景"""
        # 1. Mock OSS上传器创建失败
        mock_create_oss_uploader.side_effect = OSSUploaderError("OSS配置错误")

        # 2. 创建测试文件
        test_file_content = b"fake video content"
        test_file = BytesIO(test_file_content)

        # 3. 发送文件上传请求
        response = self.client.post(
            "/api/parse", files={"file": ("test_video.mp4", test_file, "video/mp4")}
        )

        # 4. 验证响应 - 应该成功返回但包含错误信息
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Processing failed" in data["data"]["transcript"]

    @patch("app.main.create_oss_uploader_from_env")
    @patch("app.main.ASRService")
    def test_parse_file_with_asr_error(
        self, mock_asr_service_class, mock_create_oss_uploader
    ):
        """测试文件上传端点的ASR错误场景"""
        # 1. Mock OSS上传器正常
        mock_oss_uploader = Mock()
        mock_create_oss_uploader.return_value = mock_oss_uploader

        # 2. Mock ASR服务实例和转录失败
        from unittest.mock import AsyncMock

        mock_asr_service = Mock()
        mock_asr_service.transcribe_from_file = AsyncMock(
            side_effect=Exception("ASR服务不可用")
        )
        mock_asr_service_class.return_value = mock_asr_service

        # 3. 创建测试文件
        test_file_content = b"fake video content"
        test_file = BytesIO(test_file_content)

        # 4. 发送文件上传请求
        response = self.client.post(
            "/api/parse", files={"file": ("test_video.mp4", test_file, "video/mp4")}
        )

        # 5. 验证响应 - 应该成功返回但包含错误信息
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Processing failed" in data["data"]["transcript"]

    def test_parse_file_without_file(self):
        """测试没有文件的请求"""
        response = self.client.post("/api/parse")
        assert response.status_code == 400
        assert "Either URL or file must be provided" in response.json()["detail"]

    def test_parse_url_success(self):
        """测试URL解析成功场景（不涉及OSS）"""
        # 这个测试验证URL解析功能仍然正常工作
        with patch("app.main.ShareURLParser.parse") as mock_parse:
            # Mock URL解析结果
            from .url_parser import VideoInfo

            mock_video_info = VideoInfo(
                video_id="test123",
                platform="douyin",
                title="测试视频",
                download_url="https://example.com/video.mp4",
            )
            mock_parse.return_value = mock_video_info

            # Mock ASR转录
            with patch("app.main.ASRService") as mock_asr_service_class:
                from unittest.mock import AsyncMock

                mock_asr_service = Mock()
                mock_asr_service.transcribe_from_url = AsyncMock(
                    return_value="URL视频转录文本"
                )
                mock_asr_service_class.return_value = mock_asr_service

                response = self.client.post(
                    "/api/parse", json={"url": "https://v.douyin.com/test123/"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["data"]["transcript"] == "URL视频转录文本"
                assert data["data"]["analysis"]["video_info"]["platform"] == "douyin"
