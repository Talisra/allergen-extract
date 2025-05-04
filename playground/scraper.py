import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        }
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def scrape_recipe(self, url: str) -> dict:
        """Scrape recipe content and ingredients from a given URL"""
        try:
            response = self.session.get(
                url, 
                headers=self.headers,
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract recipe content
            content = soup.get_text(separator='\n', strip=True)
            
            # Extract ingredients (customize selector for target site)
            ingredients = []
            for ingredient in soup.select('[class*="ingredient"], .ingredients li'):
                ingredients.append(ingredient.get_text(strip=True))
                
            if not ingredients:
                logger.warning("No ingredients found - trying alternative parsing")
                ingredients = self._fallback_ingredient_parsing(soup)
            
            return {
                'original_content': content,
                'ingredients': ingredients,
                'status': 'success'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _fallback_ingredient_parsing(self, soup: BeautifulSoup) -> list:
        """Alternative parsing strategies"""
        # Strategy 1: Look for common data attributes
        ingredients = soup.select('[data-ingredient-name]')
        if ingredients:
            return [i.get('data-ingredient-name') for i in ingredients]
        
        # Strategy 2: Search by text patterns
        return [
            el.get_text() for el in soup.find_all(
                text=lambda t: t and any(word in t.lower() for word in ['cup', 'tbsp', 'gram'])
            )
        ]

# Usage
if __name__ == "__main__":
    scraper = RecipeScraper()
    # result = scraper.scrape_recipe("https://www.allrecipes.com/recipe/46822/indian-chicken-curry-ii/")
    result = scraper.scrape_recipe("https://quotes.toscrape.com/")

    if result['status'] == 'success':
        print("First 3 ingredients:", result['ingredients'][:3])
        print("\nSample content:", result['original_content'][:500] + "...")
    else:
        print("Scraping failed:", result['message'])
