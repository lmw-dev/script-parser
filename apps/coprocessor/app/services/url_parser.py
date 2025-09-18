import json
import re
from typing import Any

import httpx
from pydantic import BaseModel


class VideoInfo(BaseModel):
    """Video information extracted from sharing URL"""

    video_id: str
    platform: str
    title: str
    download_url: str


class URLParserError(Exception):
    """Custom exception for URL parsing errors"""

    pass


class ShareURLParser:
    """URL parser for extracting video information from platform sharing URLs"""

    def __init__(self):
        # 模拟移动端访问的请求头，基于成功的 PoC 实现
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1"
        }

    async def parse(self, share_text: str) -> VideoInfo:
        """
        Parse video information from sharing text containing URL

        Args:
            share_text: Text containing video sharing URL

        Returns:
            VideoInfo: Structured video information

        Raises:
            URLParserError: When parsing fails or no URL found
            NotImplementedError: When platform is not supported
        """
        # Extract URL from text
        url = self._extract_url_from_text(share_text)

        # Identify platform and route to appropriate parser
        platform = self._identify_platform(url)

        if platform == "douyin":
            return await self._parse_douyin(url)
        elif platform == "xiaohongshu":
            return await self._parse_xiaohongshu(url)
        else:
            raise URLParserError(f"Unsupported platform in URL: {url}")

    def _extract_url_from_text(self, text: str) -> str:
        """Extract URL from sharing text using regex"""
        url_pattern = r"https?://[^\s]+"
        matches = re.findall(url_pattern, text)
        if not matches:
            raise URLParserError("No URL found in the provided text")
        return matches[0]  # Return first URL found

    def _identify_platform(self, url: str) -> str:
        """Identify platform based on URL domain"""
        if "douyin.com" in url:
            return "douyin"
        elif "xiaohongshu.com" in url:
            return "xiaohongshu"
        else:
            raise URLParserError(f"Unsupported platform in URL: {url}")

    async def _parse_douyin(self, url: str) -> VideoInfo:
        """Parse Douyin video URL and extract video information - 基于成功的 PoC 实现"""
        try:
            async with httpx.AsyncClient(headers=self.headers) as client:
                # 第一步：跟随重定向获取 video_id
                share_response = await client.get(url, follow_redirects=True)
                video_id = share_response.url.path.rstrip("/").split("/")[-1]

                # 第二步：构造标准的抖音视频页面 URL
                standard_url = f"https://www.iesdouyin.com/share/video/{video_id}"

                # 第三步：获取视频页面内容
                response = await client.get(standard_url)
                response.raise_for_status()
                html_content = response.text

                # 第四步：提取并解析 _ROUTER_DATA
                router_data = self._extract_router_data_optimized(html_content)

                # 第五步：解析视频信息
                return self._parse_douyin_router_data_optimized(router_data, video_id)

        except httpx.RequestError as e:
            raise URLParserError(f"Failed to fetch video page: {str(e)}") from e
        except Exception as e:
            raise URLParserError(f"Failed to parse Douyin video: {str(e)}") from e

    async def _parse_xiaohongshu(self, url: str) -> VideoInfo:
        """Parse Xiaohongshu video URL and extract video information"""
        try:
            # 提取小红书的 item ID
            item_id = self._extract_xiaohongshu_item_id(url)

            # 调用第三方解析服务
            video_data = await self._fetch_xiaohongshu_data(item_id)

            # 解析返回的数据
            return self._parse_xiaohongshu_data(video_data, item_id)

        except Exception as e:
            raise URLParserError(f"Failed to parse Xiaohongshu video: {str(e)}") from e

    def _extract_xiaohongshu_item_id(self, url: str) -> str:
        """从小红书 URL 中提取 item ID"""
        # 从 URL 中提取 item ID: /discovery/item/68c94ab0000000001202ca84
        import re
        pattern = r'/item/([a-f0-9]+)'
        match = re.search(pattern, url)
        if not match:
            raise URLParserError("无法从小红书 URL 中提取 item ID")
        return match.group(1)

    async def _fetch_xiaohongshu_data(self, item_id: str) -> dict:
        """调用第三方解析服务获取小红书视频数据"""
        # 这里需要你提供第三方解析服务的 API 端点
        # 暂时返回模拟数据，你需要替换为实际的 API 调用

        # 模拟 API 调用
        # async with httpx.AsyncClient(headers=self.headers) as client:
        #     # 这里应该是实际的第三方 API 端点
        #     # api_url = f"https://your-api-service.com/parse?url=xiaohongshu&item_id={item_id}"
        #     # response = await client.get(api_url)
        #     # return response.json()

        # 暂时返回你提供的示例数据结构
        return {
                "code": 200,
                "message": "操作成功",
                "data": {
                    "vid": item_id,
                    "host": "xiaohongshu",
                    "hostAlias": "小红书",
                    "displayTitle": "升级mac os26，变化太大了？",
                    "status": "finish",
                    "videoItemVoList": [
                        {
                            "baseUrl": "https://sns-video-hw.xhscdn.com/stream/79/110/258/01e8c94a61bce4ac4f03700199524c593d_258.mp4",
                            "quality": "未知",
                            "qualityAlias": "未知清晰度",
                            "fileType": "video",
                            "size": 0,
                            "mustUseDownloader": False,
                            "hlsType": False,
                            "dashType": False,
                            "live": False,
                            "canDownload": True,
                            "canDirectPlay": True,
                            "canDirectDownload": False,
                            "onlyForVip": False
                        },
                        {
                            "baseUrl": "https://sns-webpic.xhscdn.com/1040g00831mg8iahp4u004a031hprq9f1r7a89j8?imageView2/2/w/0/format/jpg",
                            "quality": "封面",
                            "qualityAlias": "图片(封面)",
                            "fileType": "image",
                            "size": 0,
                            "mustUseDownloader": False,
                            "hlsType": False,
                            "dashType": False,
                            "live": False,
                            "canDownload": True,
                            "canDirectPlay": True,
                            "canDirectDownload": False,
                            "onlyForVip": False
                        }
                    ]
                }
            }

    def _parse_xiaohongshu_data(self, api_response: dict, item_id: str) -> VideoInfo:
        """解析第三方 API 返回的小红书数据"""
        try:
            if api_response.get("code") != 200:
                raise URLParserError(f"第三方解析服务返回错误: {api_response.get('message', 'Unknown error')}")

            data = api_response["data"]

            # 获取视频信息
            video_id = data.get("vid", item_id)
            title = data.get("displayTitle", f"xiaohongshu_{video_id}")

            # 查找视频文件
            video_url = None
            for item in data.get("videoItemVoList", []):
                if item.get("fileType") == "video" and item.get("canDownload"):
                    video_url = item.get("baseUrl")
                    break

            if not video_url:
                raise URLParserError("未找到可下载的视频文件")

            # 清理标题中的非法字符
            title = re.sub(r'[\\/:*?"<>|]', '_', title)

            return VideoInfo(
                video_id=video_id,
                platform="xiaohongshu",
                title=title,
                download_url=video_url,
            )

        except (KeyError, IndexError, TypeError) as e:
            raise URLParserError(
                f"Failed to parse Xiaohongshu video data: Missing required fields - {str(e)}"
            ) from e

    def _extract_router_data(self, html_content: str) -> dict[str, Any]:
        """Extract _ROUTER_DATA JSON from HTML content"""
        # Find the script tag containing _ROUTER_DATA
        pattern = r"window\._ROUTER_DATA\s*=\s*({.*?});"
        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            raise URLParserError(
                "Failed to parse Douyin video data: _ROUTER_DATA not found"
            )

        try:
            router_data = json.loads(match.group(1))
            return router_data
        except json.JSONDecodeError as e:
            raise URLParserError(
                "Failed to parse Douyin video data: Invalid JSON in _ROUTER_DATA"
            ) from e

    def _extract_router_data_optimized(self, html_content: str) -> dict[str, Any]:
        """Extract _ROUTER_DATA JSON from HTML content - 基于成功的 PoC 实现"""
        # 使用更精确的正则表达式，匹配到 </script> 标签
        pattern = re.compile(
            pattern=r"window\._ROUTER_DATA\s*=\s*(.*?)</script>",
            flags=re.DOTALL,
        )
        find_res = pattern.search(html_content)

        if not find_res or not find_res.group(1):
            raise URLParserError("从HTML中解析视频信息失败")

        try:
            # 解析JSON数据，去除末尾可能的分号
            json_str = find_res.group(1).strip().rstrip(";")
            router_data = json.loads(json_str)
            return router_data
        except json.JSONDecodeError as e:
            raise URLParserError(
                "Failed to parse Douyin video data: Invalid JSON in _ROUTER_DATA"
            ) from e

    def _parse_douyin_router_data(self, router_data: dict[str, Any]) -> VideoInfo:
        """Parse video information from Douyin router data"""
        try:
            # Navigate through the nested structure
            loader_data = router_data.get("loaderData", {})

            # Find the video data (key pattern: "video_(id)")
            video_key = None
            for key in loader_data.keys():
                if key.startswith("video_"):
                    video_key = key
                    break

            if not video_key:
                raise URLParserError(
                    "Failed to parse Douyin video data: Video data not found"
                )

            video_data = loader_data[video_key]
            item_struct = video_data["itemInfo"]["itemStruct"]

            # Extract video information
            video_id = item_struct["id"]
            title = item_struct["desc"]
            download_url = item_struct["video"]["playAddr"][0]["src"]

            return VideoInfo(
                video_id=video_id,
                platform="douyin",
                title=title,
                download_url=download_url,
            )

        except (KeyError, IndexError, TypeError) as e:
            raise URLParserError(
                f"Failed to parse Douyin video data: Missing required fields - {str(e)}"
            ) from e

    def _parse_douyin_router_data_optimized(
        self, router_data: dict[str, Any], video_id: str
    ) -> VideoInfo:
        """Parse video information from Douyin router data - 基于成功的 PoC 实现"""
        try:
            # 支持多种页面结构
            VIDEO_ID_PAGE_KEY = "video_(id)/page"
            NOTE_ID_PAGE_KEY = "note_(id)/page"

            loader_data = router_data.get("loaderData", {})

            # 尝试不同的数据结构
            if VIDEO_ID_PAGE_KEY in loader_data:
                original_video_info = loader_data[VIDEO_ID_PAGE_KEY]["videoInfoRes"]
            elif NOTE_ID_PAGE_KEY in loader_data:
                original_video_info = loader_data[NOTE_ID_PAGE_KEY]["videoInfoRes"]
            else:
                raise URLParserError("无法从JSON中解析视频或图集信息")

            data = original_video_info["item_list"][0]

            # 获取视频信息
            video_url = data["video"]["play_addr"]["url_list"][0].replace(
                "playwm", "play"
            )
            desc = data.get("desc", "").strip() or f"douyin_{video_id}"

            # 替换文件名中的非法字符
            desc = re.sub(r'[\\/:*?"<>|]', "_", desc)

            return VideoInfo(
                video_id=video_id,
                platform="douyin",
                title=desc,
                download_url=video_url,
            )

        except (KeyError, IndexError, TypeError) as e:
            raise URLParserError(
                f"Failed to parse Douyin video data: Missing required fields - {str(e)}"
            ) from e
