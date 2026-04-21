import os  # Added missing import
import json
import uuid
import sys
from pathlib import Path
from urllib.parse import urlparse
from dotenv import set_key  
from .utils import atomic_write  # Adjusted to relative import if in same package

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"
file_name = BASE_DIR / "config.json"

env_path.touch(exist_ok=True)

def is_valid_url(url):
    try: 
        result = urlparse(url)
        return all([result.scheme, result.netloc]) 
    except ValueError: 
        return False

def main():
    # 1. Load existing data
    configs = []
    if file_name.exists():  # Use Path object method
        try:
            with open(file_name, 'r') as f:
                configs = json.load(f)
                if not isinstance(configs, list):
                    configs = [configs]
            print(f"--- Loaded {len(configs)} existing configurations ---")
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Warning: {file_name.name} is invalid or missing. Starting fresh.")

    # 2. Input count
    try:
        val = input("How many separate URL configurations would you like to add? ").strip()
        num_configs_to_add = int(val) if val else 0
    except ValueError:
        num_configs_to_add = 0

    keys = [
        "name", "url", "method", "enabled", "headers", "url_params", "json_payload",
        "timeout_ms", "max_retries", "expected_status", "fail_on_status",
        "max_expected_delay_ms"
    ]

    for n in range(num_configs_to_add):
        print(f"\n--- Setting up Configuration {n+1} of {num_configs_to_add} ---")
        data = {}

        for key in keys:
            if key == "name":
                inp = input(f"Enter name for this endpoint: ").strip()
                data[key] = inp if inp else str(uuid.uuid4())

            elif key == "url":
                while True:
                    url = input(f"Enter target endpoint URL: ").strip()
                    if is_valid_url(url):
                        data[key] = url
                        break
                    print("Invalid URL. Please try again.")

            elif key == "method":
                inp = input("Enter HTTP method [default: GET]: ").strip().upper()
                data[key] = inp if inp else "GET"

            elif key in ["headers", "url_params", "json_payload"]:
                item_data = {}
                display_name = key.replace("_", " ")
                inp = input(f"Enter number of {display_name} for this URL: ").strip()
                num_items = int(inp) if inp.isdigit() else 0
                
                for i in range(num_items):
                    item_key = input(f"  [{i+1}] {display_name.capitalize()} key: ")
                    item_val = input(f"  [{i+1}] {display_name.capitalize()} value: ")
                    
                    item_data[item_key] = "RUNTIME_VAL"
                    # dotenv set_key usually expects a string path
                    set_key(dotenv_path=str(env_path), key_to_set=item_key, value_to_set=item_val)
                    
                data[key] = item_data

            elif "ms" in key:
                default = 5000 if "timeout" in key else 1000
                inp = input(f"Enter {key} [default: {default}]: ").strip()
                try:
                    data[key] = int(inp) if inp else default
                except ValueError:
                    data[key] = default

            elif "status" in key:
                codes = []
                label = "success" if "expected" in key else "failure"
                inp = input(f"Enter number of {label} codes: ").strip()
                for i in range(int(inp) if inp.isdigit() else 0):
                    try:
                        codes.append(int(input(f"  Code {i+1}: ")))
                    except ValueError: pass
                data[key] = codes

            elif key == "enabled":
                inp = input(f"Set {key} to true? (y/n) [default: y]: ").strip().lower()
                data[key] = False if inp == 'n' else True

            elif key == "max_retries":
                inp = input("Enter max retries [default: 3]: ").strip()
                data[key] = int(inp) if inp.isdigit() else 3

        configs.append(data)

    # 3. Write using absolute path string
    if num_configs_to_add > 0:
        atomic_write(str(file_name), json.dumps(configs, indent=4))
        print(f"\nSuccessfully updated {file_name.name}!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
