from crawl4ai import AsyncWebCrawler
import logging

# Configure logger
logger = logging.getLogger(__name__)

class SovereignScraper:
    @staticmethod
    async def scrape_url(url: str) -> str:
        """
        Scrapes the given URL using crawl4ai and returns the markdown content.
        
        Args:
            url (str): The URL to scrape.
            
        Returns:
            str: The scraped markdown content. Returns empty string on failure.
        """
        try:
            logger.info(f"Starting crawl for URL: {url}")
            # Initialize with verbose=True for better debugging
            async with AsyncWebCrawler(verbose=True) as crawler:
                # Use arun to fetch content
                result = await crawler.arun(
                    url=url,
                    # Modern user agent to avoid being blocked
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    magic=True,  # Handle dynamic content/waiting
                )
                
                if not result.success:
                    logger.error(f"Failed to crawl {url}: {result.error_message}")
                    return ""
                
                # Check for empty markdown
                if not result.markdown:
                    logger.warning(f"Zero length markdown returned for {url}. Raw HTML length: {len(result.html) if result.html else 0}")
                    return ""

                logger.info(f"Successfully scraped {len(result.markdown)} bytes from {url}")
                return result.markdown
                
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return ""
