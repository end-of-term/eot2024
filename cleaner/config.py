import yaml
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config/main.yml"

def load_config():
    """Load configuration from the YAML file."""
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)
