"""
OSS Uploader Service Tests
测试阿里云OSS文件上传服务
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import oss2
import pytest

from app.services.oss_uploader import (
    OSSUploader,
    OSSUploaderError,
    OSSUploadResult,
    create_oss_uploader_from_env,
)


class TestOSSUploader:
    """OSS Uploader 服务测试"""

    def test_init_with_credentials(self):
        """测试使用凭证初始化"""
        uploader = OSSUploader(
            access_key_id="test-key-id",
            access_key_secret="test-key-secret",
            endpoint="https://oss-cn-beijing.aliyuncs.com",
            bucket_name="test-bucket",
        )

        assert uploader.access_key_id == "test-key-id"
        assert uploader.access_key_secret == "test-key-secret"
        assert uploader.endpoint == "https://oss-cn-beijing.aliyuncs.com"
        assert uploader.bucket_name == "test-bucket"

    @patch("oss2.Bucket")
    @patch("oss2.Auth")
    def test_upload_file_success(self, mock_auth, mock_bucket_class, mocker):
        """测试成功上传文件"""
        # 创建模拟对象
        mock_auth_instance = Mock()
        mock_auth.return_value = mock_auth_instance

        mock_bucket = Mock()
        mock_bucket_class.return_value = mock_bucket

        # 模拟上传成功的响应
        mock_result = Mock()
        mock_result.etag = "test-etag-123"
        mock_bucket.put_object_from_file.return_value = mock_result

        # 创建上传器实例
        uploader = OSSUploader(
            access_key_id="test-key-id",
            access_key_secret="test-key-secret",
            endpoint="https://oss-cn-beijing.aliyuncs.com",
            bucket_name="test-bucket",
        )

        # 创建测试文件路径
        test_file_path = Path("/tmp/test_audio.wav")

        # 模拟时间戳
        with patch("time.time", return_value=1234567890):
            result = uploader.upload_file(test_file_path)

        # 验证结果
        assert isinstance(result, OSSUploadResult)
        assert (
            result.file_url
            == "https://test-bucket.oss-cn-beijing.aliyuncs.com/audio/1234567890_test_audio.wav"
        )
        assert result.object_key == "audio/1234567890_test_audio.wav"

        # 验证调用
        mock_auth.assert_called_once_with("test-key-id", "test-key-secret")
        mock_bucket_class.assert_called_once_with(
            mock_auth_instance, "https://oss-cn-beijing.aliyuncs.com", "test-bucket"
        )
        mock_bucket.put_object_from_file.assert_called_once_with(
            "audio/1234567890_test_audio.wav",
            test_file_path,
            headers={"x-oss-object-acl": "public-read"},
        )

    @patch("oss2.Bucket")
    @patch("oss2.Auth")
    def test_upload_file_oss_error(self, mock_auth, mock_bucket_class):
        """测试OSS上传异常处理"""
        # 创建模拟对象
        mock_auth_instance = Mock()
        mock_auth.return_value = mock_auth_instance

        mock_bucket = Mock()
        mock_bucket_class.return_value = mock_bucket

        # 模拟OSS异常
        mock_bucket.put_object_from_file.side_effect = oss2.exceptions.OssError(
            400,
            {"x-oss-request-id": "test-request-id"},
            "test-body",
            {"error": "upload_failed"},
        )

        # 创建上传器实例
        uploader = OSSUploader(
            access_key_id="test-key-id",
            access_key_secret="test-key-secret",
            endpoint="https://oss-cn-beijing.aliyuncs.com",
            bucket_name="test-bucket",
        )

        # 测试异常处理
        test_file_path = Path("/tmp/test_audio.wav")

        with pytest.raises(OSSUploaderError, match="OSS upload failed"):
            uploader.upload_file(test_file_path)

    @patch("oss2.Bucket")
    @patch("oss2.Auth")
    def test_upload_file_generic_error(self, mock_auth, mock_bucket_class):
        """测试通用异常处理"""
        # 创建模拟对象
        mock_auth_instance = Mock()
        mock_auth.return_value = mock_auth_instance

        mock_bucket = Mock()
        mock_bucket_class.return_value = mock_bucket

        # 模拟通用异常
        mock_bucket.put_object_from_file.side_effect = Exception("Network error")

        # 创建上传器实例
        uploader = OSSUploader(
            access_key_id="test-key-id",
            access_key_secret="test-key-secret",
            endpoint="https://oss-cn-beijing.aliyuncs.com",
            bucket_name="test-bucket",
        )

        # 测试异常处理
        test_file_path = Path("/tmp/test_audio.wav")

        with pytest.raises(OSSUploaderError, match="OSS uploader error"):
            uploader.upload_file(test_file_path)

    @patch("oss2.Bucket")
    @patch("oss2.Auth")
    def test_ensure_bucket_exists_success(self, mock_auth, mock_bucket_class):
        """测试确保bucket存在 - 成功情况"""
        # 创建模拟对象
        mock_auth_instance = Mock()
        mock_auth.return_value = mock_auth_instance

        mock_bucket = Mock()
        mock_bucket_class.return_value = mock_bucket

        # 模拟bucket存在
        mock_bucket.get_bucket_info.return_value = Mock()

        # 创建上传器实例
        uploader = OSSUploader(
            access_key_id="test-key-id",
            access_key_secret="test-key-secret",
            endpoint="https://oss-cn-beijing.aliyuncs.com",
            bucket_name="test-bucket",
        )

        # 测试确保bucket存在
        result = uploader.ensure_bucket_exists()

        assert result is True
        mock_bucket.get_bucket_info.assert_called_once()

    @patch("oss2.Bucket")
    @patch("oss2.Auth")
    def test_ensure_bucket_exists_create_bucket(self, mock_auth, mock_bucket_class):
        """测试确保bucket存在 - 需要创建bucket"""
        # 创建模拟对象
        mock_auth_instance = Mock()
        mock_auth.return_value = mock_auth_instance

        mock_bucket = Mock()
        mock_bucket_class.return_value = mock_bucket

        # 模拟bucket不存在，需要创建
        mock_bucket.get_bucket_info.side_effect = oss2.exceptions.NoSuchBucket(
            404, {"x-oss-request-id": "test-request-id"}, "test-body", {}
        )
        mock_bucket.create_bucket.return_value = Mock()

        # 创建上传器实例
        uploader = OSSUploader(
            access_key_id="test-key-id",
            access_key_secret="test-key-secret",
            endpoint="https://oss-cn-beijing.aliyuncs.com",
            bucket_name="test-bucket",
        )

        # 测试确保bucket存在
        result = uploader.ensure_bucket_exists()

        assert result is True
        mock_bucket.get_bucket_info.assert_called_once()
        mock_bucket.create_bucket.assert_called_once_with(oss2.BUCKET_ACL_PUBLIC_READ)

    @patch("oss2.Bucket")
    @patch("oss2.Auth")
    def test_ensure_bucket_exists_error(self, mock_auth, mock_bucket_class):
        """测试确保bucket存在 - 错误情况"""
        # 创建模拟对象
        mock_auth_instance = Mock()
        mock_auth.return_value = mock_auth_instance

        mock_bucket = Mock()
        mock_bucket_class.return_value = mock_bucket

        # 模拟OSS错误
        mock_bucket.get_bucket_info.side_effect = oss2.exceptions.OssError(
            500, {"x-oss-request-id": "test-request-id"}, "test-body", {}
        )

        # 创建上传器实例
        uploader = OSSUploader(
            access_key_id="test-key-id",
            access_key_secret="test-key-secret",
            endpoint="https://oss-cn-beijing.aliyuncs.com",
            bucket_name="test-bucket",
        )

        # 测试错误处理
        with pytest.raises(OSSUploaderError, match="Failed to check bucket"):
            uploader.ensure_bucket_exists()


class TestOSSUploaderFactory:
    """OSS Uploader 工厂函数测试"""

    @patch.dict(
        os.environ,
        {
            "ALIBABA_CLOUD_ACCESS_KEY_ID": "env-key-id",
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "env-key-secret",
            "OSS_ENDPOINT": "https://oss-cn-beijing.aliyuncs.com",
            "OSS_BUCKET_NAME": "env-bucket",
        },
    )
    def test_create_from_env_success(self):
        """测试从环境变量成功创建上传器"""
        uploader = create_oss_uploader_from_env()

        assert uploader.access_key_id == "env-key-id"
        assert uploader.access_key_secret == "env-key-secret"
        assert uploader.endpoint == "https://oss-cn-beijing.aliyuncs.com"
        assert uploader.bucket_name == "env-bucket"

    @patch.dict(os.environ, {}, clear=True)
    def test_create_from_env_missing_access_key_id(self):
        """测试缺少ACCESS_KEY_ID时抛出异常"""
        with pytest.raises(
            ValueError, match="ALIBABA_CLOUD_ACCESS_KEY_ID environment variable not set"
        ):
            create_oss_uploader_from_env()

    @patch.dict(os.environ, {"ALIBABA_CLOUD_ACCESS_KEY_ID": "env-key-id"}, clear=True)
    def test_create_from_env_missing_access_key_secret(self):
        """测试缺少ACCESS_KEY_SECRET时抛出异常"""
        with pytest.raises(
            ValueError,
            match="ALIBABA_CLOUD_ACCESS_KEY_SECRET environment variable not set",
        ):
            create_oss_uploader_from_env()

    @patch.dict(
        os.environ,
        {
            "ALIBABA_CLOUD_ACCESS_KEY_ID": "env-key-id",
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "env-key-secret",
        },
        clear=True,
    )
    def test_create_from_env_with_defaults(self):
        """测试使用默认值创建上传器"""
        uploader = create_oss_uploader_from_env()

        assert uploader.access_key_id == "env-key-id"
        assert uploader.access_key_secret == "env-key-secret"
        assert uploader.endpoint == "https://oss-cn-beijing.aliyuncs.com"  # 默认值
        assert uploader.bucket_name == "scriptparser-audio"  # 默认值


class TestOSSUploadResult:
    """OSS Upload Result 模型测试"""

    def test_oss_upload_result_creation(self):
        """测试创建OSS上传结果对象"""
        result = OSSUploadResult(
            file_url="https://test-bucket.oss-cn-beijing.aliyuncs.com/audio/test.wav",
            object_key="audio/test.wav",
        )

        assert (
            result.file_url
            == "https://test-bucket.oss-cn-beijing.aliyuncs.com/audio/test.wav"
        )
        assert result.object_key == "audio/test.wav"

    def test_oss_upload_result_validation(self):
        """测试OSS上传结果对象验证"""
        # 测试必需字段
        with pytest.raises(ValueError):
            OSSUploadResult()  # 缺少必需字段


class TestOSSUploaderError:
    """OSS Uploader Error 异常测试"""

    def test_oss_uploader_error_creation(self):
        """测试创建OSS上传器异常"""
        error = OSSUploaderError("Test error message")
        assert str(error) == "Test error message"

    def test_oss_uploader_error_inheritance(self):
        """测试OSS上传器异常继承关系"""
        error = OSSUploaderError("Test error")
        assert isinstance(error, Exception)
