# Health Checker (Python)

![Python](https://img.shields.io/badge/language-python-blue)  
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos-lightgrey)  
![License](https://img.shields.io/badge/license-MIT-lightgrey)  
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)  
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange)

A **robust, automated API health monitoring tool** written in Python and Bash that:
* Executes **HTTP requests** (GET, POST, etc.) based on a structured JSON configuration.
* Supports **dynamic retries**, exponential backoffs, and specific failure status code aborts.
* Securely handles sensitive headers and parameters via **`.env` injection**.
* Provides a **Bash wrapper** for easy CI/CD, cron integration, and exit-code management.

---

## Why This Project?

Manual endpoint monitoring is prone to oversight, and hardcoding secrets in scripts is a security risk. This project provides a **modular and secure** framework to ensure your web services are responsive.

**Key benefits:**
* **Security First**: Sensitive API keys or tokens are stored in a `.env` file, not in the plain JSON config.
* **Interactive Setup**: Includes a `create_config.py` wizard to easily generate endpoints without manual JSON typing.
* **Intelligent Retries**: Aborts immediately on client-side errors (4xx) or specific fail codes, but retries transient server errors.
* **Automation Ready**: The `run.sh` script automatically searches for configurations and handles execution flow.

---

## Architecture

```text
User executes `./run.sh`
        ↓
Check for `config.json` (Triggers `create_config.py` if missing)
        ↓
`health-checker.py` loads config & `.env` secrets
        ↓
Inject `RUNTIME_VAL` into headers/params
        ↓
HTTP Request Cycle (Validates response against `expected_status`)
        ↓
Retries on failure (respecting `max_retries` & delays)
        ↓
Logs output and exits (0 for Success, >0 for Failure)
```

---

## Features

* ✅ **Dynamic Configuration**: Interactive CLI to build complex JSON payloads, headers, and params.
* ✅ **Environment Injection**: Replaces `RUNTIME_VAL` placeholders in the config with real secrets loaded from `.env`.
* ✅ **Advanced Retries**: Configurable `max_retries` with `max_expected_delay_ms`.
* ✅ **Smart Aborts**: Define `fail_on_status` to immediately halt retries if specific error codes (e.g., 401 Unauthorized) are returned.
* ✅ **URL Validation**: Built-in regex and `urlparse` validation during configuration setup.
* ✅ **Smart Exit Codes**: `run.sh` returns `0` on total success and captures Python exit codes on failure for pipeline integration.

---

## ⚙️ Configuration

### 1. Requirements
Install dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. The `.env` File
Used for storing sensitive data. Generated automatically by `create_config.py` when you specify headers or params.
```plaintext
X-API-Key=your_secret_key_here
```

### 3. `config.json` Structure
An array of endpoint objects. Example endpoint:
```json
{
    "name": "Complex Request (POST)",
    "url": "[https://postman-echo.com/post](https://postman-echo.com/post)",
    "method": "POST",
    "enabled": true,
    "headers": {
        "Content-Type": "application/json",
        "X-API-Key": "RUNTIME_VAL"
    },
    "timeout_ms": 5000,
    "max_retries": 3,
    "expected_status": [200],
    "fail_on_status": [400, 401, 403],
    "max_expected_delay_ms": 2000
}
```

---

## Usage

### Using the Bash Wrapper (Recommended)
The wrapper handles directory discovery, executes the Python script, and reports success/failure cleanly.
```bash
chmod +x run.sh
./run.sh
```

### Running Manually
If you want to run the python scripts directly:
```bash
# To generate a new configuration
python3 src/python/create_config.py

# To run the health checker
python3 src/python/health-checker.py
```

---

## Exit Codes

The `run.sh` script handles exit codes gracefully, making it ideal for Cron or CI/CD pipelines.

| Code | Meaning |
| :--- | :--- |
| `0` | **SUCCESS**: All health checks executed and returned expected statuses. |
| `>0` | **FAILURE**: Health check failed, config was missing/invalid, or Python crashed. |

---

## Project Structure

```plaintext
health-checker/
├── run.sh                  # Bash entry point and exit code handler
├── temp.txt                # Temporary log pointer for bash wrapper
└── src/
    └── python/
        ├── requirements.txt  # Python dependencies
        ├── health-checker.py # Core HTTP request and validation logic
        ├── create_config.py  # Interactive JSON config builder
        ├── config.json       # Endpoint definitions (Auto-generated)
        ├── .env              # Injected runtime secrets (Auto-generated)
        └── utils/
            ├── __init__.py
            ├── logger.py      # Standard & ULID file logging
            └── atomic_write.py # Safe file generation logic
```

---

## License

MIT License

