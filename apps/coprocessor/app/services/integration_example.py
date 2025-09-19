"""
OSS Uploader 与 ASR Service 集成示例
演示如何将本地文件上传到OSS，然后使用ASR服务进行转录
"""

import asyncio
from pathlib import Path

from app.services.asr_service import ASRService
from app.services.oss_uploader import create_oss_uploader_from_env


async def transcribe_local_file_via_oss(local_file_path: Path) -> str:
    """
    通过OSS上传本地文件，然后使用ASR服务进行转录

    Args:
        local_file_path: 本地音频文件路径

    Returns:
        转录的文本内容

    Raises:
        Exception: 当上传或转录失败时
    """
    try:
        # 1. 创建OSS上传器
        oss_uploader = create_oss_uploader_from_env()

        # 2. 确保bucket存在
        oss_uploader.ensure_bucket_exists()

        # 3. 上传文件到OSS
        upload_result = oss_uploader.upload_file(local_file_path)
        print(f"文件已上传到OSS: {upload_result.file_url}")

        # 4. 创建ASR服务
        asr_service = ASRService()

        # 5. 使用OSS URL进行转录
        transcript = await asr_service.transcribe_from_url(upload_result.file_url)
        print(f"转录完成: {transcript}")

        return transcript

    except Exception as e:
        print(f"集成处理失败: {str(e)}")
        raise


async def main():
    """主函数 - 演示集成流程"""
    # 示例：处理本地音频文件
    # 注意：这里使用示例路径，实际使用时需要提供真实的音频文件路径
    example_file = Path("/tmp/example_audio.wav")

    if example_file.exists():
        try:
            result = await transcribe_local_file_via_oss(example_file)
            print(f"最终转录结果: {result}")
        except Exception as e:
            print(f"处理失败: {str(e)}")
    else:
        print(f"示例文件不存在: {example_file}")
        print("请提供一个真实的音频文件路径进行测试")


if __name__ == "__main__":
    asyncio.run(main())
