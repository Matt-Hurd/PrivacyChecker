import os
import json
from config import get_env_var
from file_handler import FileHandler
from diff_tool import DiffTool

def main():
    data_directory = get_env_var('DATA_DIRECTORY', 'data')
    domain = get_env_var('DOMAIN', 'policies.google.com')
    output_directory = get_env_var('OUTPUT_DIRECTORY', 'diffs')

    file_handler = FileHandler()
    diff_tool = DiffTool(file_handler)

    # Compare all versions
    diffs = diff_tool.compare_all_versions(data_directory, domain)

    # Save the diffs
    os.makedirs(output_directory, exist_ok=True)
    diff_tool.save_diffs(diffs, output_directory)

    # Print summaries
    for diff in diffs:
        print(f"Diff between {diff['from_version']} and {diff['to_version']}:")
        print(json.dumps(diff['summary'], indent=2))
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()