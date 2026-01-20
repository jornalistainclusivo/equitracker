from crawl4ai import AsyncWebCrawler
import logging
from urllib.parse import urlparse
import ipaddress
import socket

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
            logger.warning("Could not resolve host %s: %s — blocking for safety", host, str(e))
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
        Scrapes the given URL using crawl4ai and returns the markdown content.
        Returns empty string on failure or when URL is considered unsafe.
        """
        try:
            logger.info(f"Starting crawl for URL: {url}")

            # Basic safety checks to mitigate SSRF
            if not _is_public_http_url(url):
                logger.error("URL blocked by SSRF protection: %s", url)
                return ""

            # Initialize with verbose=True for better debugging
            async with AsyncWebCrawler(verbose=True) as crawler:
                # Use arun to fetch content
                result = await crawler.arun(
                    url=url,
                    # Modern user agent to avoid being blocked
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    magic=True,  # Handle dynamic content/waiting
                    # Consider adding a max timeout in crawl4ai args if available
                )

                if not result.success:
                    logger.error(f"Failed to crawl {url}: {getattr(result, 'error_message', 'unknown')}")
                    return ""

                # Check for empty markdown
                if not result.markdown:
                    logger.warning(f"Zero length markdown returned for {url}. Raw HTML length: {len(result.html) if result.html else 0}")
                    return ""

                logger.info(f"Successfully scraped {len(result.markdown)} bytes from {url}")
                return result.markdown

        except Exception:
            logger.exception("Unhandled exception while crawling URL")
            return ""
