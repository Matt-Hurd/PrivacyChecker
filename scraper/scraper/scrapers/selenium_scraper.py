from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from scrapers.base_scraper import BaseScraper
import time

class SeleniumScraper(BaseScraper):
    def __init__(self, url: str, file_handler):
        super().__init__(url, file_handler)
        self.driver = self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def scrape(self) -> str:
        if not self.can_fetch():
            self.logger.warning(f"Scraping not allowed for {self.url}")
            return None

        try:
            self.driver.get(self.url)
            time.sleep(5)  # Wait for JavaScript to render
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Error fetching {self.url}: {e}")
            return None
        finally:
            self.driver.quit()