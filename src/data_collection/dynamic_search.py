import logging
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicSearchEngine:
    """Class to perform dynamic web searches and content extraction when local knowledge is insufficient."""
    
    def __init__(self):
        """Initialize the dynamic search engine."""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }
    
    def search(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """
        Perform a web search for the given query and return results.
        Uses a free search engine API or direct scraping.
        """
        logger.info(f"Performing dynamic search for: {query}")
        
        # For demonstration, we'll use a simple approach to scrape search results
        # In production, consider using a service like SerpAPI, Bing API, or Google Custom Search API
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        
        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results (this is simplified and may break if Google changes their HTML structure)
            results = []
            for result in soup.select("div.g")[:num_results]:
                title_elem = result.select_one("h3")
                link_elem = result.select_one("a")
                snippet_elem = result.select_one("div.VwiC3b")
                
                if title_elem and link_elem and snippet_elem:
                    title = title_elem.text
                    link = link_elem.get("href")
                    if link and link.startswith("/url?q="):
                        link = link.split("/url?q=")[1].split("&")[0]
                    snippet = snippet_elem.text
                    
                    results.append({
                        "title": title,
                        "url": link,
                        "snippet": snippet
                    })
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Error during web search: {str(e)}")
            return []
    
    def extract_content(self, url: str) -> str:
        """Extract the main content from a webpage."""
        logger.info(f"Extracting content from: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, and nav elements
            for element in soup.select('script, style, nav, header, footer, [class*="nav"], [id*="nav"], [class*="menu"], [id*="menu"]'):
                element.extract()
            
            # Try to find the main content
            main_content = None
            
            # Try common content containers
            for selector in ['article', 'main', '.content', '#content', '.post', '.entry', '.article']:
                content = soup.select_one(selector)
                if content:
                    main_content = content
                    break
            
            # If no specific container found, use the body
            if not main_content:
                main_content = soup.body
            
            # Extract text from paragraphs and headings
            if main_content:
                text_elements = main_content.select('p, h1, h2, h3, h4, h5, h6, li')
                content_text = '\n\n'.join([elem.get_text().strip() for elem in text_elements])
                
                # Clean up the text
                content_text = re.sub(r'\s+', ' ', content_text).strip()
                
                # Add source attribution
                content_text = f"Content from {url}:\n\n{content_text}"
                
                logger.info(f"Successfully extracted {len(content_text)} characters")
                return content_text
            
            return f"Could not extract meaningful content from {url}"
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return f"Error extracting content: {str(e)}"