from bs4 import BeautifulSoup
from website_config import WebsiteConfig
from scraper_factory import ScraperFactory
from file_handler import FileHandler
from scrapers.base_scraper import BaseScraper

class WebsiteScraper(BaseScraper):
    def __init__(self, config: WebsiteConfig, file_handler: FileHandler):
        super().__init__(config.url, file_handler)
        self.config = config
        self.scraper = ScraperFactory.get_scraper(config.url, config.scraper_type, file_handler)

    def scrape(self) -> str:
        return self.scraper.scrape()

    def parse_data(self, content: str) -> dict:
        soup = BeautifulSoup(content, 'html.parser')
        data = {}
        for key, selector in self.config.selectors.items():
            elements = soup.select(selector)
            data[key] = [
                {
                    'html': str(element),
                    'text': element.get_text(strip=True)
                }
                for element in elements
            ]
        return data
    
    def scrape_and_save(self) -> None:
        content = self.scrape()
        if content:
            parsed_data = self.parse_data(content)
            self.save_data(parsed_data)