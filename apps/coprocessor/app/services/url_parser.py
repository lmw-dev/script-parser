import asyncio
import json
import re
from typing import Any
import os

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
        # 从环境变量中读取代理配置
        self.proxy_url = os.getenv("PROXY_URL")

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
        """Parse Douyin video URL and extract video information - with actual HTML parsing"""
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # 使用不同的 User-Agent 和配置重试
                user_agents = [
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
                    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
                ]
                
                headers = {
                    "User-Agent": user_agents[attempt % len(user_agents)],
                }
                
                proxies = {"all://": self.proxy_url} if self.proxy_url else None

                client = httpx.AsyncClient(
                    headers=headers,
                    proxies=proxies,  # 添加代理配置
                    timeout=httpx.Timeout(20.0, connect=10.0),
                    follow_redirects=True,
                    verify=False  # 禁用 SSL 验证以解决某些 SSL 问题
                )
                
                try:
                    # 第一步：获取重定向 URL 和 video_id
                    if attempt > 0:
                        await asyncio.sleep(1)  # 重试前稍等
                    
                    # 第一次请求，只为获取 video_id
                    share_response = await client.get(url)
                    final_url = str(share_response.url)
                    video_id = self._extract_item_id_from_url(final_url)
                    
                    if not video_id:
                        raise URLParserError("无法从 URL 中提取视频 ID")

                    # 第二步：构建干净的 URL 并获取页面内容
                    clean_url = f'https://www.iesdouyin.com/share/video/{video_id}'
                    page_response = await client.get(clean_url)
                    page_response.raise_for_status() # 确保请求成功

                    # 尝试解析页面内容
                    html_content = page_response.text
                    
                    # 尝试从页面内容中提取路由器数据
                    router_data = self._extract_router_data_optimized(html_content)
                    return self._parse_douyin_router_data_optimized(router_data, video_id)
                
                finally:
                    await client.aclose()
                    
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError) as e:
                last_error = e
                if attempt < max_retries:
                    continue  # 重试
                
            except Exception as e:
                # 非网络错误，直接抛出
                raise URLParserError(f"Failed to parse Douyin video: {str(e)}") from e
        
        # 所有重试失败，抛出最后一个错误
        if last_error:
            raise URLParserError(
                f"经过 {max_retries + 1} 次尝试，仍无法连接到抖音服务器。\n"
                f"这可能是网络问题、地理位置限制或需要使用 VPN。\n"
                f"原始错误: {str(last_error)}"
            ) from last_error
        
        raise URLParserError("未知错误")

    def _extract_item_id_from_url(self, url: str) -> str:
        """从 URL 中提取视频 ID"""
        # 尝试多种模式提取 video_id
        patterns = [
            r'/video/([0-9]+)',  # /video/1234567890
            r'/share/video/([0-9]+)',  # /share/video/1234567890  
            r'video[_/=]([0-9]+)',  # video_id=1234567890
            r'([0-9]{15,})',  # 直接匹配长数字
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # 如果都找不到，尝试从 URL path 中提取
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        for part in reversed(path_parts):
            if part.isdigit() and len(part) >= 10:
                return part
        
        return None

    async def _parse_xiaohongshu(self, url: str) -> VideoInfo:
        """Parse Xiaohongshu video URL using a robust, multi-layered approach."""
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html_content = response.text
                final_url = str(response.url)

            # Extract item_id from the final URL
            item_id_match = re.search(r'/item/([a-f0-9]+)', final_url)
            if not item_id_match:
                raise URLParserError("Could not extract item_id from Xiaohongshu URL")
            item_id = item_id_match.group(1)

            # --- Start of robust extraction logic ---
            video_info = {
                'title': None,
                'video_urls': [],
            }

            # 1. Attempt to parse JSON from script tags
            json_patterns = [
                r'window.__INITIAL_STATE__\s*=\s*(.+?);?\s*</script>',
                r'window.__NEXT_DATA__\s*=\s*(.+?);?\s*</script>'
            ]
            
            found_json = False
            for pattern in json_patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    try:
                        json_text = match.group(1).strip()
                        if json_text.endswith(';'):
                            json_text = json_text[:-1]
                        json_text = json_text.replace("undefined", "null")
                        json_data = json.loads(json_text)
                        
                        extracted_info = self._extract_from_xhs_json(json_data)
                        if extracted_info.get('video_urls'):
                            video_info.update(extracted_info)
                            found_json = True
                            break # Stop after first successful extraction
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            # 2. Fallback: Direct regex search for video URLs if JSON fails
            if not video_info.get('video_urls'):
                video_url_patterns = [
                    r'"originVideoKey"\s*:\s*"([^"]+)"', # From previous findings
                    r'"masterUrl"\s*:\s*"([^"]+)"',
                    r'https://[^\s"\\]*.(?:mp4|m3u8)[^\s"\\]*'
                ]
                
                found_urls = set()
                for pattern in video_url_patterns:
                    matches = re.findall(pattern, html_content)
                    for match_url in matches:
                        clean_url = match_url.replace('\\u002F', '/')
                        if 'sns-video' in clean_url or '.mp4' in clean_url:
                            found_urls.add(clean_url)
                video_info['video_urls'] = list(found_urls)

            if not video_info.get('video_urls'):
                raise URLParserError("Could not find any video URL in the page.")

            # Use the first found URL
            download_url = video_info['video_urls'][0]
            if 'originVideoKey' in download_url: # Handle case where we only found the key
                 download_url = f"https://sns-video-bd.xhscdn.com/{download_url}"

            # Final cleanup and return
            title = video_info.get('title') or f"xiaohongshu_{item_id}"

            print(f"---- Extracted Xiaohongshu Download URL: {download_url} ----")

            return VideoInfo(
                video_id=item_id,
                platform="xiaohongshu",
                title=title,
                download_url=download_url,
            )

        except (httpx.RequestError, json.JSONDecodeError, KeyError, IndexError) as e:
            raise URLParserError(f"Failed to parse Xiaohongshu video: {str(e)}") from e

    def _extract_from_xhs_json(self, data: dict) -> dict:
        """Recursively extract video information from Xiaohongshu JSON data."""
        result = {
            'title': None,
            'video_urls': [],
        }

        def recursive_search(obj):
            if isinstance(obj, dict):
                # Check for title
                if not result['title'] and obj.get('title') and isinstance(obj['title'], str):
                    result['title'] = obj['title']
                
                # Check for video key
                video_key = obj.get("video", {}).get("consumer", {}).get("originVideoKey")
                if video_key:
                    url = f"https://sns-video-bd.xhscdn.com/{video_key}"
                    if url not in result['video_urls']:
                        result['video_urls'].append(url)

                # Check for direct video URLs in streams
                for stream_type in obj.get("stream", {}).get("h264", []):
                    if stream_type.get('masterUrl'):
                         if stream_type['masterUrl'] not in result['video_urls']:
                            result['video_urls'].append(stream_type['masterUrl'])

                for key, value in obj.items():
                    recursive_search(value)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_search(item)
        
        recursive_search(data)
        return result



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

            # --- DEBUG: Print the entire play_addr object ---
            print("---- DOUYIN PLAY_ADDR OBJECT ----")
            print(json.dumps(data["video"].get("play_addr"), indent=2))
            print("---------------------------------")

            # 获取视频信息
            video_url = data["video"]["play_addr"]["url_list"][0].replace(
                "playwm", "play"
            )
            desc = data.get("desc", "").strip() or f"douyin_{video_id}"

            # 替换文件名中的非法字符
            desc = re.sub(r'[\\/:*?"<>|]', "_", desc)

            print(f"---- Extracted Douyin Download URL: {video_url} ----")

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
