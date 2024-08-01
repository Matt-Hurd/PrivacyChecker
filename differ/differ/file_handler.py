import os
from typing import List

class FileHandler:
    def read_file(self, file_path: str) -> str:
        with open(file_path, 'r') as file:
            return file.read()

    def write_file(self, file_path: str, content: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.write(content)

    def list_files(self, directory: str) -> List[str]:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]