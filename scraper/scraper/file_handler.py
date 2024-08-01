from google.cloud import storage
import os
from typing import List

class FileHandler:
    def __init__(self, is_cloud: bool = False, bucket_name: str = None):
        self.is_cloud = is_cloud
        self.bucket_name = bucket_name
        if is_cloud:
            self.client = storage.Client()
            self.bucket = self.client.get_bucket(bucket_name)

    def read_file(self, file_path: str) -> str:
        if self.is_cloud:
            blob = self.bucket.blob(file_path)
            return blob.download_as_text()
        else:
            with open(file_path, 'r') as file:
                return file.read()

    def write_file(self, file_path: str, content: str) -> None:
        if self.is_cloud:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(content)
        else:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(content)

    def list_files(self, directory: str) -> List[str]:
        if self.is_cloud:
            return [blob.name for blob in self.bucket.list_blobs(prefix=directory)]
        else:
            if not os.path.exists(directory):
                return []
            return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]