import os
from dotenv import load_dotenv

def get_env_var(var_name: str, default_value: str = None) -> str:
    load_dotenv()
    return os.environ.get(var_name, default_value)