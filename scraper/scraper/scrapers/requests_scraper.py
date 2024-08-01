import requests
from scrapers.base_scraper import BaseScraper

class RequestsScraper(BaseScraper):
    def __init__(self, url: str, file_handler):
        super().__init__(url, file_handler)
        self.session = requests.Session()

    def scrape(self) -> str:
        if not self.can_fetch():
            self.logger.warning(f"Scraping not allowed for {self.url}")
            return None

        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {self.url}: {e}")
            return None