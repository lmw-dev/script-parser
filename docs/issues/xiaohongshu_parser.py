#!/usr/bin/env python3
"""
Xiaohongshu Video URL Parser
A tool to extract downloadable video URLs from Xiaohongshu (Little Red Book) share links.
"""

import re
import json
import requests
from urllib.parse import urlparse, parse_qs
import trafilatura
from bs4 import BeautifulSoup
from typing import Optional, Dict, List


class XiaohongshuParser:
    """Parser for Xiaohongshu video URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        # Set common headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def validate_xiaohongshu_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid Xiaohongshu URL
        
        Args:
            url (str): The URL to validate
            
        Returns:
            bool: True if valid Xiaohongshu URL, False otherwise
        """
        xiaohongshu_patterns = [
            r'xiaohongshu\.com',
            r'xhslink\.com'
        ]
        
        for pattern in xiaohongshu_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def extract_item_id(self, url: str) -> Optional[str]:
        """
        Extract the item ID from Xiaohongshu URL
        
        Args:
            url (str): The Xiaohongshu URL
            
        Returns:
            Optional[str]: The extracted item ID, None if not found
        """
        # Pattern to match item ID in discovery URLs
        discovery_pattern = r'discovery/item/([a-f0-9]+)'
        match = re.search(discovery_pattern, url)
        if match:
            return match.group(1)
        
        # Pattern to match explore URLs
        explore_pattern = r'explore/([a-f0-9]+)'
        match = re.search(explore_pattern, url)
        if match:
            return match.group(1)
        
        return None
    
    def get_page_content(self, url: str, follow_redirects: bool = True) -> Optional[tuple]:
        """
        Fetch raw HTML content from a Xiaohongshu page
        
        Args:
            url (str): The URL to fetch
            follow_redirects (bool): Whether to follow redirects
            
        Returns:
            Optional[tuple]: (final_url, html_content) or None if failed
        """
        try:
            response = self.session.get(url, timeout=15, allow_redirects=follow_redirects)
            response.raise_for_status()
            
            final_url = response.url
            html_content = response.text
            
            return final_url, html_content
            
        except Exception as e:
            # Don't print errors here as this is library code
            return None
    
    def extract_video_info(self, html_content: str) -> Dict:
        """
        Extract video information from HTML content by parsing embedded JSON data
        
        Args:
            html_content (str): The HTML content
            
        Returns:
            Dict: Dictionary containing video information
        """
        video_info = {
            'title': None,
            'video_urls': [],
            'cover_image': None,
            'author': None
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title from HTML title tag first
            title_tag = soup.find('title')
            if title_tag:
                video_info['title'] = title_tag.get_text().strip()
            
            # Look for embedded JSON data in script tags
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                script_text = script.get_text()
                if not script_text:
                    continue
                
                # Try to find JSON data patterns
                json_patterns = [
                    r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
                    r'window\.__NEXT_DATA__\s*=\s*({.+?});',
                    r'"@type"\s*:\s*"VideoObject"[^}]+({[^}]+})',
                    r'application/json["\']>\s*({.+?})\s*</script>'
                ]
                
                for pattern in json_patterns:
                    matches = re.finditer(pattern, script_text, re.DOTALL)
                    for match in matches:
                        try:
                            json_data = json.loads(match.group(1))
                            extracted_info = self._extract_from_json(json_data)
                            
                            # Merge extracted info
                            if extracted_info['title'] and not video_info['title']:
                                video_info['title'] = extracted_info['title']
                            if extracted_info['video_urls']:
                                video_info['video_urls'].extend(extracted_info['video_urls'])
                            if extracted_info['cover_image'] and not video_info['cover_image']:
                                video_info['cover_image'] = extracted_info['cover_image']
                            if extracted_info['author'] and not video_info['author']:
                                video_info['author'] = extracted_info['author']
                        except (json.JSONDecodeError, KeyError):
                            continue
            
            # Fallback: Direct regex search for video URLs in HTML
            if not video_info['video_urls']:
                video_url_patterns = [
                    r'"videoUrl"\s*:\s*"([^"]+)"',
                    r'"video"\s*:\s*"([^"]+)"',
                    r'"url"\s*:\s*"(https://[^"]*\.(mp4|m3u8)[^"]*)"',
                    r'"src"\s*:\s*"(https://[^"]*\.(mp4|m3u8)[^"]*)"',
                    r'https://[^\s"\']*.(?:mp4|m3u8)[^\s"\']*'
                ]
                
                video_urls = set()
                for pattern in video_url_patterns:
                    matches = re.findall(pattern, html_content)
                    for match in matches:
                        # Handle tuple result from group patterns
                        if isinstance(match, tuple):
                            match = match[0]
                        
                        # Clean up the URL (remove escape characters)
                        clean_url = match.replace('\\/', '/').replace('\\u002F', '/')
                        if any(ext in clean_url.lower() for ext in ['.mp4', '.m3u8']):
                            video_urls.add(clean_url)
                
                video_info['video_urls'] = list(video_urls)
            
            # Remove duplicates and sort
            video_info['video_urls'] = list(set(video_info['video_urls']))
            
        except Exception as e:
            # If BeautifulSoup parsing fails, fall back to basic regex
            pass
        
        return video_info
    
    def _extract_from_json(self, data: Dict) -> Dict:
        """
        Recursively extract video information from JSON data
        
        Args:
            data (Dict): JSON data to extract from
            
        Returns:
            Dict: Extracted video information
        """
        result = {
            'title': None,
            'video_urls': [],
            'cover_image': None,
            'author': None
        }
        
        def recursive_search(obj, path=""):
            if isinstance(obj, dict):
                # Look for video-related keys
                for key, value in obj.items():
                    key_lower = key.lower()
                    
                    # Title extraction
                    if key_lower in ['title', 'desc', 'description', 'name'] and isinstance(value, str):
                        if not result['title'] or len(value) > len(result['title']):
                            result['title'] = value
                    
                    # Video URL extraction
                    elif key_lower in ['videourl', 'video', 'src', 'url'] and isinstance(value, str):
                        if any(ext in value.lower() for ext in ['.mp4', '.m3u8']):
                            clean_url = value.replace('\\/', '/').replace('\\u002F', '/')
                            result['video_urls'].append(clean_url)
                    
                    # Cover image extraction
                    elif key_lower in ['cover', 'coverurl', 'thumbnail', 'poster'] and isinstance(value, str):
                        if not result['cover_image'] and ('jpg' in value or 'png' in value or 'jpeg' in value):
                            result['cover_image'] = value.replace('\\/', '/')
                    
                    # Author extraction
                    elif key_lower in ['author', 'nickname', 'username'] and isinstance(value, str):
                        if not result['author']:
                            result['author'] = value
                    
                    # Recurse into nested objects
                    recursive_search(value, path + '.' + key)
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    recursive_search(item, path + f'[{i}]')
        
        recursive_search(data)
        return result
    
    def parse_video_url(self, url: str) -> Dict:
        """
        Parse a Xiaohongshu video URL and extract downloadable video URLs
        
        Args:
            url (str): The Xiaohongshu share URL
            
        Returns:
            Dict: Dictionary containing parsed video information and download URLs
        """
        result = {
            'success': False,
            'original_url': url,
            'item_id': None,
            'title': None,
            'video_urls': [],
            'cover_image': None,
            'author': None,
            'error': None
        }
        
        try:
            # Validate URL
            if not self.validate_xiaohongshu_url(url):
                result['error'] = 'Invalid Xiaohongshu URL'
                return result
            
            # Extract item ID
            item_id = self.extract_item_id(url)
            result['item_id'] = item_id
            
            # Get page content
            page_result = self.get_page_content(url)
            if not page_result:
                result['error'] = 'Failed to fetch page content'
                return result
            
            final_url, html_content = page_result
            
            # Re-extract item ID from final URL in case of redirects
            final_item_id = self.extract_item_id(final_url)
            if final_item_id:
                result['item_id'] = final_item_id
            
            # Extract video information
            video_info = self.extract_video_info(html_content)
            
            result.update({
                'success': True,
                'title': video_info['title'],
                'video_urls': video_info['video_urls'],
                'cover_image': video_info['cover_image'],
                'author': video_info['author']
            })
            
            if not video_info['video_urls']:
                result['success'] = False
                result['error'] = 'No video URLs found. This might not be a video post or the page structure has changed.'
            
        except Exception as e:
            result['error'] = f'Parsing error: {str(e)}'
        
        return result


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse Xiaohongshu video URLs and extract download links')
    parser.add_argument('url', help='Xiaohongshu video share URL')
    parser.add_argument('--json', action='store_true', help='Output result in JSON format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Create parser instance
    xhs_parser = XiaohongshuParser()
    
    if args.verbose:
        print(f"Parsing URL: {args.url}")
    
    # Parse the URL
    result = xhs_parser.parse_video_url(args.url)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result['success']:
            print(f"✓ Successfully parsed Xiaohongshu video!")
            print(f"Title: {result['title']}")
            if result['author']:
                print(f"Author: {result['author']}")
            if result['item_id']:
                print(f"Item ID: {result['item_id']}")
            
            if result['video_urls']:
                print(f"\nFound {len(result['video_urls'])} video URL(s):")
                for i, video_url in enumerate(result['video_urls'], 1):
                    print(f"  {i}. {video_url}")
            
            if result['cover_image']:
                print(f"\nCover Image: {result['cover_image']}")
        else:
            print(f"✗ Failed to parse video: {result['error']}")
            if args.verbose and result.get('item_id'):
                print(f"Item ID: {result['item_id']}")


if __name__ == '__main__':
    main()