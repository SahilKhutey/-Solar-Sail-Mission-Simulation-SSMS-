import yaml
import json
import os


def load_config(config_path):
    """
    Load mission configuration from YAML or JSON file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    ext = os.path.splitext(config_path)[1].lower()

    with open(config_path, "r") as f:
        if ext == ".yaml" or ext == ".yml":
            return yaml.safe_load(f)
        elif ext == ".json":
            return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {ext}")


def validate_config(config):
    """
    Basic validation of config structure.
    """
    required_keys = ["mission", "spacecraft", "orbit"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config section: {key}")
    return True
