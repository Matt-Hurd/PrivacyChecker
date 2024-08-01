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
import os
from dotenv import load_dotenv
from google.cloud import storage

class FileHandler:
    def __init__(self, is_cloud=False, bucket_name=None):
        self.is_cloud = is_cloud
        self.bucket_name = bucket_name
        if is_cloud:
            self.client = storage.Client()
            self.bucket = self.client.get_bucket(bucket_name)

    def read_file(self, file_path):
        if self.is_cloud:
            blob = self.bucket.blob(file_path)
            return blob.download_as_text()
        else:
            with open(file_path, 'r') as file:
                return file.read()

    def write_file(self, file_path, content):
        if self.is_cloud:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(content)
        else:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(content)

    def list_files(self, directory):
        if self.is_cloud:
            return [blob.name for blob in self.bucket.list_blobs(prefix=directory)]
        else:
            return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def get_env_var(var_name, default_value=None):
    load_dotenv()
    return os.environ.get(var_name, default_value)

class BaseScraper(ABC):
    def __init__(self, url, file_handler):
        self.url = url
        self.root_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f"{self.root_url}/robots.txt")
        self.robot_parser.read()
        self.setup_logging()
        self.file_handler = file_handler

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

        previous_data = self.load_previous_dump()
        
        if previous_data == data:
            logging.info(f"No changes detected for {self.url}. Skipping save.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/scrape_{urlparse(self.url).netloc}_{timestamp}.json"
        
        self.file_handler.write_file(filename, json.dumps(data, indent=2))
        
        logging.info(f"Changes detected. New data saved to {filename}")

    def load_previous_dump(self):
        data_dir = "data"
        domain = urlparse(self.url).netloc
        files = [f for f in self.file_handler.list_files(data_dir) if f.startswith(f"scrape_{domain}_") and f.endswith(".json")]
        
        if not files:
            return None

        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(data_dir, f)))
        content = self.file_handler.read_file(os.path.join(data_dir, latest_file))
        return json.loads(content)

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
    def __init__(self, config, file_handler):
        super().__init__(config.url, file_handler)
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
    
    def scrape_and_save(self):
        content = self.scrape()
        if content:
            parsed_data = self.parse_data(content)
            self.save_data(parsed_data)

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

def main(event=None, context=None):
    is_cloud = get_env_var('IS_CLOUD', 'false').lower() == 'true'
    bucket_name = get_env_var('BUCKET_NAME')
    config_directory = get_env_var('CONFIG_DIRECTORY', 'configs')

    file_handler = FileHandler(is_cloud=is_cloud, bucket_name=bucket_name)

    configs = []
    for filename in file_handler.list_files(config_directory):
        if filename.endswith(".yaml"):
            file_path = os.path.join(config_directory, filename)
            config_content = file_handler.read_file(file_path)
            config_data = yaml.safe_load(config_content)
            configs.append(WebsiteConfig(config_data))

    for website_config in configs:
        scraper = WebsiteScraper(website_config, file_handler)
        scraper.scrape_and_save()

# Cloud Functions entry point
def scrape_websites(event, context):
    main(event, context)

if __name__ == "__main__":
    main()