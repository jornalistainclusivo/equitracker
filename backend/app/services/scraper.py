import httpx
import logging
from urllib.parse import urlparse
import ipaddress
import socket
from bs4 import BeautifulSoup
from html2text import HTML2Text

# Configure logger
logger = logging.getLogger(__name__)

def _is_public_http_url(url: str) -> bool:
    """
    Validate URL for scraping:
    - scheme must be http or https
    - hostname must resolve
    - resolved IP must not be private, loopback, link-local, multicast or reserved
    This reduces SSRF risk by blocking internal addresses.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            logger.warning("Blocked URL due to invalid scheme: %s", url)
            return False

        host = parsed.hostname
        if not host:
            logger.warning("Blocked URL due to missing hostname: %s", url)
            return False

        # Resolve hostname to IP(s)
        try:
            resolved_ip = socket.gethostbyname(host)
            ip = ipaddress.ip_address(resolved_ip)
        except Exception as e:
            logger.warning("Could not resolve host %s: %s \u2014 blocking for safety", host, str(e))
            return False

        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            logger.warning("Blocked URL because IP is private/loopback/link-local/reserved: %s -> %s", host, ip)
            return False

        return True
    except Exception as e:
        logger.exception("Unexpected error during URL validation: %s", str(e))
        return False

class SovereignScraper:
    @staticmethod
    async def scrape_url(url: str) -> str:
        """
        Scrapes the given URL and returns the markdown content.
        Uses crawl4ai as primary method, falls back to httpx + BeautifulSoup
        if Playwright fails (common on Windows due to asyncio limitations).
        Returns empty string on failure or when URL is considered unsafe.
        
        Args:
            url (str): The URL to scrape.
            
        Returns:
            str: The scraped markdown content. Returns empty string on failure.
        """
        # Basic safety checks to mitigate SSRF
        if not _is_public_http_url(url):
            logger.error("URL blocked by SSRF protection: %s", url)
            return ""

        # Try crawl4ai first (Playwright-based, best quality)
        try:
            content = await SovereignScraper._scrape_with_crawl4ai(url)
            if content:
                return content
            logger.warning(f"crawl4ai returned empty content for {url}, trying fallback...")
        except Exception as e:
            logger.warning(f"crawl4ai failed for {url}: {type(e).__name__}: {e}. Trying httpx fallback...")

        # Fallback: httpx + BeautifulSoup (no Playwright needed)
        try:
            content = await SovereignScraper._scrape_with_httpx(url)
            if content:
                return content
            logger.error(f"httpx fallback also returned empty for {url}")
        except Exception as e:
            logger.error(f"httpx fallback also failed for {url}: {e}")

        return ""

    @staticmethod
    async def _scrape_with_crawl4ai(url: str) -> str:
        """Primary scraper using crawl4ai (Playwright-based)."""
        from crawl4ai import AsyncWebCrawler

        logger.info(f"[crawl4ai] Starting crawl for URL: {url}")
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=url,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                magic=True,
            )
            
            if not result.success:
                logger.error(f"[crawl4ai] Failed to crawl {url}: {getattr(result, 'error_message', 'unknown')}")
                return ""
            
            if not result.markdown:
                logger.warning(f"[crawl4ai] Zero length markdown for {url}")
                return ""

            logger.info(f"[crawl4ai] Successfully scraped {len(result.markdown)} bytes from {url}")
            return result.markdown

    @staticmethod
    async def _scrape_with_httpx(url: str) -> str:
        """Fallback scraper using httpx + BeautifulSoup. No Playwright needed."""
        logger.info(f"[httpx-fallback] Starting fetch for URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers=headers
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove non-content elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                tag.decompose()
            
            # Convert to markdown using html2text
            converter = HTML2Text()
            converter.ignore_links = False
            converter.ignore_images = True
            converter.body_width = 0  # Don't wrap text
            converter.ignore_emphasis = False
            
            markdown = converter.handle(str(soup))
            
            if not markdown or len(markdown.strip()) < 50:
                logger.warning(f"[httpx-fallback] Minimal content extracted from {url}")
                return ""
            
            logger.info(f"[httpx-fallback] Successfully scraped {len(markdown)} bytes from {url}")
            return markdown
