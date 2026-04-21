from pathlib import Path
from dotenv import get_key
from utils import log
import json
import requests
import sys
import os
import time

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
ENV_PATH = BASE_DIR / ".env"

config = {}

## TODO: Load endpoint configs from the config file.
try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as file: 
        config = json.load(file)
except FileNotFoundError:
    print(f"Error: Could not find config file at {CONFIG_PATH}")
    sys.exit(1)

## Keys list
keys = [
        "name", "url", "method", "enabled", "headers", "params",
        "timeout_ms", "max_retries", "expected_status", "fail_on_status",
        "max_expected_delay_ms"
    ]
		
def populate_env_key(entry, param_key):
    if param_key in ["headers", "params"]:
        
        # Loop directly through the dictionary keys
        for key in entry[param_key]:
            val = get_key(dotenv_path=ENV_PATH, key_to_get=key)  # Get the real value from the .env
            entry[param_key][key] = val

def make_http_request(entry):
    max_retries = entry["max_retries"]
    delay = entry["max_expected_delay_ms"]/1000
    last_response = None  # Initialize to avoid UnboundLocalError
    
    for attempt in range(1, max_retries + 1):
        try:
            log(f"Attempt {attempt} of {max_retries}", "info")
            
            request_kwargs = {}
            
            reqKeys_to_entryKeys_Map = {
                "method": "method", 
                "params": "url_params", 
                "headers": "headers",    
                "json": "json_payload", 
                "timeout": "timeout_ms"
            }
            
            for reqKey, entryKey in reqKeys_to_entryKeys_Map.items():
                if entryKey in entry:
                    key_val_pair = {reqKey: entry[entryKey]}
                    request_kwargs.update(key_val_pair)  
            

            response = requests.request(
                url=entry["url"],
                **request_kwargs
            )
            
            # Checks the HTTP status code
            response.raise_for_status() 
            return response
            
        except requests.exceptions.RequestException as e:
            last_response = e.response
            # Safely get status code (only if response exists)
            bad_code = last_response.status_code if last_response is not None else None
            log(f"Request Failed: {e}", "error")
            
            # Don't retry on 4xx errors (client-side issues)
            if bad_code and 400 <= bad_code < 500:
                log("Client-side error detected. Stopping retries.", "error")
                break
            
            # Don't retry on any response codes that match the fail_on_status codes
            fail_codes = entry.get("fail_on_status", [])
            if bad_code and fail_codes:
                if bad_code in fail_codes:
                    log(f"Fail on status code: {bad_code} returned by the request. Stopping retries.", "error")
                    break
                
            if attempt < max_retries:
                log(f"Waiting {delay} seconds before retrying...\n", "info")
                time.sleep(delay)
            else:
                log("Max retries reached.", "warning")
    
    # If we reached here, all retries failed or were broken out of
    if last_response is None:
        # Create a dummy response object so calling res.ok doesn't crash
        last_response = requests.Response()
        last_response.status_code = 500  # Default to 500 so .ok is False
        
    return last_response			
			
## Method to hit url according to given config and perform health check            
def hit_url(entry):
	# Before hitting a url, make sure the enabled flag is set to true
	if entry["enabled"] == True:
		name = entry["name"] 
		url = entry["url"]
		method = entry["method"]
		print("-"*60)
		log(f"The configuration for {name} has been loaded.", "info")
		print("-"*60)
		print(f"Endpoint: {url}")
		print(f"Method: {method}")
		log(f"Making http request to {url}...", "info")
		res = make_http_request(entry)
		default_success_codes = [200, 201, 204]
		if res.ok:
			status_code = res.status_code
			if entry["expected_status"]:
				if status_code in entry["expected_status"]:
					log(f"Expected status code: {status_code} returned by response. Success!", "info")
			elif status_code >= 200 and status_code < 300:
				log(f"Returned success code by request: {status_code}. Success!", "info")
	print("-"*60)
	print("\n")
		
            
def main():    	
## Iterate over the config json
	for entry in config:
		for key, value in entry.items():
			if (key == "headers" or key == "params") and len(entry[key]) != 0:
				populate_env_key(entry, key)
		hit_url(entry)
	return 0

if __name__ == "__main__":
    sys.exit(main())
			
				
			
		
		        


	 
