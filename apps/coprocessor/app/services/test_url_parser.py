from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from .url_parser import ShareURLParser, URLParserError, VideoInfo

# Test data
DOUYIN_SHARE_TEXT = "看看这个视频 https://v.douyin.com/ieFKhre/ 复制此链接，打开Dou音搜索，直接观看视频！"
XIAOHONGSHU_SHARE_TEXT = "49 【升级mac os26，变化太大了？ - 玩机国王 | 小红书 - 你的生活兴趣社区】 😆 3s1YuKFs000BYza 😆 https://www.xiaohongshu.com/discovery/item/68c94ab0000000001202ca84?source=webshare&xhsshare=pc_web&xsec_token=AB28Ibm6kG7-vTzwh_PBkMMTDJIS9vmYmKQHp3myYC8rE=&xsec_source=pc_share"
NO_URL_TEXT = "这是一段没有链接的文本"

DOUYIN_HTML_SAMPLE = """
<!DOCTYPE html>
<html>
<head><title>抖音视频</title></head>
<body>
<script>
window._ROUTER_DATA = {
    "loaderData": {
        "video_(id)/page": {
            "videoInfoRes": {
                "item_list": [
                    {
                        "id": "7123456789012345678",
                        "desc": "Amazing Video Title",
                        "video": {
                            "play_addr": {
                                "url_list": [
                                    "https://v26-web.douyinvod.com/test-videoplaywm.mp4"
                                ]
                            }
                        }
                    }
                ]
            }
        }
    }
};
</script>
</body>
</html>
"""

DOUYIN_HTML_INVALID = """
<!DOCTYPE html>
<html>
<head><title>抖音视频</title></head>
<body>
<p>No router data here</p>
</body>
</html>
"""


class TestShareURLParser:
    @pytest.fixture
    def parser(self):
        return ShareURLParser()

    @pytest.fixture
    def mock_httpx_response(self):
        mock_response = Mock()
        mock_response.text = DOUYIN_HTML_SAMPLE
        mock_response.status_code = 200
        return mock_response

    @pytest.fixture
    def mock_httpx_response_invalid(self):
        mock_response = Mock()
        mock_response.text = DOUYIN_HTML_INVALID
        mock_response.status_code = 200
        return mock_response

    @pytest.mark.asyncio
    async def test_successful_douyin_parsing(self, parser, mocker):
        """Test successful Douyin URL parsing with optimized logic"""
        # Mock httpx.AsyncClient
        mock_client = AsyncMock()

        # Mock the first request (redirect response)
        mock_redirect_response = AsyncMock()
        mock_redirect_response.url.path = "/share/video/7123456789012345678"

        # Mock the second request (HTML content)
        mock_html_response = AsyncMock()
        mock_html_response.text = DOUYIN_HTML_SAMPLE
        mock_html_response.raise_for_status = AsyncMock()

        # Set up the mock to return different responses for different calls
        mock_client.get.side_effect = [mock_redirect_response, mock_html_response]

        mock_async_client = mocker.patch("httpx.AsyncClient")
        mock_async_client.return_value.__aenter__.return_value = mock_client

        # Test parsing
        result = await parser.parse(DOUYIN_SHARE_TEXT)

        # Assertions
        assert isinstance(result, VideoInfo)
        assert result.platform == "douyin"
        assert result.video_id == "7123456789012345678"
        assert result.title == "Amazing Video Title"
        # Verify playwm was replaced with play
        assert "play.mp4" in result.download_url

        # Verify HTTP requests were made (2 calls: redirect + HTML)
        assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_xiaohongshu_parsing_success(self, parser, mocker):
        """Test successful Xiaohongshu parsing"""
        # Mock httpx.AsyncClient for the third-party API call
        mock_client = AsyncMock()

        # Mock API response with the structure you provided
        mock_api_response = AsyncMock()
        mock_api_response.json.return_value = {
            "code": 200,
            "message": "操作成功",
            "data": {
                "vid": "68c94ab0000000001202ca84",
                "host": "xiaohongshu",
                "hostAlias": "小红书",
                "displayTitle": "升级mac os26，变化太大了？",
                "status": "finish",
                "videoItemVoList": [
                    {
                        "baseUrl": "https://sns-video-hw.xhscdn.com/stream/test-video.mp4",
                        "quality": "未知",
                        "fileType": "video",
                        "canDownload": True,
                    }
                ],
            },
        }

        mock_client.get.return_value = mock_api_response

        mock_async_client = mocker.patch("httpx.AsyncClient")
        mock_async_client.return_value.__aenter__.return_value = mock_client

        # Test parsing
        result = await parser.parse(XIAOHONGSHU_SHARE_TEXT)

        # Assertions
        assert isinstance(result, VideoInfo)
        assert result.platform == "xiaohongshu"
        assert result.video_id == "68c94ab0000000001202ca84"
        assert result.title == "升级mac os26，变化太大了？"
        assert "sns-video-hw.xhscdn.com" in result.download_url

    @pytest.mark.asyncio
    async def test_no_url_in_text(self, parser):
        """Test that text without URL raises URLParserError"""
        with pytest.raises(URLParserError, match="No URL found in the provided text"):
            await parser.parse(NO_URL_TEXT)

    @pytest.mark.asyncio
    async def test_douyin_parsing_failure_invalid_html(self, parser, mocker):
        """Test Douyin parsing failure when HTML structure changes"""
        # Mock httpx.AsyncClient with invalid HTML
        mock_client = AsyncMock()

        # Mock the first request (redirect response)
        mock_redirect_response = AsyncMock()
        mock_redirect_response.url.path = "/share/video/7123456789012345678"

        # Mock the second request (invalid HTML content)
        mock_html_response = AsyncMock()
        mock_html_response.text = DOUYIN_HTML_INVALID
        mock_html_response.raise_for_status = AsyncMock()

        # Set up the mock to return different responses for different calls
        mock_client.get.side_effect = [mock_redirect_response, mock_html_response]

        mock_async_client = mocker.patch("httpx.AsyncClient")
        mock_async_client.return_value.__aenter__.return_value = mock_client

        # Test parsing failure - should match the new error message format
        with pytest.raises(URLParserError, match="从HTML中解析视频信息失败"):
            await parser.parse(DOUYIN_SHARE_TEXT)

    @pytest.mark.asyncio
    async def test_http_request_failure(self, parser, mocker):
        """Test handling of HTTP request failures"""
        # Mock httpx.AsyncClient to raise exception
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.RequestError("Network error")

        mock_async_client = mocker.patch("httpx.AsyncClient")
        mock_async_client.return_value.__aenter__.return_value = mock_client

        # Test network error handling
        with pytest.raises(URLParserError, match="Failed to fetch video page"):
            await parser.parse(DOUYIN_SHARE_TEXT)

    @pytest.mark.asyncio
    async def test_unsupported_platform(self, parser):
        """Test handling of unsupported platform URLs"""
        unsupported_text = "Check this out https://www.youtube.com/watch?v=123"

        with pytest.raises(URLParserError, match="Unsupported platform"):
            await parser.parse(unsupported_text)
