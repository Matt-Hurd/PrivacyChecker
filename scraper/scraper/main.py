import requests
from bs4 import BeautifulSoup, NavigableString
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import yaml
from datetime import datetime
import os
import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self, url):
        self.url = url
        self.root_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f"{self.root_url}/robots.txt")
        self.robot_parser.read()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def can_fetch(self):
        return self.robot_parser.can_fetch("*", self.url)

    @abstractmethod
    def scrape(self):
        pass

    def save_data(self, data):
        if not data:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scrape_{urlparse(self.url).netloc}_{timestamp}.json"
        
        os.makedirs("data", exist_ok=True)
        with open(os.path.join("data", filename), "w") as f:
            json.dump(data, f, indent=2)
        
        logging.info(f"Data saved to {filename}")

class RequestsScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.session = requests.Session()

    def scrape(self):
        if not self.can_fetch():
            logging.warning(f"Scraping not allowed for {self.url}")
            return None

        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching {self.url}: {e}")
            return None
        

class SeleniumScraper(BaseScraper):
    def __init__(self, url):
        super().__init__(url)
        self.driver = self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def scrape(self):
        if not self.can_fetch():
            logging.warning(f"Scraping not allowed for {self.url}")
            return None

        try:
            self.driver.get(self.url)
            time.sleep(5)  # Wait for JavaScript to render
            return self.driver.page_source
        except Exception as e:
            logging.error(f"Error fetching {self.url}: {e}")
            return None
        finally:
            self.driver.quit()


class ScraperFactory:
    @staticmethod
    def get_scraper(url, scraper_type):
        if scraper_type == "requests":
            return RequestsScraper(url)
        elif scraper_type == "selenium":
            return SeleniumScraper(url)
        else:
            raise ValueError(f"Unknown scraper type: {scraper_type}")

class WebsiteConfig:
    def __init__(self, config_data):
        self.url = config_data['url']
        self.scraper_type = config_data['scraper_type']
        self.selectors = config_data['selectors']

class WebsiteScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config.url)
        self.config = config
        self.scraper = ScraperFactory.get_scraper(config.url, config.scraper_type)

    def scrape(self):
        return self.scraper.scrape()

    def parse_data(self, content):
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

def load_config_from_yaml(file_path):
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return WebsiteConfig(config_data)

def load_all_configs(directory):
    configs = []
    for filename in os.listdir(directory):
        if filename.endswith(".yaml"):
            file_path = os.path.join(directory, filename)
            configs.append(load_config_from_yaml(file_path))
    return configs

def main():
    config_directory = "configs"
    websites = load_all_configs(config_directory)

    for website_config in websites:
        scraper = WebsiteScraper(website_config)
        data = scraper.scrape()
        scraper.save_data(scraper.parse_data(data))

if __name__ == "__main__":
    main()