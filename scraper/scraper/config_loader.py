import yaml
from typing import List
from website_config import WebsiteConfig
from file_handler import FileHandler

def load_config_from_yaml(file_path: str, file_handler: FileHandler) -> WebsiteConfig:
    config_content = file_handler.read_file(file_path)
    config_data = yaml.safe_load(config_content)
    return WebsiteConfig(config_data)

def load_all_configs(directory: str, file_handler: FileHandler) -> List[WebsiteConfig]:
    configs = []
    for filename in file_handler.list_files(directory):
        if filename.endswith(".yaml"):
            file_path = f"{directory}/{filename}"
            configs.append(load_config_from_yaml(file_path, file_handler))
    return configs