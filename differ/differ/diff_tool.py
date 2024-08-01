import os
import json
from typing import List, Dict, Any
from file_handler import FileHandler
from diff_generator import generate_diff
from diff_visualizer import visualize_diff

class DiffTool:
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler

    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        content = self.file_handler.read_file(file_path)
        return json.loads(content)

    def compare_versions(self, file_path1: str, file_path2: str) -> Dict[str, Any]:
        data1 = self.load_json_file(file_path1)
        data2 = self.load_json_file(file_path2)
        return generate_diff(data1, data2)

    def visualize_comparison(self, diff: Dict[str, Any]) -> str:
        return visualize_diff(diff)

    def get_file_versions(self, directory: str, domain: str) -> List[str]:
        domain_dir = os.path.join(directory, domain)
        return sorted([
            f for f in self.file_handler.list_files(domain_dir)
            if f.endswith(".json")
        ])

    def compare_all_versions(self, directory: str, domain: str) -> List[Dict[str, Any]]:
        versions = self.get_file_versions(directory, domain)
        diffs = []
        for i in range(len(versions) - 1):
            file_path1 = os.path.join(directory, domain, versions[i])
            file_path2 = os.path.join(directory, domain, versions[i+1])
            diff = self.compare_versions(file_path1, file_path2)
            diffs.append({
                'from_version': versions[i],
                'to_version': versions[i+1],
                'diff': diff
            })
        return diffs