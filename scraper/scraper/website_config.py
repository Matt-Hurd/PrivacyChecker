from typing import Dict

class WebsiteConfig:
    def __init__(self, config_data: Dict):
        self.url = config_data['url']
        self.scraper_type = config_data['scraper_type']
        self.selectors = config_data['selectors']