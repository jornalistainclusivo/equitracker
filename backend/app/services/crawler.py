from crawl4ai import AsyncWebCrawler

class CrawlerService:
    @staticmethod
    async def scrape_url(url: str) -> str:
        """
        Scrapes the given URL using crawl4ai and returns the markdown content.
        Handles connection errors gracefully.
        """
        try:
            # Initialize with verbose=True as requested
            async with AsyncWebCrawler(verbose=True) as crawler:
                # Stealth Headers & Wait Strategy (Magic Mode)
                result = await crawler.arun(
                    url=url,
                    # user_agent from instructions
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    magic=True,  # Handle dynamic content/waiting
                )
                
                if not result.success:
                    print(f"Failed to crawl {url}: {result.error_message}")
                    return ""
                
                # Error Logging for empty return
                if not result.markdown:
                    print(f"WARNING: Zero length markdown returned for {url}. Raw length: {len(result.html) if result.html else 0}")
                    return ""

                return result.markdown
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
            return ""
