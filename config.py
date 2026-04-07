import os
from pathlib import Path


def load_config() -> dict:
    base_data_dir = Path("./data")

    return {
        "api_key": os.getenv("API_KEY", ""),
        "model_name": "models/gemini-2.5-pro",
        "temperature": 0.0,
        "max_output_tokens": 8192,
        "thinking_budget": 8192,
        "http_timeout": 300000,
        "rate_limit_delay": 4,
        "save_interval": 3,
        "max_retries": 3,
        "data_dir": str(base_data_dir),
        "image_dir": str(base_data_dir / "images"),
        "output_dir": "./output",
        "template_file": "submission_template.csv",
        "progress_file": "progress.json",
        "output_file": "submission.csv",
    }
