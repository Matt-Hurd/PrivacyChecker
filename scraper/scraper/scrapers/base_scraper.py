from abc import ABC, abstractmethod
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from file_handler import FileHandler
from logger import get_logger
import json
from datetime import datetime
import logging

class BaseScraper(ABC):
    def __init__(self, url: str, file_handler: FileHandler):
        self.url = url
        self.root_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f"{self.root_url}/robots.txt")
        self.robot_parser.read()
        self.logger = get_logger(__name__)
        self.file_handler = file_handler

    def can_fetch(self) -> bool:
        return self.robot_parser.can_fetch("*", self.url)

    @abstractmethod
    def scrape(self) -> str:
        pass

    def save_data(self, data: dict) -> None:
        if not data:
            return

        previous_data = self.load_previous_dump()
        
        if previous_data == data:
            self.logger.info(f"No changes detected for {self.url}. Skipping save.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/{urlparse(self.url).netloc}/{timestamp}.json"
        
        self.file_handler.write_file(filename, json.dumps(data, indent=2))
        
        self.logger.info(f"Changes detected. New data saved to {filename}")

    def load_previous_dump(self) -> dict:
        domain = urlparse(self.url).netloc
        data_dir = f"data/{domain}"
        files = [f for f in self.file_handler.list_files(data_dir) if f.endswith(".json")]

        if not files:
            return None

        latest_file = max(files, key=lambda f: datetime.strptime(f.split('.')[0], "%Y%m%d_%H%M%S"))
        content = self.file_handler.read_file(f"{data_dir}/{latest_file}")
        return json.loads(content)