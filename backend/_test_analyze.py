import asyncio
import sys
import traceback
sys.path.insert(0, ".")
from app.services.scraper import SovereignScraper
from app.services.llm import OllamaService

async def main():
    try:
        url = "https://jornalistainclusivo.com/fotografos-cegos-exposicao-itinerante-espirito-santo-2026/"
        print(f"Scraping {url} with httpx fallback...")
        content = await SovereignScraper._scrape_with_httpx(url)
        print(f"Scraped {len(content)} bytes.")
        
        print("Analyzing...")
        res = await OllamaService.analyze_article(content)
        print(res)
    except Exception as e:
        print(f"Exception: {type(e).__name__}: {e}")
        traceback.print_exc()

asyncio.run(main())
