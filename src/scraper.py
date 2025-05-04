import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from src.sites import SiteRegistry
from urllib.parse import urlparse
import yaml

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class AbstractScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> dict:
        pass
    
class RecipeScraper(ABC):
    @abstractmethod
    def _parse_ingredients(self, scrapper, url) -> list:
        """Parse ingredients from url. Returns list of ingredients."""
        pass

class BeautifulSoupScraper(AbstractScraper):
    def __init__(self):
        self.session = requests.Session()
        self.headers = config['headers']
        retry_strategy = Retry(
            total=config['request']['retry']['total'],
            status_forcelist=config['request']['retry']['status_forcelist'],
            allowed_methods=config['request']['retry']['allowed_methods'],
            backoff_factor=config['request']['retry']['backoff_factor']
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.timeout = config['request']['timeout']

    def get_soup(self, url: str) -> BeautifulSoup:
        response = self.session.get(
            url, 
            headers=self.headers,
            timeout=10,
            allow_redirects=True
        )
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

class BSoupRecipeScraper(BeautifulSoupScraper, RecipeScraper):
    def scrape(self, url: str) -> dict:
        try:
            soup = self.get_soup(url)
            content = soup.get_text(separator='\n', strip=True)
            ingredients = self._parse_ingredients(soup, url)
            if not ingredients:
                ingredients = self._fallback_ingredients(soup)
            return {
                'original_content': content,
                'ingredients': ingredients,
                'status': 'success'
            }
        except requests.exceptions.RequestException as e:
            return {'status': 'error', 'message': str(e)}

    def _fallback_ingredients(self, soup: BeautifulSoup) -> list:
        """
        Attempt to extract ingredient information using alternative strategies if standard selectors fail.
        This method first searches for elements with a 'data-ingredient-name' attribute and collects their values.
        If none are found, it scans all text nodes for common measurement keywords (e.g., 'cup', 'tbsp', 'gram')
        and returns the matching text as potential ingredient entries.
        This is supposed to be a generic solution but wasn't tested on multiple sites!
        """
        ingredients = soup.select('[data-ingredient-name]')
        if ingredients:
            return [i.get('data-ingredient-name') for i in ingredients]
        return [
            el.get_text() for el in soup.find_all(
                text=lambda t: t and any(word in t.lower() for word in ['cup', 'tbsp', 'gram'])
            )
        ]
    
    def _parse_ingredients(self, soup, url):
        """
        Attemps to retrieve the ingredients from the url: if it's in the site registry, use upfront known HTML element.
        If not in site registry, use a generic solution.
        """
        base_url = self._parse_url(url)
        if (SiteRegistry.sites.__contains__(base_url)):
            return [
                    ing.get_text(strip=True)
                    for ing in soup.select(SiteRegistry.sites[base_url].ingredient_selector)
                ]
        else:   
            return [
                    ing.get_text(strip=True)
                    for ing in soup.select(SiteRegistry.default_selector)
                ]
    
    def _parse_url(self, url):
        base_url = urlparse(url).netloc
        if base_url.startswith('www.'):
            base_url = base_url[4:]
        return base_url
