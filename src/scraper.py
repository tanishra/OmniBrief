"""
src/scraper.py
V5 Engine: Hybrid Scraping (BeautifulSoup primary, Playwright fallback).
V5.1: SSRF Protection.
"""

import socket
import ipaddress
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def _is_safe_url(url: str) -> bool:
    """Checks if a URL is safe for server-side fetching (prevents SSRF)."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        
        hostname = parsed.hostname
        if not hostname:
            return False

        # 1. Block literal IP addresses if they are private
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
                return False
        except ValueError:
            # Not an IP literal, continue to DNS resolution
            pass

        # 2. Resolve hostname and block private IPs (Basic DNS check)
        # Note: This doesn't fully prevent DNS rebinding but blocks direct internal access.
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
                    return False
        except socket.gaierror:
            # DNS failure, URL likely invalid anyway
            return False

        return True
    except Exception:
        return False

async def _scrape_playwright(url: str) -> Dict[str, Any]:
    """Headless browser fallback for heavy JS sites."""
    if not _is_safe_url(url):
        print(f"    🚫 SSRF Blocked (Playwright): {url[:50]}...")
        return {}
        
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=HEADERS["User-Agent"])
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=20000)
            
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Extract basic text
            for s in soup(["script", "style"]): s.decompose()
            text = soup.get_text(separator=" ", strip=True)
            
            # Try to find OG image again in rendered HTML
            og_image = soup.find("meta", property="og:image")
            image_url = og_image["content"] if og_image else None
            
            await browser.close()
            return {"og_image": image_url, "full_text": text[:3000]}
    except Exception as e:
        print(f"    ⚠️ Playwright fallback failed for {url[:30]}: {e}")
        return {}

async def fetch_metadata(url: str) -> Dict[str, Any]:
    """Primary: fast HTTPX. Fallback: Playwright."""
    if not _is_safe_url(url):
        print(f"    🚫 SSRF Blocked (HTTPX): {url[:50]}...")
        return {}

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True, headers=HEADERS) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                og_image = soup.find("meta", property="og:image")
                image_url = og_image["content"] if og_image else None
                
                for s in soup(["script", "style", "nav", "header", "footer"]): s.decompose()
                article = soup.find("article") or soup.find("main")
                text = article.get_text(separator=" ", strip=True) if article else soup.get_text(separator=" ", strip=True)
                
                # If text is too short, site likely requires JS
                if len(text) < 500:
                    print(f"    🔄 Low content found, triggering Playwright fallback for {url[:30]}...")
                    return await _scrape_playwright(url)
                
                return {"og_image": image_url, "full_text": text[:3000]}
            
            elif resp.status_code in (403, 401, 429):
                print(f"    🔄 Blocked ({resp.status_code}), triggering Playwright fallback...")
                return await _scrape_playwright(url)
                
    except Exception:
        return await _scrape_playwright(url)
    return {}

async def enrich_items(items: list, max_scrape: int = 5) -> list:
    """Enriches items with metadata and full text."""
    tasks = [fetch_metadata(item.get("url", "")) for item in items[:max_scrape]]
    meta_results = await asyncio.gather(*tasks)
    
    for i, meta in enumerate(meta_results):
        if meta:
            items[i].update(meta)
    
    # Predictable GitHub fallback
    for item in items:
        if "github.com" in item.get("url", "") and not item.get("og_image"):
            user_repo = item.get("name", "").replace(" ", "")
            if "/" in user_repo:
                item["og_image"] = f"https://opengraph.githubassets.com/1/{user_repo}"
                
    return items
