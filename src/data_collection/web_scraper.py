import requests
from bs4 import BeautifulSoup
import os
import logging
from typing import List, Dict, Any
import yaml
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the web scraper with configuration."""
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)["data_collection"]
        
        self.output_dir = "data/raw/web"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def scrape_urls(self) -> List[Dict[str, Any]]:
        """Scrape content from configured URLs."""
        results = []
        
        web_sources = [source for source in self.config["sources"] if source["type"] == "web"]
        for source in web_sources:
            for url in source.get("urls", []):
                try:
                    logger.info(f"Scraping: {url}")
                    response = requests.get(url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    })
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    # Extract main content (customize for different sites)
                    content = ""
                    
                    # Common content selectors (customize based on sites)
                    selectors = ["article", "main", ".content", "#content", ".post-content"]
                    for selector in selectors:
                        main_content = soup.select_one(selector)
                        if main_content:
                            # Extract text from paragraphs
                            paragraphs = main_content.find_all("p")
                            content = "\n\n".join([p.get_text().strip() for p in paragraphs])
                            break
                    
                    if not content:
                        # Fallback: get all paragraph text
                        paragraphs = soup.find_all("p")
                        content = "\n\n".join([p.get_text().strip() for p in paragraphs])
                    
                    # Save the content
                    filename = url.split("/")[-1].replace("-", "_") or "index"
                    filename = f"{filename}.txt"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"Source: {url}\n\n")
                        f.write(content)
                    
                    results.append({
                        "url": url,
                        "filename": filepath,
                        "content_length": len(content)
                    })
                    
                    # Be nice to servers
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error scraping {url}: {str(e)}")
        
        return results

if __name__ == "__main__":
    scraper = WebScraper()
    results = scraper.scrape_urls()
    logger.info(f"Scraped {len(results)} web pages")