from config import get_env_var
from file_handler import FileHandler
from diff_tool import DiffTool

def main():
    data_directory = get_env_var('DATA_DIRECTORY', 'data')
    domain = 'bumble.com'

    file_handler = FileHandler()
    diff_tool = DiffTool(file_handler)

    # Compare all versions
    diffs = diff_tool.compare_all_versions(data_directory, domain)

    # Print or save the diffs
    for diff_item in diffs:
        print(f"Comparing {diff_item['from_version']} to {diff_item['to_version']}:")
        print(diff_tool.visualize_comparison(diff_item['diff']))
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()