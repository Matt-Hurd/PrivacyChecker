from scrapers.requests_scraper import RequestsScraper
from scrapers.selenium_scraper import SeleniumScraper
from scrapers.base_scraper import BaseScraper
from file_handler import FileHandler

class ScraperFactory:
    @staticmethod
    def get_scraper(url: str, scraper_type: str, file_handler: FileHandler) -> BaseScraper:
        if scraper_type == "requests":
            return RequestsScraper(url, file_handler)
        elif scraper_type == "selenium":
            return SeleniumScraper(url, file_handler)
        else:
            raise ValueError(f"Unknown scraper type: {scraper_type}")