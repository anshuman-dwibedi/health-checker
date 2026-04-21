import logging
import sys
import os
from pathlib import Path
from ulid import ULID
from .atomic_write import atomic_write 

LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
# Safely convert string to logging constant, defaulting to INFO if invalid
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# 2. Setup paths
logs_folder = Path(__file__).parent.parent / "logs"
log_file_name = f"log_{ULID()}.log"

os.makedirs(logs_folder, exist_ok=True)
log_file = logs_folder / log_file_name

with open('temp.txt', 'w') as f: f.write(str(log_file))

# 3. Using atomic_write to initialize the file
atomic_write(str(log_file), f"--- Log Start (Level: {LOG_LEVEL_STR})[Log File: {str(log_file)}] ---\n")

# 4. Configure Logging with dynamic level
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file), 
        logging.StreamHandler(sys.stdout)
    ]
)

# 5. Dynamic log function
def log(message, level="INFO"):
    """
    Logs a message at a specific level.
    Usage: log("Started", "DEBUG")
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.log(numeric_level, message)

