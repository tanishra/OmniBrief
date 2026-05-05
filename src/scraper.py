
import socket
import ipaddress
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright
import httpcore

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def _resolve_and_check_safe(url: str) -> Optional[str]:
    """Resolves the URL and checks if the IP is safe. Returns the IP if safe, None otherwise."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return None
        
        hostname = parsed.hostname
        if not hostname:
            return None

        # 1. Block literal IP addresses if they are private
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
                return None
            return str(ip)
        except ValueError:
            pass

        # 2. Resolve hostname and block private IPs
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
                    return None
                return str(ip) # Return first resolved safe IP
        except socket.gaierror:
            return None

    except Exception:
        return None
    return None

class SafeNetworkBackend(httpcore.AsyncNetworkBackend):
    def __init__(self, original_backend: httpcore.AsyncNetworkBackend):
        self.original_backend = original_backend

    async def connect_tcp(
        self,
        host: str,
        port: int,
        timeout: Optional[float] = None,
        local_address: Optional[str] = None,
        socket_options: Optional[List[Any]] = None,
    ) -> httpcore.AsyncNetworkStream:
        ip = _resolve_and_check_safe(f"http://{host}")
        if not ip:
            raise Exception("SSRF Blocked: Unsafe IP")
        return await self.original_backend.connect_tcp(
            host=ip,
            port=port,
            timeout=timeout,
            local_address=local_address,
            socket_options=socket_options,
        )

    async def connect_unix_socket(
        self,
        path: str,
        timeout: Optional[float] = None,
        socket_options: Optional[List[Any]] = None,
    ) -> httpcore.AsyncNetworkStream:
        return await self.original_backend.connect_unix_socket(
            path, timeout=timeout, socket_options=socket_options
        )

    async def connect_tls(self, *args, **kwargs):
        return await self.original_backend.connect_tls(*args, **kwargs)

class SafeAsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._transport._pool._network_backend = SafeNetworkBackend(self._transport._pool._network_backend)

# Global browser instance
_browser = None
_playwright = None
_browser_semaphore = None

async def _get_browser():
    global _browser, _playwright, _browser_semaphore
    if _browser_semaphore is None:
        _browser_semaphore = asyncio.Semaphore(3)
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
    return _browser

async def _close_browser():
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None

async def _resolve_and_check_safe_async(url: str) -> Optional[str]:
    loop = asyncio.get_event_loop()
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return None

        hostname = parsed.hostname
        if not hostname:
            return None

        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
                return None
            return str(ip)
        except ValueError:
            pass

        try:
            addr_info = await loop.getaddrinfo(hostname, None)
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
                    return None
                return str(ip)
        except socket.gaierror:
            return None

    except Exception:
        return None
    return None

async def _playwright_route_interceptor(route):
    url = route.request.url
    ip = await _resolve_and_check_safe_async(url)
    if not ip:
         await route.abort()
         return
    await route.continue_()

async def _scrape_playwright(url: str) -> Dict[str, Any]:
    """Headless browser fallback for heavy JS sites."""
    if not await _resolve_and_check_safe_async(url):
        print(f"    🚫 SSRF Blocked (Playwright): {url[:50]}...")
        return {}
        
    global _browser_semaphore
    if _browser_semaphore is None:
        _browser_semaphore = asyncio.Semaphore(3)

    async with _browser_semaphore:
        try:
            browser = await _get_browser()
            context = await browser.new_context(user_agent=HEADERS["User-Agent"])
            await context.route("**/*", _playwright_route_interceptor)
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
            
            await context.close()
            return {"og_image": image_url, "full_text": text[:3000]}
        except Exception as e:
            print(f"    ⚠️ Playwright fallback failed for {url[:30]}: {e}")
            return {}

async def fetch_metadata(url: str) -> Dict[str, Any]:
    """Primary: fast HTTPX. Fallback: Playwright."""
    if not _resolve_and_check_safe(url):
        print(f"    🚫 SSRF Blocked (HTTPX): {url[:50]}...")
        return {}

    try:
        async with SafeAsyncClient(timeout=10, follow_redirects=True, headers=HEADERS) as client:
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
                
    except Exception as e:
        print(f"    ⚠️ httpx failed, triggering Playwright fallback for {url[:30]}: {e}")
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
                
    # Shutdown playwright if used
    await _close_browser()
    return items
