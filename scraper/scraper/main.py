from config import get_env_var
from file_handler import FileHandler
from config_loader import load_all_configs
from website_scraper import WebsiteScraper
from logger import get_logger

def main(event=None, context=None):
    logger = get_logger(__name__)
    
    is_cloud = get_env_var('IS_CLOUD', 'false').lower() == 'true'
    bucket_name = get_env_var('BUCKET_NAME')
    config_directory = get_env_var('CONFIG_DIRECTORY', 'configs')

    file_handler = FileHandler(is_cloud=is_cloud, bucket_name=bucket_name)

    configs = load_all_configs(config_directory, file_handler)

    for website_config in configs:
        scraper = WebsiteScraper(website_config, file_handler)
        try:
            scraper.scrape_and_save()
        except Exception as e:
            logger.error(f"Error scraping {website_config.url}: {e}")

# Cloud Functions entry point
def scrape_websites(event, context):
    main(event, context)

if __name__ == "__main__":
    main()