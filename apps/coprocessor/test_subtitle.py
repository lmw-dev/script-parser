"""测试抖音视频字幕获取"""
import asyncio
import httpx
import json
import re
import os
from urllib.parse import unquote

# 禁用代理
for proxy_var in ['all_proxy', 'ALL_PROXY', 'http_proxy', 'HTTP_PROXY', 'https_proxy', 'HTTPS_PROXY']:
    os.environ.pop(proxy_var, None)


async def test_douyin_subtitle():
    """测试抖音视频是否包含字幕数据 - 使用 iesdouyin.com 域名"""
    video_id = "7553559387223182602"
    url = f"https://www.iesdouyin.com/share/video/{video_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/121.0.2277.107 Version/17.0 Mobile/15E148 Safari/604.1"
    }
    
    print(f"🔗 请求 URL: {url}")
    
    async with httpx.AsyncClient(follow_redirects=True, headers=headers, timeout=30.0, verify=False) as client:
        response = await client.get(url)
        html_content = response.text
        
        print(f"📡 HTTP 状态: {response.status_code}")
        print(f"📝 HTML 长度: {len(html_content)} 字符")
        
        # 提取 RENDER_DATA（URL编码格式）
        render_data_match = re.search(
            r'<script id="RENDER_DATA" type="application/json">(.*?)</script>',
            html_content,
            re.DOTALL
        )
        
        if render_data_match:
            print("✅ 找到 RENDER_DATA!")
            json_data = unquote(render_data_match.group(1))
            data = json.loads(json_data)
            
            # 遍历找视频数据
            loader_data = data.get("loaderData", {})
            for key in loader_data:
                if "video" in key.lower() or "note" in key.lower():
                    page_data = loader_data[key]
                    if "videoInfoRes" in page_data:
                        video_info = page_data["videoInfoRes"]
                        if "item_list" in video_info and video_info["item_list"]:
                            item = video_info["item_list"][0]
                            
                            # 保存完整数据
                            with open("douyin_video_data.json", "w", encoding="utf-8") as f:
                                json.dump(item, f, ensure_ascii=False, indent=2)
                            print(f"💾 完整视频数据已保存到 douyin_video_data.json")
                            
                            # 打印所有字段
                            print(f"\n🎬 视频数据顶级字段:")
                            for k in sorted(item.keys()):
                                print(f"   - {k}")
                            
                            # 检查 video 字段
                            if "video" in item:
                                video = item["video"]
                                print(f"\n🎥 video 对象字段:")
                                for k in sorted(video.keys()):
                                    print(f"   - {k}")
                                
                                # 检查字幕相关字段
                                subtitle_keys = ["subtitle", "caption", "text", "srt", "vtt"]
                                for k, v in video.items():
                                    if v and any(sk in k.lower() for sk in subtitle_keys):
                                        print(f"\n✅ 发现可能的字幕字段: {k}")
                                        print(f"   内容: {json.dumps(v, ensure_ascii=False, indent=2)[:1000]}")
                            
                            # 深度搜索字幕字段
                            await search_subtitle_in_data(item)
                            return item
            
            print("❌ 未在 loaderData 中找到视频数据")
        else:
            print("❌ 未找到 RENDER_DATA")
            # 保存HTML供分析
            with open("douyin_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"💾 HTML 已保存到 douyin_page.html")
        
        return None


async def search_subtitle_in_data(item: dict):
    """在视频数据中递归搜索字幕相关字段"""
    if not item:
        return
    
    print("\n" + "=" * 60)
    print("🔍 深度搜索字幕相关字段...")
    print("=" * 60)
    
    def find_fields(obj, path="", results=None):
        if results is None:
            results = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                # 检查字幕关键词
                if any(kw in key.lower() for kw in ['subtitle', 'caption', 'srt', 'vtt', 'transcript', 'text_track']):
                    results.append((current_path, type(value).__name__, value))
                find_fields(value, current_path, results)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                find_fields(v, f"{path}[{i}]", results)
        
        return results
    
    results = find_fields(item)
    
    if results:
        print(f"\n找到 {len(results)} 个相关字段:")
        for path, type_name, value in results:
            print(f"\n📌 {path} ({type_name})")
            if value:
                value_str = json.dumps(value, ensure_ascii=False, indent=2) if not isinstance(value, str) else value
                print(f"   {value_str[:500]}")
    else:
        print("❌ 未找到明显的字幕字段")
        print("\n💡 可能原因:")
        print("   1. 视频没有上传字幕")
        print("   2. 字幕通过其他 API 单独获取")
        print("   3. 字幕字段使用了其他名称")


if __name__ == "__main__":
    asyncio.run(test_douyin_subtitle())
