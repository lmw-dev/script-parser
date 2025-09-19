"""
阿里云OSS文件上传服务
基于 oss2 库实现
"""

import os
import time
from pathlib import Path

import oss2
from pydantic import BaseModel


class OSSUploaderError(Exception):
    """Custom exception for OSS Uploader errors."""

    pass


class OSSUploadResult(BaseModel):
    """OSS上传结果模型"""

    file_url: str
    object_key: str


class OSSUploader:
    """OSS文件上传器 - 处理音频文件上传到阿里云OSS"""

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        bucket_name: str,
    ):
        """
        初始化OSS上传器

        Args:
            access_key_id: 阿里云Access Key ID
            access_key_secret: 阿里云Access Key Secret
            endpoint: OSS服务端点
            bucket_name: OSS存储桶名称
        """
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name

        # 初始化OSS认证和存储桶
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)

    def upload_file(self, local_file_path: Path) -> OSSUploadResult:
        """
        上传文件到OSS并返回公开URL

        Args:
            local_file_path: 本地文件路径

        Returns:
            OSS上传结果，包含文件URL和对象键

        Raises:
            OSSUploaderError: 当上传失败时
        """
        try:
            # 1. 生成唯一的对象键名
            timestamp = int(time.time())
            filename = local_file_path.name
            object_key = f"audio/{timestamp}_{filename}"

            # 2. 上传文件并设置公共读取权限
            self.bucket.put_object_from_file(
                object_key, local_file_path, headers={"x-oss-object-acl": "public-read"}
            )

            # 3. 构建公开访问URL
            # 从endpoint中提取region信息
            # endpoint格式: https://oss-cn-beijing.aliyuncs.com
            region = self.endpoint.split("oss-")[1].split(".")[0]
            file_url = (
                f"https://{self.bucket_name}.oss-{region}.aliyuncs.com/{object_key}"
            )

            return OSSUploadResult(file_url=file_url, object_key=object_key)

        except oss2.exceptions.OssError as e:
            raise OSSUploaderError(f"OSS upload failed: {str(e)}") from e
        except Exception as e:
            raise OSSUploaderError(f"OSS uploader error: {str(e)}") from e

    def ensure_bucket_exists(self) -> bool:
        """
        确保bucket存在，不存在则创建

        Returns:
            True if bucket exists or was created successfully

        Raises:
            OSSUploaderError: 当bucket操作失败时
        """
        try:
            # 检查bucket是否存在
            self.bucket.get_bucket_info()
            return True
        except oss2.exceptions.NoSuchBucket:
            try:
                # 创建bucket并设置公共读取权限
                self.bucket.create_bucket(oss2.BUCKET_ACL_PUBLIC_READ)
                return True
            except oss2.exceptions.OssError as e:
                raise OSSUploaderError(f"Failed to create bucket: {str(e)}") from e
        except oss2.exceptions.OssError as e:
            raise OSSUploaderError(f"Failed to check bucket: {str(e)}") from e


def create_oss_uploader_from_env() -> OSSUploader:
    """
    从环境变量创建OSS上传器实例

    Returns:
        配置好的OSS上传器实例

    Raises:
        ValueError: 当必需的环境变量未设置时
    """
    # 读取必需的环境变量
    access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
    if not access_key_id:
        raise ValueError("ALIBABA_CLOUD_ACCESS_KEY_ID environment variable not set.")

    access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    if not access_key_secret:
        raise ValueError(
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET environment variable not set."
        )

    # 读取可选的环境变量，提供默认值
    endpoint = os.getenv("OSS_ENDPOINT", "https://oss-cn-beijing.aliyuncs.com")
    bucket_name = os.getenv("OSS_BUCKET_NAME", "scriptparser-audio")

    return OSSUploader(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        endpoint=endpoint,
        bucket_name=bucket_name,
    )
